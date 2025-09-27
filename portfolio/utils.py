"""
Utility functions for portfolio app.
"""
from django.template.loader import render_to_string
from django.http import HttpResponse
import io


def generate_resume_pdf(profile):
    """
    Generate PDF summary of resume (1-2 pages)
    
    Filters the most relevant experiences and skills to create a concise
    resume suitable for recruiters. Includes GitHub and LinkedIn links.
    
    Args:
        profile: Profile model instance
        
    Returns:
        bytes: PDF content as bytes or None if WeasyPrint is not available
    """
    # Try to import WeasyPrint, but make it optional
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        # Return None if WeasyPrint is not available
        # The view should handle this gracefully
        return None
    
    # Filter only the most relevant experiences (last 4 positions)
    key_experiences = profile.experience_set.all().order_by('-start_date')[:4]
    
    # Filter top skills (advanced and expert level only)
    top_skills = profile.skill_set.filter(proficiency__gte=3).order_by('category', '-proficiency')
    
    # Get most recent education entries (max 3)
    recent_education = profile.education_set.all().order_by('-end_date', '-start_date')[:3]
    
    # Prepare context for PDF template
    context = {
        'profile': profile,
        'experiences': key_experiences,
        'education': recent_education,
        'skills': top_skills,
        'github_url': profile.github_url,
        'linkedin_url': profile.linkedin_url,
        'is_pdf': True,  # Flag to indicate this is for PDF rendering
    }
    
    # Render HTML template
    html_content = render_to_string('portfolio/resume_pdf_summary.html', context)
    
    try:
        # Create PDF with WeasyPrint
        font_config = FontConfiguration()
        html = HTML(string=html_content)
        
        # Custom CSS for PDF styling
        css = CSS(string='''
            @page {
                size: A4;
                margin: 1cm;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                font-size: 11pt;
                line-height: 1.4;
                color: #333;
            }
            
            .header {
                text-align: center;
                margin-bottom: 20px;
                border-bottom: 2px solid #2c3e50;
                padding-bottom: 15px;
            }
            
            .header h1 {
                margin: 0;
                font-size: 24pt;
                color: #2c3e50;
            }
            
            .header .title {
                font-size: 14pt;
                color: #7f8c8d;
                margin: 5px 0;
            }
            
            .contact-info {
                font-size: 10pt;
                margin-top: 10px;
            }
            
            .contact-info a {
                color: #3498db;
                text-decoration: none;
            }
            
            .section {
                margin-bottom: 20px;
            }
            
            .section h2 {
                font-size: 14pt;
                color: #2c3e50;
                border-bottom: 1px solid #bdc3c7;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }
            
            .experience-item, .education-item {
                margin-bottom: 15px;
                page-break-inside: avoid;
            }
            
            .experience-header, .education-header {
                font-weight: bold;
                color: #2c3e50;
            }
            
            .company, .institution {
                color: #3498db;
            }
            
            .date-range {
                font-style: italic;
                color: #7f8c8d;
                font-size: 10pt;
            }
            
            .skills-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }
            
            .skill-category {
                margin-bottom: 10px;
            }
            
            .skill-category h3 {
                font-size: 12pt;
                color: #2c3e50;
                margin-bottom: 5px;
            }
            
            .skill-list {
                font-size: 10pt;
                line-height: 1.3;
            }
            
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 9pt;
                color: #7f8c8d;
            }
        ''', font_config=font_config)
        
        # Generate PDF
        pdf_bytes = html.write_pdf(stylesheets=[css], font_config=font_config)
        
        return pdf_bytes
        
    except Exception as e:
        # Log the error and return None
        import logging
        logger = logging.getLogger('portfolio')
        logger.error(f'Error generating PDF: {e}')
        return None


def get_resume_web_data(profile):
    """
    Get complete data for web version of resume
    
    Organizes all education by types for better presentation on the web.
    Includes all experiences, skills, and education entries.
    
    Args:
        profile: Profile model instance
        
    Returns:
        dict: Complete resume data organized for web display
    """
    # Get all experiences ordered by start date
    experiences = profile.experience_set.all().order_by('-start_date')
    
    # Get education organized by type
    education_qs = profile.education_set.all()
    
    # Organize education by type for better web presentation
    formal_education = education_qs.filter(education_type='formal').order_by('-start_date')
    certifications = education_qs.filter(education_type='certification').order_by('-end_date', '-start_date')
    online_courses = education_qs.filter(education_type='online_course').order_by('-end_date', '-start_date')
    bootcamps = education_qs.filter(education_type__in=['bootcamp', 'workshop']).order_by('-end_date', '-start_date')
    
    # Get all skills organized by category
    skills = profile.skill_set.all().order_by('category', '-proficiency', 'name')
    
    # Group skills by category for better display
    skills_by_category = {}
    for skill in skills:
        category = skill.category
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill)
    
    return {
        'profile': profile,
        'experiences': experiences,
        'formal_education': formal_education,
        'certifications': certifications,
        'online_courses': online_courses,
        'bootcamps': bootcamps,
        'skills': skills,
        'skills_by_category': skills_by_category,
        'github_url': profile.github_url,
        'linkedin_url': profile.linkedin_url,
    }


def generate_resume_pdf_response(profile, filename=None):
    """
    Generate PDF resume and return as HTTP response for download
    
    Args:
        profile: Profile model instance
        filename: Optional custom filename for the PDF
        
    Returns:
        HttpResponse: PDF file as downloadable response or error response
    """
    pdf_bytes = generate_resume_pdf(profile)
    
    if pdf_bytes is None:
        # Return an error response if PDF generation failed
        from django.http import HttpResponseServerError
        return HttpResponseServerError(
            "PDF generation is currently unavailable. Please try again later."
        )
    
    if not filename:
        filename = f"{profile.name.replace(' ', '_')}_Resume.pdf"
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(pdf_bytes)
    
    return response


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