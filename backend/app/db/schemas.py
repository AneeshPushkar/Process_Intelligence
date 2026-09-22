from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Auth Schemas
class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    organization: Optional[str] = Field(None, max_length=255)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    organization: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Process Schemas
class ProcessCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)


class ProcessUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=5)


class ProcessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    description: str
    status: str
    overall_confidence: Optional[float] = None
    confidence_decision: Optional[str] = None
    validation_status: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    model: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    confidence: Optional[Dict[str, Any]] = None
    intelligence: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ProcessListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    domain: Optional[str] = "General"
    overall_confidence: Optional[float] = None
    confidence_decision: Optional[str] = None
    validation_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Detailed Agent Schemas
class AnalystOutput(BaseModel):
    title: str
    summary: str
    domain: str
    actors: List[str]
    activities: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]
    start_event: Dict[str, Any]
    end_event: Dict[str, Any]
    assumptions: List[str]
    ambiguities: List[str]
    analyst_confidence: float


class FlowNode(BaseModel):
    id: str
    type: str  # event, task, gateway
    data: Dict[str, Any]
    position: Dict[str, float]


class FlowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    condition: Optional[str] = None


class ProcessModelOutput(BaseModel):
    nodes: List[FlowNode]
    edges: List[FlowEdge]
    statistics: Dict[str, int]


class ValidationCheck(BaseModel):
    id: str
    label: str
    result: str  # Pass, Review, Fail
    detail: str


class ValidationIssue(BaseModel):
    id: str
    severity: str  # ERROR, WARNING, INFO
    message: str
    node_id: Optional[str] = None


class ValidationOutput(BaseModel):
    status: str  # PASS, NEEDS_REVIEW, FAIL
    issues: List[ValidationIssue]
    warnings: List[str]
    checks: List[ValidationCheck]
    validation_score: float


class ConfidenceOutput(BaseModel):
    analyst_score: float
    model_completeness_score: float
    validation_score: float
    sequence_consistency_score: float
    gateway_consistency_score: float
    overall_score: float
    decision: str  # HIGH, REVIEW, LOW
    explanation: str
    reasons: List[str]


class InsightItem(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # High, Medium, Low
    priority: str  # P1, P2, P3
    impact: str    # High, Medium, Low
    recommendation: str
    related_node_ids: List[str] = []


class IntelligenceOutput(BaseModel):
    bottlenecks: List[InsightItem]
    risks: List[InsightItem]
    redundant_steps: List[InsightItem]
    automation_opportunities: List[InsightItem]
    recommendations: List[InsightItem]
    efficiency_metrics: Optional[List[Dict[str, Any]]] = None
    issue_distribution: Optional[List[Dict[str, Any]]] = None


class DashboardStatsResponse(BaseModel):
    total_processes: int
    average_confidence: float
    validated_count: int
    insights_generated_count: int
    confidence_trend: List[Dict[str, Any]]
    recent_processes: List[ProcessListItem]
    issue_distribution: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    database: str
    llm_provider: str
    llm_model: str
    analysis_mode: str
