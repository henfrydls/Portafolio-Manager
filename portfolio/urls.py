"""
URL configuration for portfolio app.
Single page portfolio with clean layout
"""
from django.urls import path
from . import views
from . import auth_views

app_name = 'portfolio'

urlpatterns = [
    # Main single-page portfolio
    path('', views.HomeView.as_view(), name='home'),

    # Blog listing page with search
    path('posts/', views.BlogListView.as_view(), name='post-list'),

    # Blog post detail pages
    path('post/<slug:slug>/', views.BlogDetailView.as_view(), name='post-detail'),

    # Project detail pages
    path('project/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),

    # Resume page
    path('resume/', views.ResumeView.as_view(), name='resume'),

    # Authentication URLs
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.CustomLogoutView.as_view(), name='logout'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password-change'),
    
    # AJAX Authentication URLs
    path('api/session-status/', auth_views.SessionStatusView.as_view(), name='session-status'),
    path('api/extend-session/', auth_views.ExtendSessionView.as_view(), name='extend-session'),

    # Admin URLs (protected) - keep these for content management
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('analytics/', views.AnalyticsView.as_view(), name='admin-analytics'),
    
    # Profile Management
    path('manage/profile/edit/', views.ProfileUpdateView.as_view(), name='admin-profile-edit'),
    
    # Project Management
    path('manage/projects/', views.ProjectListAdminView.as_view(), name='admin-project-list'),
    path('manage/projects/create/', views.ProjectCreateView.as_view(), name='admin-project-create'),
    path('manage/projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='admin-project-edit'),
    path('manage/projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='admin-project-delete'),
    
    # Blog Post Management
    path('manage/blog/', views.BlogPostListAdminView.as_view(), name='admin-blog-list'),
    path('manage/blog/create/', views.BlogPostCreateView.as_view(), name='admin-blog-create'),
    path('manage/blog/<int:pk>/edit/', views.BlogPostUpdateView.as_view(), name='admin-blog-edit'),
    path('manage/blog/<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='admin-blog-delete'),
    
    # Contact Management
    path('manage/contacts/', views.ContactListAdminView.as_view(), name='admin-contact-list'),
    path('manage/contacts/<int:pk>/', views.ContactDetailView.as_view(), name='admin-contact-detail'),
    path('manage/contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='admin-contact-delete'),
    
    # CV Management Hub
    path('manage/cv/', views.CVManagementView.as_view(), name='admin-cv-hub'),
    
    # CV Management - Experience
    path('manage/cv/experience/', views.ExperienceListAdminView.as_view(), name='admin-experience-list'),
    path('manage/cv/experience/create/', views.ExperienceCreateView.as_view(), name='admin-experience-create'),
    path('manage/cv/experience/<int:pk>/edit/', views.ExperienceUpdateView.as_view(), name='admin-experience-edit'),
    path('manage/cv/experience/<int:pk>/delete/', views.ExperienceDeleteView.as_view(), name='admin-experience-delete'),
    
    # CV Management - Education
    path('manage/cv/education/', views.EducationListAdminView.as_view(), name='admin-education-list'),
    path('manage/cv/education/create/', views.EducationCreateView.as_view(), name='admin-education-create'),
    path('manage/cv/education/<int:pk>/edit/', views.EducationUpdateView.as_view(), name='admin-education-edit'),
    path('manage/cv/education/<int:pk>/delete/', views.EducationDeleteView.as_view(), name='admin-education-delete'),
    
    # CV Management - Skills
    path('manage/cv/skills/', views.SkillListAdminView.as_view(), name='admin-skill-list'),
    path('manage/cv/skills/create/', views.SkillCreateView.as_view(), name='admin-skill-create'),
    path('manage/cv/skills/<int:pk>/edit/', views.SkillUpdateView.as_view(), name='admin-skill-edit'),
    path('manage/cv/skills/<int:pk>/delete/', views.SkillDeleteView.as_view(), name='admin-skill-delete'),
    
    # AJAX Quick Actions
    path('manage/ajax/upload-blog-image/', views.BlogImageUploadView.as_view(), name='ajax-upload-blog-image'),
    path('manage/ajax/toggle-contact-read/', views.ToggleContactReadView.as_view(), name='ajax-toggle-contact-read'),
    path('manage/ajax/toggle-project-featured/', views.ToggleProjectFeaturedView.as_view(), name='ajax-toggle-project-featured'),
    path('manage/ajax/toggle-blog-featured/', views.ToggleBlogPostFeaturedView.as_view(), name='ajax-toggle-blog-featured'),
    path('manage/ajax/quick-publish-blog/', views.QuickPublishBlogPostView.as_view(), name='ajax-quick-publish-blog'),
    path('manage/ajax/test-email/', views.EmailTestView.as_view(), name='ajax-test-email'),
]