/**
 * Escalation Tracker - TypeScript Types
 * Matches backend Pydantic schemas with camelCase transformation
 */

// User types
export type UserRole = 'admin' | 'manager' | 'viewer';

export interface User {
    id: string;
    email: string;
    fullName: string;
    role: UserRole;
    expertiseTags: string[];
    maxConcurrentEscalations: number;
    currentEscalationCount: number;
    isActive: boolean;
    departmentId?: string | null;
    departmentName?: string | null;
    projectIds: string[];
    projectNames: string[];
    createdAt: string;
    updatedAt: string;
}

export interface UserCreate {
    email: string;
    password: string;
    full_name: string;
    role?: UserRole;
    expertise_tags?: string[];
    max_concurrent_escalations?: number;
    department_id?: string;
}

export interface LoginCredentials {
    username: string; // OAuth2 uses username field for email
    password: string;
}

export interface AuthToken {
    accessToken: string;
    tokenType: string;
}

// Client types
export interface Client {
    id: string;
    name: string;
    emailDomain: string | null;
    contactEmails: string[];
    industry: string | null;
    accountManagerId: string | null;
    riskScore: number;
    createdAt: string;
    updatedAt: string;
}

export interface ClientCreate {
    name: string;
    email_domain?: string;
    contact_emails?: string[];
    industry?: string;
    account_manager_id?: string;
}

// Escalation types
export type EscalationPriority = 'low' | 'medium' | 'high' | 'critical';
export type EscalationStatus = 'open' | 'in_progress' | 'resolved';

export interface Escalation {
    id: string;
    title: string;
    description: string;
    executiveSummary: string | null;
    clientId: string;
    clientName: string | null;
    priority: EscalationPriority;
    status: EscalationStatus;
    complaintType: string | null;
    sentimentScore: number;
    churnRisk: number;
    assignedTo: string | null;
    assigneeName: string | null;
    createdBy: string;
    creatorName: string | null;
    projectId: string | null;
    projectName: string | null;
    departmentName: string | null;
    aiRecommendedAssigneeId: string | null;
    aiAssignmentReason: string | null;
    aiAssignmentConfidence: number | null;
    aiSuggestions: AISuggestion[];
    dueDate: string;
    resolvedAt: string | null;
    daysUntilDue: number;
    isOverdue: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface AISuggestion {
    id: string;
    suggestionType: 'assignment' | 'resolution';
    content: any;
    confidenceScore: number | null;
    modelVersion: string | null;
    createdAt: string;
}

export interface EscalationCreate {
    title: string;
    description: string;
    executive_summary?: string;
    client_id: string;
    priority?: EscalationPriority;
    complaint_type?: string;
    sentiment_score?: number;
    churn_risk?: number;
}

export interface EscalationAssign {
    assignee_id: string;
    reason?: string;
}

export interface EscalationStatusUpdate {
    status: EscalationStatus;
    note?: string;
}

export interface EscalationListResponse {
    items: Escalation[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

// Timeline types
export type ActionType =
    | 'created'
    | 'assigned'
    | 'reassigned'
    | 'status_changed'
    | 'note_added'
    | 'priority_changed'
    | 'sla_warning'
    | 'sla_breach'
    | 'ai_recommendation';

export interface TimelineEvent {
    id: string;
    escalationId: string;
    userId: string | null;
    userName: string | null;
    actionType: ActionType;
    description: string;
    metadata: Record<string, unknown>;
    createdAt: string;
}

// Note types
export interface Note {
    id: string;
    escalationId: string;
    authorId: string;
    authorName: string | null;
    content: string;
    isInternal: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface NoteCreate {
    content: string;
}

// Analytics types
export interface PriorityBreakdown {
    low: number;
    medium: number;
    high: number;
    critical: number;
}

export interface StatusBreakdown {
    open: number;
    inProgress: number;
    resolved: number;
}

export interface TrendItem {
    date: string;
    count: number;
    avgResolutionTime: number;
    avgSentiment: number;
}

export interface ResolutionRate {
    resolved: number;
    unresolved: number;
    rate: number;
}

export interface DashboardStats {
    totalEscalations: number;
    openEscalations: number;
    resolvedEscalations: number;
    overdueEscalations: number;
    slaBreachCount: number;
    averageResolutionDays: number | null;
    priorityBreakdown: PriorityBreakdown;
    statusBreakdown: StatusBreakdown;
    dailyTrends: TrendItem[];
    resolutionRate: ResolutionRate;
    escalationsThisWeek: number;
    escalationsThisMonth: number;
}

export interface ClientAnalyticsItem {
    clientId: string;
    clientName: string;
    totalEscalations: number;
    openEscalations: number;
    resolvedEscalations: number;
    averageResolutionDays: number | null;
    riskScore: number;
    churnRisk: number;
}

export interface ClientAnalytics {
    clients: ClientAnalyticsItem[];
    totalClients: number;
}

export interface TeamMemberAnalytics {
    userId: string;
    userName: string;
    role: string;
    assignedEscalations: number;
    resolvedEscalations: number;
    averageResolutionDays: number | null;
    currentWorkload: number;
    maxWorkload: number;
    utilizationPercent: number;
}

export interface TeamAnalytics {
    members: TeamMemberAnalytics[];
    totalMembers: number;
    overloadedMembers: number;
}

export interface ComplaintTypeBreakdown {
    complaintType: string;
    count: number;
    percentage: number;
}

export interface InsightItem {
    category: string;
    title: string;
    description: string;
    severity: 'info' | 'warning' | 'critical';
    actionable: boolean;
}

export interface Insights {
    topComplaintTypes: ComplaintTypeBreakdown[];
    insights: InsightItem[];
    generatedAt: string;
}

export interface ClusterItem {
    id: string;
    title: string;
    clientName: string | null;
    createdAt: string;
}

export interface ComplaintCluster {
    id: string;
    name: string;
    description: string;
    severity: 'info' | 'warning' | 'critical';
    count: number;
    items: ClusterItem[];
    isRecurrence: boolean;
}

// API Error
export interface ApiError {
    detail: string;
}

// Filters
export interface EscalationFilters {
    status?: EscalationStatus;
    priority?: EscalationPriority;
    clientId?: string;
    assignedTo?: string;
    page?: number;
    pageSize?: number;
}
