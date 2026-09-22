import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models import Process, User
from app.db.schemas import ProcessCreateRequest, ProcessListItem, ProcessResponse, ProcessUpdateRequest
from app.workflow.graph import process_graph_workflow

router = APIRouter(prefix="/processes", tags=["Processes"])


def _format_process_response(proc: Process) -> Dict[str, Any]:
    """Helper to deserialize stored JSON columns into the response dictionary."""
    return {
        "id": proc.id,
        "user_id": proc.user_id,
        "name": proc.name,
        "description": proc.description,
        "status": proc.status,
        "overall_confidence": proc.overall_confidence,
        "confidence_decision": proc.confidence_decision,
        "validation_status": proc.validation_status,
        "analysis": json.loads(proc.analysis_json) if proc.analysis_json else None,
        "model": json.loads(proc.model_json) if proc.model_json else None,
        "validation": json.loads(proc.validation_json) if proc.validation_json else None,
        "confidence": json.loads(proc.confidence_json) if proc.confidence_json else None,
        "intelligence": json.loads(proc.intelligence_json) if proc.intelligence_json else None,
        "created_at": proc.created_at,
        "updated_at": proc.updated_at
    }


@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
def create_process(
    req: ProcessCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new process owned exclusively by the authenticated user."""
    proc = Process(
        user_id=current_user.id,
        name=req.name.strip(),
        description=req.description.strip(),
        status="Draft"
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    return _format_process_response(proc)


@router.get("", response_model=List[ProcessListItem])
def list_processes(
    search: Optional[str] = Query(None, description="Search term in name or description"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Draft, Completed, Failed)"),
    validation_filter: Optional[str] = Query(None, alias="validation", description="Filter by validation (Validated, Needs review, Failed)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List processes belonging strictly to the authenticated user.
    Never exposes other users' processes.
    """
    query = db.query(Process).filter(Process.user_id == current_user.id)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(Process.name.ilike(s) | Process.description.ilike(s))

    if status_filter and status_filter.lower() != "all":
        query = query.filter(Process.status.ilike(status_filter))

    if validation_filter and validation_filter.lower() != "all":
        query = query.filter(Process.validation_status.ilike(validation_filter))

    processes = query.order_by(Process.created_at.desc()).all()

    results = []
    for p in processes:
        domain = "General"
        if p.analysis_json:
            try:
                ad = json.loads(p.analysis_json)
                domain = ad.get("domain", "General")
            except Exception:
                pass
        results.append({
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "domain": domain,
            "overall_confidence": p.overall_confidence,
            "confidence_decision": p.confidence_decision,
            "validation_status": p.validation_status or "Pending",
            "created_at": p.created_at,
            "updated_at": p.updated_at
        })
    return results


@router.get("/{process_id}", response_model=ProcessResponse)
def get_process(
    process_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve process details. Strict user data isolation:
    Returns 404 if process belongs to another user.
    """
    proc = db.query(Process).filter(
        Process.id == process_id,
        Process.user_id == current_user.id
    ).first()

    if not proc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found."
        )
    return _format_process_response(proc)


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete process owned by authenticated user.
    Strict isolation: Returns 404 if not found or belongs to another user.
    """
    proc = db.query(Process).filter(
        Process.id == process_id,
        Process.user_id == current_user.id
    ).first()

    if not proc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found."
        )

    db.delete(proc)
    db.commit()
    return None


@router.post("/{process_id}/analyze", response_model=ProcessResponse)
def analyze_process(
    process_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute real LangGraph multi-agent analysis workflow on the process.
    Persists analysis, model, validation, confidence, and intelligence JSON.
    """
    proc = db.query(Process).filter(
        Process.id == process_id,
        Process.user_id == current_user.id
    ).first()

    if not proc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process not found."
        )

    proc.status = "Analyzing"
    db.commit()

    try:
        # Run LangGraph multi-agent workflow
        initial_state = {
            "process_name": proc.name,
            "user_input": proc.description,
            "analysis_attempt": 1,
            "errors": []
        }
        final_state = process_graph_workflow.invoke(initial_state)

        analyst_out = final_state.get("analyst_result", {})
        model_out = final_state.get("model_result", {})
        val_out = final_state.get("validation_result", {})
        conf_out = final_state.get("confidence_result", {})
        intel_out = final_state.get("intelligence_result", {})

        proc.status = "Completed"
        proc.overall_confidence = conf_out.get("overall_score")
        proc.confidence_decision = conf_out.get("decision")
        proc.validation_status = val_out.get("display_status", "Validated")

        proc.analysis_json = json.dumps(analyst_out)
        proc.model_json = json.dumps(model_out)
        proc.validation_json = json.dumps(val_out)
        proc.confidence_json = json.dumps(conf_out)
        proc.intelligence_json = json.dumps(intel_out)

        db.commit()
        db.refresh(proc)
        return _format_process_response(proc)
    except Exception as e:
        proc.status = "Failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis pipeline execution failed: {str(e)}"
        )
