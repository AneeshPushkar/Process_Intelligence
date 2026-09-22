import json
from datetime import datetime
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.db.models import Process, User
from app.db.schemas import DashboardStatsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compute real aggregated dashboard statistics strictly for the authenticated user.
    """
    user_processes = db.query(Process).filter(
        Process.user_id == current_user.id
    ).order_by(Process.created_at.desc()).all()

    total_processes = len(user_processes)
    completed = [p for p in user_processes if p.overall_confidence is not None]

    if completed:
        avg_confidence = round(sum(p.overall_confidence for p in completed) / len(completed), 1)
    else:
        avg_confidence = 0.0

    validated_count = sum(
        1 for p in user_processes
        if p.validation_status and p.validation_status.lower() in ["validated", "pass"]
    )

    total_insights = 0
    issue_counts = {"Bottlenecks": 0, "Risks": 0, "Redundant": 0, "Automation": 0}

    for p in user_processes:
        if p.intelligence_json:
            try:
                intel = json.loads(p.intelligence_json)
                b_cnt = len(intel.get("bottlenecks", []))
                r_cnt = len(intel.get("risks", []))
                d_cnt = len(intel.get("redundant_steps", []))
                a_cnt = len(intel.get("automation_opportunities", []))
                rec_cnt = len(intel.get("recommendations", []))

                total_insights += (b_cnt + r_cnt + d_cnt + a_cnt + rec_cnt)
                issue_counts["Bottlenecks"] += b_cnt
                issue_counts["Risks"] += r_cnt
                issue_counts["Redundant"] += d_cnt
                issue_counts["Automation"] += a_cnt
            except Exception:
                pass

    # Confidence Trend: sequence of analyzed processes (or empty list if none)
    trend = []
    # Reverse to chronological order for trend display
    for p in reversed(completed[-6:]):
        month_label = p.created_at.strftime("%b %d") if p.created_at else "Recent"
        trend.append({
            "month": month_label,
            "confidence": round(p.overall_confidence, 1),
            "name": p.name[:15]
        })

    # Recent processes (up to 4)
    recent = []
    for p in user_processes[:4]:
        domain = "General"
        if p.analysis_json:
            try:
                ad = json.loads(p.analysis_json)
                domain = ad.get("domain", "General")
            except Exception:
                pass
        recent.append({
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

    issue_dist = [
        {"name": "Bottlenecks", "value": issue_counts["Bottlenecks"], "fill": "#fbbf24"},
        {"name": "Risks", "value": issue_counts["Risks"], "fill": "#f87171"},
        {"name": "Redundant", "value": issue_counts["Redundant"], "fill": "#a1a1aa"},
        {"name": "Automation", "value": issue_counts["Automation"], "fill": "#14b8a6"},
    ]

    return {
        "total_processes": total_processes,
        "average_confidence": avg_confidence,
        "validated_count": validated_count,
        "insights_generated_count": total_insights,
        "confidence_trend": trend,
        "recent_processes": recent,
        "issue_distribution": issue_dist
    }
