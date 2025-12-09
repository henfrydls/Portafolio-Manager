from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('portfolio')

def cleanup_old_page_visits(days_to_keep=180):
    """
    Clean up old page visit data to optimize database performance

    Removes PageVisit records older than the specified number of days.
    This function is called automatically from the analytics view and
    can also be run manually via management command.

    Args:
        days_to_keep (int): Number of days to keep (default: 180 days / 6 months)

    Returns:
        int: Number of records deleted
    """
    from ..models import PageVisit
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        # Count records to be deleted
        old_visits = PageVisit.objects.filter(timestamp__lt=cutoff_date)
        count_to_delete = old_visits.count()

        if count_to_delete == 0:
            logger.info(f'No page visit records older than {days_to_keep} days found for cleanup')
            return 0

        # Delete old records
        deleted_count, _ = old_visits.delete()

        logger.info(f'Automatically cleaned up {deleted_count} page visit records older than {cutoff_date.date()}')

        return deleted_count

    except Exception as e:
        logger.error(f'Error during automatic page visit cleanup: {e}')
        return 0


def get_analytics_summary():
    """
    Get a quick summary of analytics data for dashboard display

    Returns:
        dict: Summary analytics data
    """
    from ..models import PageVisit, BlogPost, Contact, Project
    
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    return {
        'total_visits': PageVisit.objects.count(),
        'today_visits': PageVisit.objects.filter(timestamp__date=today).count(),
        'week_visits': PageVisit.objects.filter(timestamp__gte=week_ago).count(),
        'month_visits': PageVisit.objects.filter(timestamp__gte=month_ago).count(),
        'total_posts': BlogPost.objects.count(),
        'published_posts': BlogPost.objects.filter(status='published').count(),
        'total_projects': Project.objects.count(),
        'public_projects': Project.objects.filter(visibility='public').count(),
        'total_messages': Contact.objects.count(),
        'unread_messages': Contact.objects.filter(read=False).count(),
    }
