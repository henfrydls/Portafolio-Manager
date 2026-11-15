from django.db import migrations

from portfolio.migration_utils import table_columns

# Legacy columns whose content lives in the translation tables. PostgreSQL
# kept them; the SQLite rebuilds already dropped them. The statements are
# written out because DROP COLUMN IF EXISTS is PostgreSQL only.
LEGACY_COLUMNS = (
    (
        'portfolio_language', 'name',
        'ALTER TABLE portfolio_language DROP COLUMN name',
        'ALTER TABLE portfolio_language ADD COLUMN name varchar(100) NULL',
    ),
    (
        'portfolio_knowledgebase', 'name',
        'ALTER TABLE portfolio_knowledgebase DROP COLUMN name',
        'ALTER TABLE portfolio_knowledgebase ADD COLUMN name varchar(100) NULL',
    ),
    (
        'portfolio_projecttype', 'name',
        'ALTER TABLE portfolio_projecttype DROP COLUMN name',
        'ALTER TABLE portfolio_projecttype ADD COLUMN name varchar(100) NULL',
    ),
    (
        'portfolio_projecttype', 'description',
        'ALTER TABLE portfolio_projecttype DROP COLUMN description',
        'ALTER TABLE portfolio_projecttype ADD COLUMN description text NULL',
    ),
)


def drop_legacy_columns(apps, schema_editor):
    for table, column, drop_sql, _add_sql in LEGACY_COLUMNS:
        if column in table_columns(schema_editor.connection, table):
            schema_editor.execute(drop_sql)


def restore_legacy_columns(apps, schema_editor):
    for table, column, _drop_sql, add_sql in LEGACY_COLUMNS:
        if column not in table_columns(schema_editor.connection, table):
            schema_editor.execute(add_sql)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0033_create_default_project_types'),
    ]

    operations = [
        # Was RunSQL with DROP COLUMN IF EXISTS, which SQLite does not accept
        migrations.RunPython(drop_legacy_columns, restore_legacy_columns),
    ]
