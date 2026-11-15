from django.db import migrations

from portfolio.migration_utils import add_column_if_missing, drop_column_if_exists

# Legacy columns whose content lives in the translation tables. PostgreSQL
# kept them; the SQLite rebuilds in 0024 already dropped them.
LEGACY_COLUMNS = (
    ('portfolio_language', 'name', 'varchar(100)'),
    ('portfolio_knowledgebase', 'name', 'varchar(100)'),
    ('portfolio_projecttype', 'name', 'varchar(100)'),
    ('portfolio_projecttype', 'description', 'text'),
)


def drop_legacy_columns(apps, schema_editor):
    for table, column, _sql_type in LEGACY_COLUMNS:
        drop_column_if_exists(schema_editor, table, column)


def restore_legacy_columns(apps, schema_editor):
    for table, column, sql_type in LEGACY_COLUMNS:
        add_column_if_missing(schema_editor, table, column, sql_type)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0033_create_default_project_types'),
    ]

    operations = [
        # Was RunSQL with DROP COLUMN IF EXISTS, which SQLite does not accept
        migrations.RunPython(drop_legacy_columns, restore_legacy_columns),
    ]
