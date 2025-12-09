# -*- coding: utf-8 -*-
import django.db.models.deletion
import parler.fields
import parler.models
import portfolio.utils.validators
from django.db import migrations, models


def copy_project_translations(apps, schema_editor):
    """
    Populate the new ProjectTranslation table with existing content
    using the current English values as the default translation.
    """
    cursor = schema_editor.connection.cursor()
    cursor.execute(
        "SELECT id, title, description, detailed_description FROM portfolio_project"
    )
    rows = cursor.fetchall()

    ProjectTranslation = apps.get_model('portfolio', 'ProjectTranslation')
    for pk, title, description, detailed_description in rows:
        ProjectTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            title=title or '',
            description=description or '',
            detailed_description=detailed_description or '',
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0017_remove_profile_bio_remove_profile_location_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Project'),
                migrations.CreateModel(
                    name='Project',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('slug', models.SlugField(help_text='URL amigable generada automaticamente', unique=True, verbose_name='Slug')),
                        ('image', models.ImageField(blank=True, upload_to='projects/', validators=[portfolio.utils.validators.project_image_validator, portfolio.utils.validators.validate_no_executable], verbose_name='Imagen principal')),
                        ('project_type', models.CharField(blank=True, choices=[('framework', 'Framework'), ('tool', 'Tool'), ('website', 'Website'), ('template', 'Template'), ('dataset', 'Dataset'), ('mobile_app', 'Mobile App'), ('desktop_app', 'Desktop App'), ('library', 'Library'), ('api', 'API'), ('consulting', 'Consulting'), ('strategy', 'Strategy'), ('research', 'Research'), ('process', 'Process'), ('training', 'Training'), ('case_study', 'Case Study'), ('implementation', 'Implementation'), ('other', 'Other')], default='other', help_text='Categoria del proyecto (Framework, Tool, Website, etc.)', max_length=20, null=True, verbose_name='Tipo de proyecto')),
                        ('stars_count', models.PositiveIntegerField(default=0, help_text='Para proyectos de GitHub, se actualiza automaticamente. Para proyectos privados, puedes agregar un numero estimado.', verbose_name='Numero de estrellas')),
                        ('forks_count', models.PositiveIntegerField(default=0, help_text='Para proyectos de GitHub, se actualiza automaticamente', verbose_name='Numero de forks')),
                        ('primary_language', models.CharField(blank=True, help_text='El lenguaje de programacion principal usado (Python, JavaScript, etc.)', max_length=50, verbose_name='Lenguaje principal')),
                        ('github_owner', models.CharField(blank=True, help_text='Usuario/organizacion propietaria del repositorio (ej: microsoft, google)', max_length=100, verbose_name='Propietario GitHub')),
                        ('is_private_project', models.BooleanField(default=False, help_text='Marcar si es un proyecto privado o de trabajo que no tiene repositorio publico', verbose_name='Proyecto privado/trabajo')),
                        ('github_url', models.URLField(blank=True, verbose_name='URL de GitHub')),
                        ('demo_url', models.URLField(blank=True, verbose_name='URL de demostracion')),
                        ('featured_link_type', models.CharField(choices=[('none', 'Sin enlace'), ('post', 'Enlace a Post'), ('github', 'Usar GitHub URL'), ('demo', 'Usar Demo URL'), ('pdf', 'Archivo PDF'), ('custom', 'URL personalizada')], default='none', help_text="Selecciona que tipo de enlace mostrar cuando el proyecto aparezca en Featured Work", max_length=10, verbose_name='Tipo de enlace para Featured Work')),
                        ('featured_link_pdf', models.FileField(blank=True, help_text="Sube un archivo PDF (solo si tipo es 'Archivo PDF')", upload_to='projects/pdfs/', verbose_name='Archivo PDF')),
                        ('featured_link_custom', models.URLField(blank=True, help_text="URL personalizada (solo si tipo es 'URL personalizada')", verbose_name='URL personalizada')),
                        ('visibility', models.CharField(choices=[('public', 'Publico'), ('private', 'Privado')], default='public', max_length=10, verbose_name='Visibilidad')),
                        ('featured', models.BooleanField(default=False, verbose_name='Proyecto destacado')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Orden de visualizacion')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('featured_link_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.blogpost', verbose_name='Post relacionado')),
                        ('project_type_obj', models.ForeignKey(blank=True, help_text='Tipo de proyecto principal', null=True, on_delete=django.db.models.deletion.PROTECT, to='portfolio.projecttype', verbose_name='Tipo de Proyecto')),
                        ('technologies', models.ManyToManyField(to='portfolio.technology', verbose_name='Tecnologias utilizadas')),
                    ],
                    options={
                        'verbose_name': 'Proyecto',
                        'verbose_name_plural': 'Proyectos',
                        'ordering': ['order', '-created_at'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[
                        ('objects', parler.models.TranslatableManager()),
                    ],
                ),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=200, verbose_name='Titulo')),
                ('description', models.TextField(verbose_name='Descripcion breve')),
                ('detailed_description', models.TextField(verbose_name='Descripcion detallada')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.project')),
            ],
            options={
                'verbose_name': 'Proyecto Translation',
                'db_table': 'portfolio_project_translation',
                'db_tablespace': '',
                'managed': True,
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_project_translations, noop),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_project DROP COLUMN title",
            reverse_sql="ALTER TABLE portfolio_project ADD COLUMN title varchar(200)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_project DROP COLUMN description",
            reverse_sql="ALTER TABLE portfolio_project ADD COLUMN description text",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_project DROP COLUMN detailed_description",
            reverse_sql="ALTER TABLE portfolio_project ADD COLUMN detailed_description text",
        ),
    ]
