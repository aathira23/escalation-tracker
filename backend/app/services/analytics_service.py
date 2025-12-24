"""
Analytics Service
Business logic for analytics and reporting.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case

from app.models.escalation import Escalation, EscalationStatus, EscalationPriority
from app.models.client import Client
from app.models.user import User, UserRole
from app.schemas.analytics import (
    DashboardStats, PriorityBreakdown, StatusBreakdown, TrendItem, ResolutionRate,
    ClientAnalytics, ClientAnalyticsItem,
    TeamAnalytics, TeamMemberAnalytics
)


class AnalyticsService:
    """Service for analytics operations."""
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> DashboardStats:
        """Get main dashboard statistics."""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Total counts
        total = db.query(Escalation).count()
        open_count = db.query(Escalation).filter(Escalation.status == EscalationStatus.OPEN).count()
        in_progress = db.query(Escalation).filter(Escalation.status == EscalationStatus.IN_PROGRESS).count()
        resolved = db.query(Escalation).filter(Escalation.status == EscalationStatus.RESOLVED).count()
        
        # Overdue count (not resolved and past due date)
        overdue = db.query(Escalation).filter(
            and_(
                Escalation.status != EscalationStatus.RESOLVED,
                Escalation.due_date < now
            )
        ).count()
        
        # SLA breaches (resolved after due date)
        sla_breaches = db.query(Escalation).filter(
            and_(
                Escalation.status == EscalationStatus.RESOLVED,
                Escalation.resolved_at > Escalation.due_date
            )
        ).count()
        
        # Average resolution time
        avg_resolution = db.query(
            func.avg(
                func.extract('epoch', Escalation.resolved_at - Escalation.created_at) / 86400
            )
        ).filter(Escalation.resolved_at.isnot(None)).scalar()
        
        # Priority breakdown
        priority_counts = db.query(
            Escalation.priority,
            func.count(Escalation.id)
        ).group_by(Escalation.priority).all()
        
        priority_dict = {p.value: 0 for p in EscalationPriority}
        for priority, count in priority_counts:
            priority_dict[priority.value] = count
        
        # Time-based counts
        this_week = db.query(Escalation).filter(Escalation.created_at >= week_ago).count()
        this_month = db.query(Escalation).filter(Escalation.created_at >= month_ago).count()
        
        # Daily trends (last 14 days)
        daily_trends = AnalyticsService._get_daily_trends(db, 14)
        
        # Resolution rate
        resolution_rate = ResolutionRate(
            resolved=resolved,
            unresolved=total - resolved,
            rate=round((resolved / total * 100), 1) if total > 0 else 0
        )
        
        return DashboardStats(
            totalEscalations=total,
            openEscalations=open_count,
            resolvedEscalations=resolved,
            overdueEscalations=overdue,
            slaBreachCount=sla_breaches,
            averageResolutionDays=round(avg_resolution, 1) if avg_resolution else None,
            priorityBreakdown=PriorityBreakdown(
                low=priority_dict.get("low", 0),
                medium=priority_dict.get("medium", 0),
                high=priority_dict.get("high", 0),
                critical=priority_dict.get("critical", 0)
            ),
            statusBreakdown=StatusBreakdown(
                open=open_count,
                inProgress=in_progress,
                resolved=resolved
            ),
            dailyTrends=daily_trends,
            resolutionRate=resolution_rate,
            escalationsThisWeek=this_week,
            escalationsThisMonth=this_month
        )

    @staticmethod
    def _get_daily_trends(db: Session, days: int) -> List[TrendItem]:
        """Calculate daily escalation trends."""
        now = datetime.utcnow()
        start_date = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        trends = []
        for i in range(days + 1):
            current_day = start_date + timedelta(days=i)
            next_day = current_day + timedelta(days=1)
            
            # Count escalations created today
            count = db.query(Escalation).filter(
                and_(
                    Escalation.created_at >= current_day,
                    Escalation.created_at < next_day
                )
            ).count()
            
            # Avg resolution time for those resolved today
            avg_res = db.query(
                func.avg(
                    func.extract('epoch', Escalation.resolved_at - Escalation.created_at) / 3600 # in hours
                )
            ).filter(
                and_(
                    Escalation.resolved_at >= current_day,
                    Escalation.resolved_at < next_day
                )
            ).scalar()
            
            # Avg sentiment for those created today
            avg_sentiment = db.query(
                func.avg(Escalation.sentiment_score)
            ).filter(
                and_(
                    Escalation.created_at >= current_day,
                    Escalation.created_at < next_day
                )
            ).scalar()
            
            trends.append(TrendItem(
                date=current_day.strftime("%b %d"),
                count=count,
                avgResolutionTime=round(avg_res, 1) if avg_res else 0,
                avgSentiment=round(avg_sentiment, 2) if avg_sentiment else 0
            ))
            
        return trends
    
    @staticmethod
    def get_client_analytics(db: Session) -> ClientAnalytics:
        """Get analytics by client."""
        clients = db.query(Client).all()
        items = []
        
        for client in clients:
            escalations = db.query(Escalation).filter(Escalation.client_id == client.id).all()
            
            total_count = len(escalations)
            open_count = sum(1 for e in escalations if e.status == EscalationStatus.OPEN)
            resolved_count = sum(1 for e in escalations if e.status == EscalationStatus.RESOLVED)
            
            # Average resolution time
            resolved_escalations = [e for e in escalations if e.resolved_at]
            avg_days = None
            if resolved_escalations:
                total_days = sum(
                    (e.resolved_at - e.created_at).days for e in resolved_escalations
                )
                avg_days = total_days / len(resolved_escalations)
            
            # Average churn risk
            avg_churn = sum(e.churn_risk for e in escalations) / total_count if total_count > 0 else 0
            
            items.append(ClientAnalyticsItem(
                clientId=client.id,
                clientName=client.name,
                totalEscalations=total_count,
                openEscalations=open_count,
                resolvedEscalations=resolved_count,
                averageResolutionDays=round(avg_days, 1) if avg_days else None,
                riskScore=client.risk_score,
                churnRisk=round(avg_churn, 2)
            ))
        
        # Sort by total escalations descending
        items.sort(key=lambda x: x.totalEscalations, reverse=True)
        
        return ClientAnalytics(
            clients=items,
            totalClients=len(clients)
        )
    
    @staticmethod
    def get_team_analytics(db: Session) -> TeamAnalytics:
        """Get team performance analytics."""
        # Get all active users who can be assigned escalations (viewers)
        users = db.query(User).filter(User.is_active == True).all()
        members = []
        overloaded = 0
        
        for user in users:
            # Get assigned (non-resolved) escalations
            assigned = db.query(Escalation).filter(
                and_(
                    Escalation.assigned_to == user.id,
                    Escalation.status != EscalationStatus.RESOLVED
                )
            ).count()
            
            # Get resolved escalations
            resolved = db.query(Escalation).filter(
                and_(
                    Escalation.assigned_to == user.id,
                    Escalation.status == EscalationStatus.RESOLVED
                )
            ).all()
            
            # Average resolution time
            avg_days = None
            if resolved:
                total_days = sum((e.resolved_at - e.created_at).days for e in resolved)
                avg_days = total_days / len(resolved)
            
            utilization = (assigned / user.max_concurrent_escalations * 100) if user.max_concurrent_escalations > 0 else 0
            
            if assigned >= user.max_concurrent_escalations:
                overloaded += 1
            
            members.append(TeamMemberAnalytics(
                userId=user.id,
                userName=user.full_name,
                role=user.role.value,
                assignedEscalations=assigned,
                resolvedEscalations=len(resolved),
                averageResolutionDays=round(avg_days, 1) if avg_days else None,
                currentWorkload=assigned,
                maxWorkload=user.max_concurrent_escalations,
                utilizationPercent=round(min(utilization, 100), 1)
            ))
        
        # Sort by current workload descending
        members.sort(key=lambda x: x.currentWorkload, reverse=True)
        
        return TeamAnalytics(
            members=members,
            totalMembers=len(members),
            overloadedMembers=overloaded
        )
