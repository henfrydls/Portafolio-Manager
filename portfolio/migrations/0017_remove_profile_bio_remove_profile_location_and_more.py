# -*- coding: utf-8 -*-
import django.db.models.deletion
import parler.fields
import parler.models
import portfolio.validators
from django.db import migrations, models


def copy_profile_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, name, title, bio, location FROM portfolio_profile")
    rows = cursor.fetchall()
    ProfileTranslation = apps.get_model('portfolio', 'ProfileTranslation')
    for pk, name, title, bio, location in rows:
        ProfileTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            name=name or '',
            title=title or '',
            bio=bio or '',
            location=location or '',
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0016_alter_siteconfiguration_options_alter_profile_bio_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Profile'),
                migrations.CreateModel(
                    name='Profile',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('profile_image', models.ImageField(help_text='Sube una imagen cuadrada (misma anchura y altura). Se optimizará automáticamente a 250x250px. Formatos: JPG, PNG, WebP. Máximo 3MB.', upload_to='profile/', validators=[portfolio.validators.ProfileImageValidator(), portfolio.validators.validate_no_executable], verbose_name='Foto de perfil')),
                        ('email', models.EmailField(max_length=254, verbose_name='Email')),
                        ('phone', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                        ('linkedin_url', models.URLField(blank=True, verbose_name='URL de LinkedIn')),
                        ('github_url', models.URLField(blank=True, verbose_name='URL de GitHub')),
                        ('medium_url', models.URLField(blank=True, verbose_name='URL de Medium')),
                        ('resume_pdf', models.FileField(blank=True, help_text='Upload your resume in English (PDF format)', upload_to='profile/', validators=[portfolio.validators.DocumentValidator(max_size=5242880), portfolio.validators.validate_no_executable], verbose_name='CV en PDF (English)')),
                        ('resume_pdf_es', models.FileField(blank=True, help_text='Sube tu currículum en español (formato PDF)', upload_to='profile/', validators=[portfolio.validators.DocumentValidator(max_size=5242880), portfolio.validators.validate_no_executable], verbose_name='CV en PDF (Español)')),
                        ('show_web_resume', models.BooleanField(default=True, verbose_name='Mostrar CV web')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Perfil',
                        'verbose_name_plural': 'Perfiles',
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[
                        ('objects', parler.models.TranslatableManager()),
                    ],
                ),
            ],
        ),
        migrations.CreateModel(
            name='ProfileTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('title', models.CharField(max_length=200, verbose_name='Título profesional')),
                ('bio', models.TextField(verbose_name='Biografía')),
                ('location', models.CharField(max_length=100, verbose_name='Ubicación')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.profile')),
            ],
            options={
                'verbose_name': 'Perfil Translation',
                'db_table': 'portfolio_profile_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_profile_translations, noop),
    ]
