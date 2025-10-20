from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0014_add_language_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_language', models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], default='en', max_length=10, verbose_name='Default language')),
                ('auto_translate_enabled', models.BooleanField(default=False, verbose_name='Traduccion automatica')),
                ('translation_provider', models.CharField(choices=[('libretranslate', 'LibreTranslate')], default='libretranslate', max_length=50, verbose_name='Proveedor de traduccion')),
                ('translation_api_url', models.URLField(blank=True, verbose_name='URL del servicio de traduccion')),
                ('translation_api_key', models.CharField(blank=True, max_length=255, verbose_name='API key del servicio de traduccion')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
