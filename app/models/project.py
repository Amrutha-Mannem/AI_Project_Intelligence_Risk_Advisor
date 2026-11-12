from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScopeItem(BaseModel):
    id: str
    title: str
    description: str
    category: str  # 'core_feature', 'infrastructure', 'integration', 'security', 'out_of_scope'
    in_scope: bool = True
    confidence: float = 0.9
    source_reference: Optional[str] = None


class Deliverable(BaseModel):
    id: str
    title: str
    description: str
    target_date: Optional[str] = None
    milestone: Optional[str] = None
    status: str = "pending"  # 'pending', 'in_progress', 'completed', 'at_risk'
    deliverable_type: str = "feature"  # 'documentation', 'code', 'deployment', 'test'
    source_reference: Optional[str] = None


class ScopeReport(BaseModel):
    project_title: str
    project_objective: str
    target_audience: str
    in_scope_items: List[ScopeItem]
    out_of_scope_items: List[ScopeItem]
    key_deliverables: List[Deliverable]
    summary: str


class RiskItem(BaseModel):
    id: str
    risk_title: str
    description: str
    category: str  # 'technical', 'schedule', 'resource', 'scope_creep', 'dependency', 'external'
    probability: str  # 'High', 'Medium', 'Low'
    impact: str  # 'High', 'Medium', 'Low'
    severity_score: int = Field(ge=1, le=25)  # 1 to 25 matrix score
    early_warning_signs: List[str] = Field(default_factory=list)
    mitigation_strategy: str
    contingency_plan: Optional[str] = None
    status: str = "identified"  # 'identified', 'mitigating', 'resolved'
    source_reference: Optional[str] = None


class DeliveryForecast(BaseModel):
    forecast_status: str  # 'On Track', 'At Risk', 'Critical Delay'
    predicted_delay_days: int = 0
    confidence_level: float = 0.85
    critical_path_factors: List[str]
    forecast_narrative: str
    recommendations: List[str]


class BlockerItem(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    assigned_owner: Optional[str] = "Unassigned"
    impacted_deliverable: Optional[str] = None
    suggested_resolution: str
    status: str = "open"  # 'open', 'investigating', 'resolved'
    source_reference: Optional[str] = None


class ActionItem(BaseModel):
    id: str
    task_description: str
    assignee: str = "Team"
    priority: str = "Medium"  # 'Urgent', 'High', 'Medium', 'Low'
    due_date: Optional[str] = None
    related_risk_or_blocker: Optional[str] = None
    status: str = "todo"  # 'todo', 'in_progress', 'done'
    source_reference: Optional[str] = None


class UserStory(BaseModel):
    id: str
    title: str
    as_a: str
    i_want_to: str
    so_that: str
    acceptance_criteria: List[str]
    priority: str = "Medium"  # 'Must Have', 'Should Have', 'Could Have', 'Won't Have'
    estimated_story_points: int = 3
    epic_tag: Optional[str] = None


class DocumentationBundle(BaseModel):
    user_stories: List[UserStory]
    risk_register: List[RiskItem]
    action_items: List[ActionItem]
    missing_documentation_gaps: List[str]
