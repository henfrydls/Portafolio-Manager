# -*- coding: utf-8 -*-
import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models


def copy_experience_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, company, position, description FROM portfolio_experience")
    rows = cursor.fetchall()
    ExperienceTranslation = apps.get_model('portfolio', 'ExperienceTranslation')
    for pk, company, position, description in rows:
        ExperienceTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            company=company or '',
            position=position or '',
            description=description or '',
        )


def copy_education_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, institution, degree, field_of_study, description FROM portfolio_education")
    rows = cursor.fetchall()
    EducationTranslation = apps.get_model('portfolio', 'EducationTranslation')
    for pk, institution, degree, field_of_study, description in rows:
        EducationTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            institution=institution or '',
            degree=degree or '',
            field_of_study=field_of_study or '',
            description=description or '',
        )


def copy_skill_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, name FROM portfolio_skill")
    rows = cursor.fetchall()
    SkillTranslation = apps.get_model('portfolio', 'SkillTranslation')
    for pk, name in rows:
        SkillTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            name=name or '',
        )


def copy_category_translations(apps, schema_editor):
    cursor = schema_editor.connection.cursor()
    cursor.execute("SELECT id, name, description FROM portfolio_category")
    rows = cursor.fetchall()
    CategoryTranslation = apps.get_model('portfolio', 'CategoryTranslation')
    for pk, name, description in rows:
        CategoryTranslation.objects.using(schema_editor.connection.alias).create(
            master_id=pk,
            language_code='en',
            name=name or '',
            description=description or '',
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0020_remove_blogpost_content_remove_blogpost_excerpt_and_more'),
    ]

    operations = [
        # Experience
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Experience'),
                migrations.CreateModel(
                    name='Experience',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('start_date', models.DateField(verbose_name='Fecha de inicio')),
                        ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                        ('current', models.BooleanField(default=False, verbose_name='Trabajo actual')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Orden de visualizacion')),
                    ],
                    options={
                        'verbose_name': 'Experiencia',
                        'verbose_name_plural': 'Experiencias',
                        'ordering': ['-start_date', 'order'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[('objects', parler.models.TranslatableManager())],
                ),
            ],
        ),
        migrations.CreateModel(
            name='ExperienceTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('company', models.CharField(max_length=200, verbose_name='Empresa')),
                ('position', models.CharField(max_length=200, verbose_name='Posicion')),
                ('description', models.TextField(verbose_name='Descripcion del trabajo')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.experience')),
            ],
            options={
                'verbose_name': 'Experiencia Translation',
                'db_table': 'portfolio_experience_translation',
                'default_permissions': (),
                'managed': True,
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_experience_translations, noop),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_experience DROP COLUMN company",
            reverse_sql="ALTER TABLE portfolio_experience ADD COLUMN company varchar(200)"
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_experience DROP COLUMN position",
            reverse_sql="ALTER TABLE portfolio_experience ADD COLUMN position varchar(200)"
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_experience DROP COLUMN description",
            reverse_sql="ALTER TABLE portfolio_experience ADD COLUMN description text"
        ),

        # Education
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Education'),
                migrations.CreateModel(
                    name='Education',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('education_type', models.CharField(choices=[('formal', 'Educacion Formal'), ('online_course', 'Curso Online'), ('certification', 'Certificacion'), ('bootcamp', 'Bootcamp'), ('workshop', 'Taller/Workshop')], default='formal', max_length=20, verbose_name='Tipo de educacion')),
                        ('start_date', models.DateField(verbose_name='Fecha de inicio')),
                        ('end_date', models.DateField(blank=True, null=True, verbose_name='Fecha de fin')),
                        ('current', models.BooleanField(default=False, verbose_name='En curso')),
                        ('credential_id', models.CharField(blank=True, max_length=100, verbose_name='ID del certificado')),
                        ('credential_url', models.URLField(blank=True, verbose_name='URL de verificacion')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Orden de visualizacion')),
                    ],
                    options={
                        'verbose_name': 'Educacion',
                        'verbose_name_plural': 'Educacion',
                        'ordering': ['-end_date', '-start_date'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[('objects', parler.models.TranslatableManager())],
                ),
            ],
        ),
        migrations.CreateModel(
            name='EducationTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('institution', models.CharField(max_length=200, verbose_name='Institucion')),
                ('degree', models.CharField(max_length=200, verbose_name='Titulo/Certificacion')),
                ('field_of_study', models.CharField(max_length=200, verbose_name='Campo de estudio')),
                ('description', models.TextField(blank=True, verbose_name='Descripcion')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.education')),
            ],
            options={
                'verbose_name': 'Educacion Translation',
                'db_table': 'portfolio_education_translation',
                'default_permissions': (),
                'managed': True,
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_education_translations, noop),
        migrations.RunSQL("ALTER TABLE portfolio_education DROP COLUMN institution",
                          reverse_sql="ALTER TABLE portfolio_education ADD COLUMN institution varchar(200)"),
        migrations.RunSQL("ALTER TABLE portfolio_education DROP COLUMN degree",
                          reverse_sql="ALTER TABLE portfolio_education ADD COLUMN degree varchar(200)"),
        migrations.RunSQL("ALTER TABLE portfolio_education DROP COLUMN field_of_study",
                          reverse_sql="ALTER TABLE portfolio_education ADD COLUMN field_of_study varchar(200)"),
        migrations.RunSQL("ALTER TABLE portfolio_education DROP COLUMN description",
                          reverse_sql="ALTER TABLE portfolio_education ADD COLUMN description text"),

        # Skill
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Skill'),
                migrations.CreateModel(
                    name='Skill',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('proficiency', models.IntegerField(choices=[(1, 'Basico'), (2, 'Intermedio'), (3, 'Avanzado'), (4, 'Experto')], verbose_name='Nivel de competencia')),
                        ('years_experience', models.PositiveIntegerField(verbose_name='Anios de experiencia')),
                        ('category', models.CharField(help_text='Ej: Programming, Cloud, Business, Methodologies, etc.', max_length=100, verbose_name='Categoria')),
                    ],
                    options={
                        'verbose_name': 'Habilidad',
                        'verbose_name_plural': 'Habilidades',
                        'ordering': ['category', '-proficiency', 'translations__name'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[('objects', parler.models.TranslatableManager())],
                ),
            ],
        ),
        migrations.CreateModel(
            name='SkillTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre de la habilidad')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.skill')),
            ],
            options={
                'verbose_name': 'Habilidad Translation',
                'db_table': 'portfolio_skill_translation',
                'default_permissions': (),
                'managed': True,
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_skill_translations, noop),
        migrations.RunSQL("ALTER TABLE portfolio_skill DROP COLUMN name",
                          reverse_sql="ALTER TABLE portfolio_skill ADD COLUMN name varchar(100)"),

        # Category
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='Category'),
                migrations.CreateModel(
                    name='Category',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Categoria',
                        'verbose_name_plural': 'Categorias',
                        'ordering': ['order', 'translations__name'],
                    },
                    bases=(parler.models.TranslatableModel,),
                    managers=[('objects', parler.models.TranslatableManager())],
                ),
            ],
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, verbose_name='Descripcion')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.category')),
            ],
            options={
                'verbose_name': 'Categoria Translation',
                'db_table': 'portfolio_category_translation',
                'default_permissions': (),
                'managed': True,
                'unique_together': {('language_code', 'master')},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_category_translations, noop),    ]
