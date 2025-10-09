# Admin Panel Usage Guide

This comprehensive guide explains how to use the Django admin panel to manage your portfolio content effectively.

**Note:** This is a generic portfolio system. All personal information should be configured through the admin panel and environment variables, not hardcoded in the application.

## 🚀 Getting Started

### Accessing the Admin Panel

1. **Start your development server**:
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```

2. **Navigate to the admin panel**:
   - URL: `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials

3. **Create a superuser** (if you haven't already):
   ```bash
   python manage.py createsuperuser --settings=config.settings.development
   ```

### Admin Dashboard Overview

The admin panel is organized into the following sections:

- **👤 Profile Management** - Personal information and settings
- **🚀 Projects** - Portfolio projects and showcases
- **📝 Blog Posts** - Content management system
- **💼 Experience** - Work history and professional background
- **🎓 Education** - Academic background and certifications
- **⚡ Skills** - Technical and professional skills
- **🔧 Technologies** - Technology stack and tools
- **📧 Contact Messages** - Visitor inquiries and feedback
- **📈 Analytics** - Visit tracking and statistics

## 👤 Profile Management

### Setting Up Your Profile

1. **Navigate to "Profiles"** in the admin panel
2. **Click "Add Profile"** or edit existing profile
3. **Fill in the required information**:

#### Basic Information
- **Name**: Your full name
- **Title**: Professional title (e.g., "Full Stack Developer")
- **Bio**: Professional summary (2-3 paragraphs recommended)
- **Email**: Professional contact email
- **Phone**: Contact phone number (optional)
- **Location**: Current location

#### Social Media Links
- **LinkedIn URL**: Your LinkedIn profile URL
- **GitHub URL**: Your GitHub profile URL

#### Resume Settings
- **Resume PDF (English)**: Upload a PDF version of your resume in English
- **Resume PDF (Español)**: Upload a PDF version of your resume in Spanish
- **Show Web Resume**: Toggle to display web version of resume
- **Note**: The system automatically serves the appropriate CV based on the visitor's language. If only one CV is uploaded, it will be served to all visitors regardless of language.

#### Profile Image
- **Upload a professional photo** (recommended: 400x400px, square format)
- **Supported formats**: JPG, PNG, WebP
- **Maximum size**: 5MB

### Best Practices for Profile
- Keep bio concise but informative
- Use a professional, high-quality profile photo
- Ensure all URLs are working and up-to-date
- Update resume PDF regularly

## 🚀 Project Management

### Adding a New Project

1. **Navigate to "Projects"** → **"Add Project"**
2. **Fill in project details**:

#### Basic Information
- **Title**: Project name (e.g., "E-commerce Platform")
- **Slug**: URL-friendly version (auto-generated from title)
- **Description**: Brief project summary (1-2 sentences)
- **Detailed Description**: Comprehensive project details (supports HTML)

#### Visual Content
- **Image**: Main project screenshot or logo
- **Additional Images**: Upload multiple project screenshots

#### Project Links
- **GitHub URL**: Repository link (if public)
- **Demo URL**: Live demo or deployed version
- **Documentation URL**: Project documentation (optional)

#### Categorization
- **Technologies**: Select relevant technologies (hold Ctrl/Cmd for multiple)
- **Project Type**: Choose appropriate category
- **Visibility**: Public (shown to visitors) or Private (hidden)
- **Featured**: Mark important projects to highlight on homepage

#### Organization
- **Order**: Numeric value for sorting (lower numbers appear first)

### Managing Project Visibility

- **Public Projects**: Visible to all visitors with full details
- **Private Projects**: Hidden from public view (useful for client work)
- **Featured Projects**: Highlighted on homepage and project listing

### Project Best Practices
- Use high-quality screenshots (recommended: 1200x800px)
- Write clear, engaging descriptions
- Keep technology tags relevant and accurate
- Update project status and links regularly

## 📝 Blog Post Management

### Creating a Blog Post

1. **Navigate to "Blog Posts"** → **"Add Blog Post"**
2. **Configure post settings**:

#### Content
- **Title**: Engaging post title
- **Slug**: URL-friendly version
- **Content**: Full post content (rich text editor available)
- **Excerpt**: Brief summary for listings (150-300 characters)

#### Categorization
- **Post Type**: Choose from News, Tutorial, Opinion, Project, Career
- **Category**: Select appropriate blog category
- **Tags**: Add relevant tags (comma-separated)

#### Publishing
- **Status**: Draft, Published, or Archived
- **Publish Date**: Schedule publication date/time
- **Featured**: Mark important posts for homepage

#### SEO & Metadata
- **Featured Image**: Main post image (recommended: 1200x630px)
- **Reading Time**: Estimated reading time in minutes
- **Meta Description**: SEO description (150-160 characters)

### Blog Post Types

- **📰 News**: Professional updates, achievements, announcements
- **📚 Tutorial**: Technical guides, how-to articles, code examples
- **💭 Opinion**: Industry insights, personal reflections, commentary
- **🚀 Project**: Detailed project case studies and breakdowns
- **💼 Career**: Professional experiences, lessons learned, advice

### Content Writing Tips
- Use clear, engaging headlines
- Break content into digestible sections
- Include relevant images and code examples
- Optimize for SEO with proper meta descriptions
- Schedule posts for optimal engagement times

## 💼 Experience Management

### Adding Work Experience

1. **Navigate to "Experiences"** → **"Add Experience"**
2. **Fill in employment details**:

#### Company Information
- **Company**: Employer name
- **Position**: Job title/role
- **Description**: Key responsibilities and achievements
- **Location**: Work location (optional)

#### Timeline
- **Start Date**: Employment start date
- **End Date**: Employment end date (leave blank if current)
- **Current**: Check if this is your current position

#### Organization
- **Order**: Numeric value for sorting (most recent first)

### Best Practices for Experience
- Focus on achievements rather than just responsibilities
- Use action verbs and quantifiable results
- Keep descriptions concise but informative
- Update current position status regularly

## 🎓 Education Management

### Adding Educational Background

1. **Navigate to "Education"** → **"Add Education"**
2. **Select education type and fill details**:

#### Education Types
- **🎓 Formal Education**: Universities, colleges, institutes
- **💻 Online Course**: Coursera, Udemy, Platzi, etc.
- **📜 Certification**: AWS, Google, Microsoft certifications
- **🚀 Bootcamp**: Intensive coding programs
- **🛠️ Workshop**: Short-term training sessions

#### Institution Details
- **Institution**: School, platform, or organization name
- **Degree/Certificate**: Qualification obtained
- **Field of Study**: Subject area or specialization
- **Description**: Additional details or achievements

#### Timeline & Verification
- **Start Date**: Program start date
- **End Date**: Completion date (leave blank if ongoing)
- **Current**: Check if currently enrolled
- **Credential ID**: Certificate or credential identifier
- **Credential URL**: Verification link for certificates

### Education Best Practices
- Include relevant certifications and courses
- Add verification links when available
- Organize by relevance and recency
- Update with new qualifications regularly

## ⚡ Skills Management

### Adding Technical Skills

1. **Navigate to "Skills"** → **"Add Skill"**
2. **Define skill details**:

#### Skill Information
- **Name**: Technology or skill name
- **Category**: Group skills logically (Frontend, Backend, Tools, etc.)
- **Proficiency**: Rate from 1 (Basic) to 4 (Expert)
- **Years Experience**: How long you've worked with this skill

#### Skill Categories
- **Frontend**: HTML, CSS, JavaScript, React, Vue.js
- **Backend**: Python, Django, Node.js, databases
- **Tools**: Git, Docker, AWS, development tools
- **Soft Skills**: Communication, leadership, project management

### Proficiency Levels
- **1 - Basic**: Learning or limited experience
- **2 - Intermediate**: Comfortable with common tasks
- **3 - Advanced**: Can handle complex projects independently
- **4 - Expert**: Can mentor others and solve complex problems

## 🔧 Technology Management

### Managing Technology Tags

Technologies are used to categorize projects and skills. The system comes with 50+ predefined technologies.

1. **Navigate to "Technologies"** → **View existing technologies**
2. **Add new technology** if needed:
   - **Name**: Technology name
   - **Icon**: CSS class for icon display
   - **Color**: Hex color code for visual consistency

### Popular Technologies Included
- **Frontend**: React, Vue.js, Angular, HTML5, CSS3, JavaScript
- **Backend**: Python, Django, Node.js, Express, PHP
- **Databases**: PostgreSQL, MySQL, MongoDB, SQLite
- **Tools**: Git, Docker, AWS, Nginx, Redis
- **Mobile**: React Native, Flutter, Swift, Kotlin

## 📧 Contact Message Management

### Viewing Contact Messages

1. **Navigate to "Contacts"** to view all messages
2. **Message details include**:
   - Sender name and email
   - Subject and message content
   - Timestamp
   - Read status

### Managing Messages
- **Mark as read/unread** to track follow-ups
- **Reply directly** via email client
- **Export messages** for external management
- **Delete spam** or irrelevant messages

### Contact Form Features
- **Spam protection** with basic validation
- **Email notifications** sent to your configured email
- **Automatic timestamping** for all messages
- **IP tracking** for security purposes

## 📈 Analytics & Monitoring

### Page Visit Tracking

The system automatically tracks:
- **Page views** and visitor counts
- **Popular pages** and content
- **Visit timestamps** and patterns
- **Basic visitor information** (IP, user agent)

### Viewing Analytics

1. **Navigate to "Page Visits"** to view raw data
2. **Use management commands** for detailed statistics:
   ```bash
   python manage.py visit_stats
   ```

### Privacy & Data Management
- **No personal data** is collected from visitors
- **IP addresses** are stored for security only
- **Automatic cleanup** removes old visit data
- **GDPR compliant** data handling

## 🛠️ Advanced Features

### Bulk Operations

#### Bulk Project Management
- **Select multiple projects** using checkboxes
- **Change visibility** for multiple projects at once
- **Update categories** or technologies in bulk
- **Export project data** for external use

#### Bulk Content Management
- **Publish multiple blog posts** simultaneously
- **Update post categories** in bulk
- **Archive old content** efficiently
- **Export content** for backup

### Import/Export Features

#### Data Export
- **Export projects** as CSV or JSON
- **Backup blog content** with full formatting
- **Export contact messages** for external CRM
- **Generate analytics reports**

#### Data Import
- **Import projects** from external sources
- **Bulk upload** blog content
- **Import technology lists** from other systems
- **Restore from backups**

## 🔒 Security & Best Practices

### Admin Security

#### Password Management
- **Use strong passwords** with mixed characters
- **Enable two-factor authentication** if available
- **Change passwords regularly** (every 3-6 months)
- **Don't share admin credentials**

#### Session Management
- **Automatic logout** after 30 minutes of inactivity
- **Secure session cookies** in production
- **HTTPS enforcement** for admin access
- **IP-based access control** if needed

### Content Security

#### File Uploads
- **Validate file types** and sizes automatically
- **Scan uploads** for malicious content
- **Organize media files** in appropriate directories
- **Regular backup** of uploaded content

#### Data Validation
- **Form validation** prevents invalid data
- **XSS protection** for user-generated content
- **SQL injection prevention** through Django ORM
- **CSRF protection** on all forms

## 🚨 Troubleshooting

### Common Issues

#### Login Problems
```bash
# Reset admin password
python manage.py changepassword your-username

# Create new superuser
python manage.py createsuperuser
```

#### File Upload Issues
- **Check file size limits** (max 5MB for images)
- **Verify file permissions** in media directory
- **Ensure supported formats** (JPG, PNG, PDF, etc.)
- **Check disk space** availability

#### Email Configuration
```bash
# Test email setup
python manage.py test_email

# Verify environment variables
python manage.py check_env
```

#### Performance Issues
```bash
# Clean old analytics data
python manage.py cleanup_old_visits

# Check database size
python manage.py dbshell
.databases
```

### Getting Help

#### Debug Information
- **Check Django logs** for error details
- **Use browser developer tools** for frontend issues
- **Verify environment settings** with management commands
- **Test individual components** systematically

#### Support Resources
- **Django Documentation**: https://docs.djangoproject.com/
- **Project Repository**: Check README and issues
- **Management Commands**: Use built-in diagnostic tools
- **Community Forums**: Django community support

## 📋 Quick Reference

### Essential Admin Tasks

#### Daily Tasks
- [ ] Check new contact messages
- [ ] Review and respond to inquiries
- [ ] Update project status if needed
- [ ] Monitor site analytics

#### Weekly Tasks
- [ ] Publish new blog content
- [ ] Update project information
- [ ] Review and update profile
- [ ] Check email configuration

#### Monthly Tasks
- [ ] Clean old analytics data
- [ ] Update resume and skills
- [ ] Review and archive old content
- [ ] Backup important data

#### Quarterly Tasks
- [ ] Update professional information
- [ ] Review and update project portfolio
- [ ] Analyze traffic and engagement
- [ ] Plan content strategy

### Keyboard Shortcuts

- **Ctrl+S**: Save current form
- **Ctrl+Z**: Undo last action (in rich text editor)
- **Tab**: Navigate between form fields
- **Enter**: Submit form (when focused on submit button)

### Quick Links

- **Admin Dashboard**: `/admin/`
- **Profile Management**: `/admin/portfolio/profile/`
- **Project Management**: `/admin/portfolio/project/`
- **Blog Management**: `/admin/portfolio/blogpost/`
- **Contact Messages**: `/admin/portfolio/contact/`
- **Analytics**: `/admin/portfolio/pagevisit/`

---

This guide covers the essential aspects of managing your portfolio through the Django admin panel. For technical issues or advanced customization, refer to the project documentation or contact the development team.