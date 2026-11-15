"""
Helpers for data migrations that write with raw SQL.

Several tables kept legacy columns (`name`, `description`) on PostgreSQL
after their content moved to the translation tables, while the SQLite
rebuild dropped them. Raw SQL written for one schema fails on the other,
so these helpers look at the table before writing to it.

This module lives outside `migrations/` because Django treats every module
in that package as a migration.
"""
from django.utils import timezone


def table_columns(connection, table):
    """Names of the columns `table` has right now."""
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table)
    return {column.name for column in description}


def insert_row(connection, table, values, legacy_values=None, timestamps=False):
    """
    Insert one row.

    `legacy_values` are written only to the columns that still exist.
    `timestamps` fills `created_at` and `updated_at`, which the model sets
    in Python and the database has no default for.
    """
    row = dict(values)
    if legacy_values:
        existing = table_columns(connection, table)
        row.update({name: value for name, value in legacy_values.items() if name in existing})
    if timestamps:
        now = timezone.now()
        row.update(created_at=now, updated_at=now)

    quote = connection.ops.quote_name
    columns = ', '.join(quote(name) for name in row)
    placeholders = ', '.join(['%s'] * len(row))
    with connection.cursor() as cursor:
        cursor.execute(
            f'INSERT INTO {quote(table)} ({columns}) VALUES ({placeholders})',
            list(row.values()),
        )


def drop_column_if_exists(schema_editor, table, column):
    """`ALTER TABLE … DROP COLUMN IF EXISTS`, which only PostgreSQL has."""
    connection = schema_editor.connection
    if column in table_columns(connection, table):
        quote = connection.ops.quote_name
        schema_editor.execute(f'ALTER TABLE {quote(table)} DROP COLUMN {quote(column)}')


def add_column_if_missing(schema_editor, table, column, sql_type):
    """Reverse of drop_column_if_exists: the column comes back empty and nullable."""
    connection = schema_editor.connection
    if column not in table_columns(connection, table):
        quote = connection.ops.quote_name
        schema_editor.execute(
            f'ALTER TABLE {quote(table)} ADD COLUMN {quote(column)} {sql_type} NULL')
