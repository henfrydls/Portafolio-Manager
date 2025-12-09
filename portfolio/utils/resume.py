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
