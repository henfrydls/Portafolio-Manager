# Management Commands Guide

This document describes the available Django management commands for the portfolio application.

## Setup & Configuration Commands

### `check_env`
Verifies that environment variables from `.env` file are loading correctly.

```bash
python manage.py check_env
```

**Use case**: Troubleshoot configuration issues, verify .env setup.

### `check_settings`
Shows which Django settings file is being used and current configuration.

```bash
python manage.py check_settings
```

**Use case**: Verify environment (development/production), check settings.

### `setup_cache`
Sets up database cache table for production environments.

```bash
python manage.py setup_cache
```

**Use case**: Initialize caching system for better performance.

## Email Commands

### `test_email`
Tests email configuration by sending a test email.

```bash
# Send to profile email
python manage.py test_email

# Send to specific email
python manage.py test_email --to user@example.com

# Use EmailService (recommended)
python manage.py test_email --service
```

**Use case**: Verify email setup, troubleshoot email delivery issues.

### `check_email_domain`
Checks compatibility of email domains with Gmail SMTP.

```bash
python manage.py check_email_domain user@example.com
```

**Use case**: Understand email delivery expectations for different domains.

## Data Population Commands

### `populate_sample_data`
Populates the database with sample portfolio data for testing/demo.

```bash
python manage.py populate_sample_data
```

**Use case**: Quick setup for development, demo purposes.

### `add_sample_projects`
Adds sample projects to the portfolio.

```bash
python manage.py add_sample_projects
```

**Use case**: Populate projects section with example data.

### `populate_technologies`
Populates the database with common web technologies.

```bash
python manage.py populate_technologies
```

**Use case**: Initialize technology tags for projects.

### `populate_categories`
Populates blog categories.

```bash
python manage.py populate_categories
```

**Use case**: Initialize blog category system.

### `populate_project_types`
Populates project type classifications.

```bash
python manage.py populate_project_types
```

**Use case**: Initialize project categorization system.

## Maintenance Commands

### `cleanup_old_visits`
Cleans up old page visit records to maintain database performance.

```bash
python manage.py cleanup_old_visits
```

**Use case**: Regular maintenance, keep analytics data manageable.

### `visit_stats`
Shows page visit statistics and analytics data.

```bash
python manage.py visit_stats
```

**Use case**: View traffic analytics, understand visitor patterns.

## Usage Examples

### Initial Setup
```bash
# 1. Verify environment configuration
python manage.py check_env
python manage.py check_settings

# 2. Set up cache (production)
python manage.py setup_cache

# 3. Populate initial data
python manage.py populate_technologies
python manage.py populate_categories
python manage.py populate_project_types

# 4. Add sample content (optional)
python manage.py populate_sample_data
```

### Email Configuration
```bash
# 1. Test basic email setup
python manage.py test_email

# 2. Check domain compatibility
python manage.py check_email_domain your-email@domain.com

# 3. Test with specific recipient
python manage.py test_email --to client@example.com --service
```

### Regular Maintenance
```bash
# Clean up old analytics data (run monthly)
python manage.py cleanup_old_visits

# Check system status
python manage.py check_env
python manage.py visit_stats
```

## Command Categories

### 🔧 **Essential for Setup**
- `check_env` - Verify configuration
- `test_email` - Verify email functionality
- `populate_technologies` - Initialize tech stack

### 📊 **Data Management**
- `populate_sample_data` - Demo content
- `cleanup_old_visits` - Maintenance
- `visit_stats` - Analytics

### 🛠️ **Development Tools**
- `check_settings` - Environment verification
- `check_email_domain` - Email troubleshooting

### 🚀 **Production Setup**
- `setup_cache` - Performance optimization
- `cleanup_old_visits` - Regular maintenance

## Best Practices

1. **Always run `check_env`** after changing `.env` file
2. **Test email configuration** before going live with `test_email`
3. **Set up caching** in production with `setup_cache`
4. **Regular maintenance** with `cleanup_old_visits` (monthly)
5. **Use sample data** for development/demo with `populate_sample_data`

## Troubleshooting

### Email Issues
```bash
python manage.py check_env  # Verify EMAIL_* variables
python manage.py test_email --service  # Test email service
python manage.py check_email_domain recipient@domain.com  # Check compatibility
```

### Configuration Issues
```bash
python manage.py check_settings  # Verify environment
python manage.py check_env  # Verify .env loading
```

### Performance Issues
```bash
python manage.py setup_cache  # Enable caching
python manage.py cleanup_old_visits  # Clean old data
```