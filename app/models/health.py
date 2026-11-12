from typing import List, Dict, Any
from pydantic import BaseModel, Field


class HealthCategoryScore(BaseModel):
    category_name: str
    score: float = Field(ge=0.0, le=100.0)  # 0 to 100
    weight: float = Field(ge=0.0, le=1.0)
    status: str  # 'healthy', 'warning', 'critical'
    findings: List[str]
    improvement_advice: str


class ProjectHealthReport(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    health_grade: str  # 'A (Excellent)', 'B (Good)', 'C (At Risk)', 'D (Critical)'
    radar_metrics: Dict[str, float]  # {Planning, Timeline, Risk, Docs, Blockers}
    categories: List[HealthCategoryScore]
    executive_summary: str
    top_positives: List[str]
    top_vulnerabilities: List[str]
    recommended_immediate_actions: List[str]
