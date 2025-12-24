/**
 * Date and number formatting utilities
 */
import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format ISO date string to readable format
 */
export const formatDate = (dateString: string): string => {
    try {
        return format(parseISO(dateString), 'MMM d, yyyy');
    } catch {
        return dateString;
    }
};

/**
 * Format ISO date string to readable datetime
 */
export const formatDateTime = (dateString: string): string => {
    try {
        return format(parseISO(dateString), 'MMM d, yyyy h:mm a');
    } catch {
        return dateString;
    }
};

/**
 * Format to relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (dateString: string): string => {
    try {
        return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
    } catch {
        return dateString;
    }
};

/**
 * Format number with commas
 */
export const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(num);
};

/**
 * Format percentage
 */
export const formatPercent = (num: number, decimals = 0): string => {
    return `${num.toFixed(decimals)}%`;
};

/**
 * Get priority color class
 */
export const getPriorityClass = (priority: string): string => {
    const classes: Record<string, string> = {
        low: 'badge-low',
        medium: 'badge-medium',
        high: 'badge-high',
        critical: 'badge-critical',
    };
    return classes[priority] || 'badge-low';
};

/**
 * Get status color class
 */
export const getStatusClass = (status: string): string => {
    const classes: Record<string, string> = {
        open: 'badge-open',
        in_progress: 'badge-in-progress',
        resolved: 'badge-resolved',
    };
    return classes[status] || 'badge-open';
};

/**
 * Format status for display
 */
export const formatStatus = (status: string): string => {
    const labels: Record<string, string> = {
        open: 'Open',
        in_progress: 'In Progress',
        resolved: 'Resolved',
    };
    return labels[status] || status;
};

/**
 * Format priority for display
 */
export const formatPriority = (priority: string): string => {
    return priority.charAt(0).toUpperCase() + priority.slice(1);
};
