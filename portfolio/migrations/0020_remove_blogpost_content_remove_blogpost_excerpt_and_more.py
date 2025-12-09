# -*- coding: utf-8 -*-
import django.db.models.deletion
import parler.fields
import parler.models
import portfolio.utils.validators
from django.db import migrations, models


def copy_blogpost_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, title, content, excerpt FROM portfolio_blogpost")
    rows = cursor.fetchall()
    BlogPostTranslation = apps.get_model('portfolio', 'BlogPostTranslation')
    for pk, title, content, excerpt in rows:
        BlogPostTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            title=title or '',
            content=content or '',
            excerpt=excerpt or '',
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0019_alter_profile_managers_alter_project_managers_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='BlogPost'),
                migrations.CreateModel(
                    name='BlogPost',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                        ('featured_image', models.ImageField(blank=True, upload_to='blog/', validators=[portfolio.utils.validators.blog_image_validator, portfolio.utils.validators.validate_no_executable], verbose_name='Imagen destacada')),
                        ('tags', models.CharField(blank=True, help_text='Tags separados por comas', max_length=200, verbose_name='Tags')),
                        ('status', models.CharField(choices=[('draft', 'Borrador'), ('published', 'Publicado'), ('archived', 'Archivado')], default='draft', max_length=10, verbose_name='Estado')),
                        ('publish_date', models.DateTimeField(verbose_name='Fecha de publicacion')),
                        ('reading_time', models.PositiveIntegerField(default=5, verbose_name='Tiempo de lectura (minutos)')),
                        ('featured', models.BooleanField(default=False, verbose_name='Post destacado')),
                        ('github_url', models.URLField(blank=True, help_text='Repositorio relacionado con el post', verbose_name='URL de GitHub')),
                        ('medium_url', models.URLField(blank=True, help_text='Enlace al articulo en Medium', verbose_name='URL de Medium')),
                        ('linkedin_url', models.URLField(blank=True, help_text='Enlace al post en LinkedIn', verbose_name='URL de LinkedIn')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('category', models.ForeignKey(blank=True, help_text='Categoria principal del post', null=True, on_delete=django.db.models.deletion.PROTECT, to='portfolio.category', verbose_name='Categoria')),
                    ],
                    options={
                        'verbose_name': 'Post del Blog',
                        'verbose_name_plural': 'Posts del Blog',
                        'ordering': ['-publish_date'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[
                        ('objects', parler.models.TranslatableManager()),
                    ],
                ),
            ],
        ),
        migrations.CreateModel(
            name='BlogPostTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Titulo')),
                ('content', models.TextField(verbose_name='Contenido')),
                ('excerpt', models.TextField(max_length=300, verbose_name='Extracto')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.blogpost')),
            ],
            options={
                'verbose_name': 'Post del Blog Translation',
                'db_table': 'portfolio_blogpost_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_blogpost_translations, noop),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_blogpost DROP COLUMN title",
            reverse_sql="ALTER TABLE portfolio_blogpost ADD COLUMN title varchar(200)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_blogpost DROP COLUMN content",
            reverse_sql="ALTER TABLE portfolio_blogpost ADD COLUMN content text",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_blogpost DROP COLUMN excerpt",
            reverse_sql="ALTER TABLE portfolio_blogpost ADD COLUMN excerpt text",
        ),
    ]
