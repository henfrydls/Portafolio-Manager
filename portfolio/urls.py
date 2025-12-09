"""
URL configuration for portfolio app.
Single page portfolio with clean layout
"""
from django.urls import path
from . import views

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
    path('resume/pdf/', views.ResumePDFView.as_view(), name='resume-pdf'),

    # Initial setup wizard
    path('setup/', views.InitialSetupView.as_view(), name='initial-setup'),

    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('password-change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # AJAX Authentication URLs
    path('api/session-status/', views.SessionStatusView.as_view(), name='session-status'),
    path('api/extend-session/', views.ExtendSessionView.as_view(), name='extend-session'),

    # Admin URLs (protected) - keep these for content management
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('dashboard/settings/', views.SiteConfigurationUpdateView.as_view(), name='admin-site-configuration'),
    path('analytics/', views.AnalyticsView.as_view(), name='admin-analytics'),
    
    # Profile Management
    path('manage/profile/edit/', views.ProfileUpdateView.as_view(), name='admin-profile-edit'),
    
    # Project Management
    path('manage/projects/', views.ProjectListAdminView.as_view(), name='admin-project-list'),
    path('manage/projects/create/', views.ProjectCreateView.as_view(), name='admin-project-create'),
    path('manage/projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='admin-project-edit'),
    path('manage/projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='admin-project-delete'),

    # Catalog Management - Categories
    path('manage/catalogs/categories/', views.CategoryListAdminView.as_view(), name='admin-category-list'),
    path('manage/catalogs/categories/create/', views.CategoryCreateView.as_view(), name='admin-category-create'),
    path('manage/catalogs/categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='admin-category-edit'),
    path('manage/catalogs/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='admin-category-delete'),

    # Catalog Management - Project Types
    path('manage/catalogs/project-types/', views.ProjectTypeListAdminView.as_view(), name='admin-projecttype-list'),
    path('manage/catalogs/project-types/create/', views.ProjectTypeCreateView.as_view(), name='admin-projecttype-create'),
    path('manage/catalogs/project-types/<int:pk>/edit/', views.ProjectTypeUpdateView.as_view(), name='admin-projecttype-edit'),
    path('manage/catalogs/project-types/<int:pk>/delete/', views.ProjectTypeDeleteView.as_view(), name='admin-projecttype-delete'),

    # Catalog Management - Knowledge Bases
    path('manage/catalogs/knowledge-bases/', views.KnowledgeBaseListAdminView.as_view(), name='admin-knowledgebase-list'),
    path('manage/catalogs/knowledge-bases/create/', views.KnowledgeBaseCreateView.as_view(), name='admin-knowledgebase-create'),
    path('manage/catalogs/knowledge-bases/<int:pk>/edit/', views.KnowledgeBaseUpdateView.as_view(), name='admin-knowledgebase-edit'),
    path('manage/catalogs/knowledge-bases/<int:pk>/delete/', views.KnowledgeBaseDeleteView.as_view(), name='admin-knowledgebase-delete'),

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
    
    # Language Management API
    path('admin-panel/languages/list/', views.LanguageListAPIView.as_view(), name='api-language-list'),
    path('admin-panel/languages/<int:pk>/', views.LanguageDetailAPIView.as_view(), name='api-language-detail'),
    path('admin-panel/languages/create/', views.LanguageCreateAPIView.as_view(), name='api-language-create'),
    path('admin-panel/languages/<int:pk>/update/', views.LanguageUpdateAPIView.as_view(), name='api-language-update'),
    path('admin-panel/languages/<int:pk>/delete/', views.LanguageDeleteAPIView.as_view(), name='api-language-delete'),
    
    # SEO URLs
    path('robots.txt', views.robots_txt, name='robots-txt'),
    path('.well-known/security.txt', views.security_txt, name='security-txt'),
    path('manifest.json', views.manifest_json, name='manifest-json'),
]
