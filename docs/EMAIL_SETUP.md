# Email Configuration Guide

**Bilingual summary / Resumen bilingüe**  
- EN: Configure SMTP credentials, sender, and contact confirmations. Test from admin or shell.  
- ES: Configura credenciales SMTP, remitente y confirmaciones de contacto. Prueba desde el admin o consola.

This guide explains how to configure email functionality for your portfolio website.

**Pasos rápidos (ES)**
- Ajusta en `.env`: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`.
- Activa/desactiva `SEND_CONTACT_CONFIRMATIONS` según tu flujo.
- Prueba desde el admin o con un comando de prueba (`python manage.py test_email` si está disponible).

## Overview

The portfolio includes email functionality for:
- **Contact form notifications**: Receive emails when visitors submit the contact form
- **Contact confirmations**: Send automatic confirmation emails to visitors
- **Admin notifications**: Get notified about important events

## Quick Setup

### 1. Configure Environment Variables

Copy the email settings from `.env.example` to your `.env` file:

```bash
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Contact Form Email Settings
SEND_CONTACT_CONFIRMATIONS=True
```

### 2. Set Up Your Profile Email

1. Go to your admin dashboard: `/dashboard/`
2. Click "Edit Profile"
3. Set your email address in the profile
4. This email will receive contact form notifications

### 3. Test Email Configuration

**From Admin Dashboard:**
1. Go to `/dashboard/`
2. Click "Test Email Configuration" in Advanced Management
3. Check if the test email is sent successfully

**From Command Line:**
```bash
python manage.py test_email
```

## Email Provider Setup

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - **Direct URL**: https://myaccount.google.com/apppasswords
   - Or go to Google Account settings → Security → 2-Step Verification → App passwords
   - Select "Mail" as application type
   - Select "Other (custom name)" and enter "Django Portfolio"
   - Google will generate a 16-character password like: `abcd efgh ijkl mnop`
3. **Use App Password** in `EMAIL_HOST_PASSWORD` (without spaces)

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com  # OPCIONAL: Si no se especifica, usa EMAIL_HOST_USER automáticamente
```

### Other Email Providers

#### Outlook/Hotmail
```bash
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Yahoo Mail
```bash
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

#### Custom SMTP Server
```bash
EMAIL_HOST=mail.yourdomain.com
EMAIL_PORT=587  # or 465 for SSL
EMAIL_USE_TLS=True  # or EMAIL_USE_SSL=True
```

## Development vs Production

### Development
- Uses console backend by default (emails printed to console)
- Override with real SMTP for testing:
  ```bash
  DJANGO_SETTINGS_MODULE=config.settings.development
  ```

### Production
- Uses SMTP backend automatically
- Requires all email environment variables

## Email Templates

The system includes responsive HTML email templates:

- **Contact Notification** (`templates/portfolio/email/contact_notification.html`)
- **Contact Confirmation** (`templates/portfolio/email/contact_confirmation.html`)

### Customizing Email Templates

1. Edit the HTML templates in `templates/portfolio/email/`
2. Modify the text versions (`.txt` files) for plain text emails
3. Update the `EmailService` class if needed

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `587` |
| `EMAIL_USE_TLS` | Use TLS encryption | `True` |
| `EMAIL_HOST_USER` | SMTP username | Required |
| `EMAIL_HOST_PASSWORD` | SMTP password | Required |
| `DEFAULT_FROM_EMAIL` | From email address | Required |
| `SEND_CONTACT_CONFIRMATIONS` | Send confirmation emails | `True` |

### Django Settings

Additional settings in `config/settings/base.py`:

```python
# Contact form email settings
SEND_CONTACT_CONFIRMATIONS = True
EMAIL_TIMEOUT = 30  # seconds
```

## Troubleshooting

### Common Issues

#### 0. Emails not reaching external domains (non-Gmail)
- **Gmail → External domains**: May be delayed (5-30 minutes) or blocked
- **Corporate domains**: Often have strict anti-spam policies
- **Solutions**:
  - Wait longer (up to 30 minutes)
  - Check recipient's spam folder
  - Contact recipient's IT administrator
  - Consider using professional email service (SendGrid, Mailgun)
- **Gmail → Gmail**: Usually works immediately

#### 1. "Authentication failed" Error
- **Gmail**: Use App Password, not regular password
  - Generate at: https://myaccount.google.com/apppasswords
  - Must have 2FA enabled first
  - Use 16-character password without spaces
- **Other providers**: Check username/password
- Verify 2FA settings

#### 2. "Connection refused" Error
- Check `EMAIL_HOST` and `EMAIL_PORT`
- Verify firewall/network settings
- Try different ports (587, 465, 25)

#### 3. "From address not allowed" Error
- Set `DEFAULT_FROM_EMAIL` to match your email provider
- **IMPORTANT**: Use your real email address, not noreply@yourdomain.com
- Gmail requires `DEFAULT_FROM_EMAIL` to match `EMAIL_HOST_USER`
- Some providers require matching from/auth emails

#### 4. Emails not being sent
- Check Django logs: `tail -f portfolio.log`
- Test with management command: `python manage.py test_email`
- Verify profile email is set in admin

### Debug Commands

```bash
# Test email configuration
python manage.py test_email

# Test with specific recipient
python manage.py test_email --to test@example.com

# Test using EmailService
python manage.py test_email --service

# Check Django settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.EMAIL_HOST)
```

### Log Files

Check `portfolio.log` for email-related errors:

```bash
tail -f portfolio.log | grep -i email
```

## Security Best Practices

1. **Use App Passwords** instead of regular passwords
2. **Enable TLS/SSL** for encrypted connections
3. **Keep credentials secure** in `.env` file (never commit to git)
4. **Use environment-specific settings** for different deployments
5. **Monitor email logs** for suspicious activity

## Advanced Configuration

### Custom Email Service

Extend the `EmailService` class for custom functionality:

```python
# portfolio/custom_email.py
from .email_service import EmailService

class CustomEmailService(EmailService):
    @staticmethod
    def send_custom_notification(data):
        # Your custom email logic
        pass
```

### Email Queue (Future Enhancement)

For high-traffic sites, consider implementing email queues:
- Celery with Redis/RabbitMQ
- Django-RQ
- Database-based queues

## Support

If you encounter issues:

1. Check this documentation
2. Review Django email documentation
3. Test with the management command
4. Check logs for specific error messages
5. Verify email provider settings

For Gmail-specific issues, see: [Google App Passwords Help](https://support.google.com/accounts/answer/185833)
