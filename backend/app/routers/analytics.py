"""
Analytics Router
Handles analytics and reporting endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import DashboardStats, ClientAnalytics, TeamAnalytics, Insights, ComplaintCluster
from app.dependencies import require_manager_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview", response_model=DashboardStats)
async def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get main dashboard statistics.
    Managers and admins only.
    """
    return AnalyticsService.get_dashboard_stats(db)


@router.get("/clients", response_model=ClientAnalytics)
async def get_client_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get analytics by client.
    Shows escalation counts, resolution times, and risk scores per client.
    """
    return AnalyticsService.get_client_analytics(db)


@router.get("/team", response_model=TeamAnalytics)
async def get_team_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get team performance analytics.
    Shows workload, resolution rates, and utilization per team member.
    """
    return AnalyticsService.get_team_analytics(db)


@router.get("/insights", response_model=Insights)
async def get_ai_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get AI-generated strategic insights.
    Analyzes trends, bottlenecks, and systematic issues.
    """
    return AnalyticsService.get_ai_insights(db)


@router.get("/clusters", response_model=List[ComplaintCluster])
async def get_complaint_clusters(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """
    Get AI-grouped complaint clusters.
    Managers and admins only.
    """
    return AnalyticsService.get_complaint_clusters(db)
