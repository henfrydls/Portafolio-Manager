# -*- coding: utf-8 -*-
import django.db.models.deletion
import parler.fields
import parler.models
from django.db import migrations, models
from django.utils.text import slugify


def copy_technology_translations(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM portfolio_technology")
    rows = cursor.fetchall()

    existing_identifiers = set()
    TechnologyTranslation = apps.get_model('portfolio', 'TechnologyTranslation')

    for tech_id, name in rows:
        name = name or ''
        base_slug = slugify(name) or f"technology-{tech_id}"
        slug = base_slug
        counter = 1
        while slug in existing_identifiers:
            counter += 1
            slug = f"{base_slug}-{counter}"
        existing_identifiers.add(slug)

        cursor.execute(
            "UPDATE portfolio_technology SET identifier = %s WHERE id = %s",
            [slug, tech_id]
        )
        TechnologyTranslation.objects.using(connection.alias).create(
            master_id=tech_id,
            language_code='en',
            name=name
        )


def copy_projecttype_translations(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, description FROM portfolio_projecttype")
    rows = cursor.fetchall()

    ProjectTypeTranslation = apps.get_model('portfolio', 'ProjectTypeTranslation')
    for pk, name, description in rows:
        ProjectTypeTranslation.objects.using(connection.alias).create(
            master_id=pk,
            language_code='en',
            name=name or '',
            description=description or ''
        )


def copy_language_translations(apps, schema_editor):
    connection = schema_editor.connection
    cursor = connection.cursor()
    cursor.execute("SELECT id, name FROM portfolio_language")
    rows = cursor.fetchall()

    existing_codes = set()
    LanguageTranslation = apps.get_model('portfolio', 'LanguageTranslation')

    for pk, name in rows:
        name = name or ''
        base_code = slugify(name) or f"lang-{pk}"
        code = base_code
        counter = 1
        while code in existing_codes:
            counter += 1
            code = f"{base_code}-{counter}"
        existing_codes.add(code)

        cursor.execute(
            "UPDATE portfolio_language SET code = %s WHERE id = %s",
            [code, pk]
        )
        LanguageTranslation.objects.using(connection.alias).create(
            master_id=pk,
            language_code='en',
            name=name
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0022_alter_blogpost_managers_alter_category_managers_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Technology'),
                migrations.CreateModel(
                    name='Technology',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('identifier', models.CharField(help_text='Identificador estable (en ingles) utilizado como clave interna.', max_length=60, unique=True, verbose_name='Identificador')),
                        ('icon', models.CharField(blank=True, help_text=(
                                "Clase CSS para mostrar el icono. Ejemplos comunes:<br>"
                                "- Python: <code>fab fa-python</code><br>"
                                "- JavaScript: <code>fab fa-js-square</code><br>"
                                "- React: <code>fab fa-react</code><br>"
                                "- Docker: <code>fab fa-docker</code><br>"
                                "- HTML: <code>fab fa-html5</code><br>"
                                "- CSS: <code>fab fa-css3-alt</code><br>"
                                "- Node.js: <code>fab fa-node-js</code><br>"
                                "- Git: <code>fab fa-git-alt</code><br>"
                                "- AWS: <code>fab fa-aws</code><br>"
                                "- Linux: <code>fab fa-linux</code><br><br>"
                                "<strong>Mas iconos disponibles en:</strong><br>"
                                "<a href='https://fontawesome.com/icons' target='_blank'>Font Awesome Icons</a><br>"
                                "<a href='https://devicon.dev/' target='_blank'>Devicon (iconos para desarrollo)</a><br>"
                                "<a href='https://simpleicons.org/' target='_blank'>Simple Icons</a>"
                            ), max_length=50, verbose_name='Clase CSS del icono')),
                        ('color', models.CharField(default='#000000', help_text=(
                                   "Color en formato hexadecimal. Ejemplos de colores oficiales:<br>"
                                   "- Python: <code>#3776ab</code><br>"
                                   "- JavaScript: <code>#f7df1e</code><br>"
                                   "- React: <code>#61dafb</code><br>"
                                   "- Django: <code>#092e20</code><br>"
                                   "- Docker: <code>#2496ed</code><br>"
                                   "- Git: <code>#f05032</code><br>"
                                   "- AWS: <code>#ff9900</code><br>"
                                   "- PostgreSQL: <code>#336791</code>"
                               ), max_length=7, verbose_name='Color')),
                    ],
                    options={
                        'ordering': ['translations__name'],
                        'verbose_name': 'Tecnologia',
                        'verbose_name_plural': 'Tecnologias',
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
            ],
            database_operations=[],
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_technology ADD COLUMN identifier varchar(60)",
            reverse_sql="ALTER TABLE portfolio_technology DROP COLUMN identifier",
        ),
        migrations.CreateModel(
            name='TechnologyTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.technology')),
            ],
            options={
                'verbose_name': 'Tecnologia Translation',
                'db_table': 'portfolio_technology_translation',
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
                'managed': True,
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_technology_translations, noop),
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX IF NOT EXISTS portfolio_technology_identifier_idx ON portfolio_technology(identifier)",
            reverse_sql="DROP INDEX IF EXISTS portfolio_technology_identifier_idx",
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='ProjectType'),
                migrations.CreateModel(
                    name='ProjectType',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                        ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'ordering': ['order', 'translations__name'],
                        'verbose_name': 'Tipo de Proyecto',
                        'verbose_name_plural': 'Tipos de Proyectos',
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name='ProjectTypeTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('description', models.TextField(blank=True, verbose_name='Descripcion')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.projecttype')),
            ],
            options={
                'verbose_name': 'Tipo de Proyecto Translation',
                'db_table': 'portfolio_projecttype_translation',
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
                'managed': True,
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_projecttype_translations, noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Language'),
                migrations.CreateModel(
                    name='Language',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('code', models.CharField(help_text='Identificador interno del idioma (en, es, fr, etc.)', max_length=20, unique=True, verbose_name='Codigo')),
                        ('proficiency', models.CharField(choices=[('A1', 'A1 - Beginner'), ('A2', 'A2 - Elementary'), ('B1', 'B1 - Intermediate'), ('B2', 'B2 - Upper Intermediate'), ('C1', 'C1 - Advanced'), ('C2', 'C2 - Proficient'), ('Native', 'Native')], max_length=10, verbose_name='Nivel de dominio')),
                        ('order', models.PositiveIntegerField(default=0, help_text='Orden en que aparecera en el CV', verbose_name='Orden de visualizacion')),
                    ],
                    options={
                        'ordering': ['order', 'translations__name'],
                        'verbose_name': 'Idioma',
                        'verbose_name_plural': 'Idiomas',
                    },
                    bases=(parler.models.TranslatableModel,),
                ),
            ],
            database_operations=[],
        ),
        migrations.RunSQL(
            sql="ALTER TABLE portfolio_language ADD COLUMN code varchar(20)",
            reverse_sql="ALTER TABLE portfolio_language DROP COLUMN code",
        ),
        migrations.CreateModel(
            name='LanguageTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(help_text='Ej: English, Espanol, Francais', max_length=50, verbose_name='Idioma')),
                ('master', parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='portfolio.language')),
            ],
            options={
                'verbose_name': 'Idioma Translation',
                'db_table': 'portfolio_language_translation',
                'default_permissions': (),
                'unique_together': {('language_code', 'master')},
                'managed': True,
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.RunPython(copy_language_translations, noop),
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX IF NOT EXISTS portfolio_language_code_idx ON portfolio_language(code)",
            reverse_sql="DROP INDEX IF EXISTS portfolio_language_code_idx",
        ),
    ]
