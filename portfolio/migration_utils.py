"""
Helper for data migrations that write with raw SQL.

Several tables kept legacy columns (`name`, `description`) on PostgreSQL
after their content moved to the translation tables, while the SQLite
rebuild dropped them. Raw SQL written for one schema fails on the other,
so callers look at the table first and pick the statement that fits.

This module lives outside `migrations/` because Django treats every module
in that package as a migration.
"""


def table_columns(connection, table):
    """Names of the columns `table` has right now."""
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table)
    return {column.name for column in description}
