"""
Utility functions for portfolio app.
"""


def get_education_summary(profile):
    """
    Get a summary of education organized by type for quick display

    Args:
        profile: Profile model instance

    Returns:
        dict: Education summary with counts and latest entries
    """
    education_qs = profile.education_set.all()

    return {
        'formal_count': education_qs.filter(education_type='formal').count(),
        'certification_count': education_qs.filter(education_type='certification').count(),
        'course_count': education_qs.filter(education_type='online_course').count(),
        'bootcamp_count': education_qs.filter(education_type__in=['bootcamp', 'workshop']).count(),
        'latest_formal': education_qs.filter(education_type='formal').first(),
        'latest_certification': education_qs.filter(education_type='certification').first(),
        'total_count': education_qs.count(),
    }


def get_skills_summary(profile):
    """
    Get a summary of skills organized by proficiency and category

    Args:
        profile: Profile model instance

    Returns:
        dict: Skills summary with counts and top skills
    """
    skills_qs = profile.skill_set.all()

    return {
        'total_count': skills_qs.count(),
        'expert_count': skills_qs.filter(proficiency=4).count(),
        'advanced_count': skills_qs.filter(proficiency=3).count(),
        'categories': skills_qs.values_list('category', flat=True).distinct(),
        'top_skills': skills_qs.filter(proficiency__gte=3).order_by('-proficiency', '-years_experience')[:8],
    }


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
    from django.utils import timezone
    from datetime import timedelta
    from .models import PageVisit
    import logging

    logger = logging.getLogger('portfolio')

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
    from django.utils import timezone
    from django.db.models import Count
    from datetime import timedelta
    from .models import PageVisit, BlogPost, Contact, Project

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