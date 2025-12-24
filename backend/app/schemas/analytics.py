"""
Analytics Schemas
Pydantic models for analytics API responses.
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from typing import List


class TrendItem(BaseModel):
    """A single data point for time-series charts."""
    date: str
    count: int
    avgResolutionTime: Optional[float] = None
    avgSentiment: Optional[float] = None


class ResolutionRate(BaseModel):
    """Resolution rate statistics."""
    resolved: int
    unresolved: int
    rate: float  # Percentage


class PriorityBreakdown(BaseModel):
    """Breakdown of escalations by priority."""
    low: int
    medium: int
    high: int
    critical: int


class StatusBreakdown(BaseModel):
    """Breakdown of escalations by status."""
    open: int
    inProgress: int
    resolved: int


class DashboardStats(BaseModel):
    """Schema for main dashboard statistics."""
    # Counts
    totalEscalations: int
    openEscalations: int
    resolvedEscalations: int
    overdueEscalations: int
    
    # SLA metrics
    slaBreachCount: int
    averageResolutionDays: Optional[float]
    
    # Breakdowns
    priorityBreakdown: PriorityBreakdown
    statusBreakdown: StatusBreakdown
    
    # Trends
    dailyTrends: List[TrendItem]
    resolutionRate: ResolutionRate
    
    # Trends (optional)
    escalationsThisWeek: int
    escalationsThisMonth: int


class ClientAnalyticsItem(BaseModel):
    """Analytics for a single client."""
    clientId: UUID
    clientName: str
    totalEscalations: int
    openEscalations: int
    resolvedEscalations: int
    averageResolutionDays: Optional[float]
    riskScore: float
    churnRisk: float


class ClientAnalytics(BaseModel):
    """Schema for client analytics response."""
    clients: list[ClientAnalyticsItem]
    totalClients: int


class TeamMemberAnalytics(BaseModel):
    """Analytics for a single team member."""
    userId: UUID
    userName: str
    role: str
    assignedEscalations: int
    resolvedEscalations: int
    averageResolutionDays: Optional[float]
    currentWorkload: int
    maxWorkload: int
    utilizationPercent: float


class TeamAnalytics(BaseModel):
    """Schema for team performance analytics."""
    members: list[TeamMemberAnalytics]
    totalMembers: int
    overloadedMembers: int  # Members at max capacity


class ComplaintTypeBreakdown(BaseModel):
    """Breakdown of escalations by complaint type."""
    complaintType: str
    count: int
    percentage: float


class InsightItem(BaseModel):
    """A single AI-generated insight."""
    category: str
    title: str
    description: str
    severity: str  # info, warning, critical
    actionable: bool


class Insights(BaseModel):
    """Schema for AI-generated insights."""
    topComplaintTypes: list[ComplaintTypeBreakdown]
    insights: list[InsightItem]
    generatedAt: date
