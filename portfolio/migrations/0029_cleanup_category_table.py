# -*- coding: utf-8 -*-
from django.db import migrations


CATEGORY_REBUILD_SQLITE = """
CREATE TABLE IF NOT EXISTS portfolio_category_new (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    slug VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
INSERT INTO portfolio_category_new (id, slug, is_active, "order", created_at, updated_at)
SELECT id,
       COALESCE(NULLIF(slug, ''), 'category-' || id),
       COALESCE(is_active, 1),
       COALESCE("order", 0),
       COALESCE(created_at, datetime('now')),
       COALESCE(updated_at, datetime('now'))
FROM portfolio_category;
DROP TABLE portfolio_category;
ALTER TABLE portfolio_category_new RENAME TO portfolio_category;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_category_slug_idx
    ON portfolio_category(slug);
"""

CATEGORY_REBUILD_POSTGRES = """
CREATE TABLE IF NOT EXISTS portfolio_category_new (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
INSERT INTO portfolio_category_new (id, slug, is_active, "order", created_at, updated_at)
SELECT id,
       COALESCE(NULLIF(slug, ''), 'category-' || id),
       COALESCE(is_active, TRUE),
       COALESCE("order", 0),
       COALESCE(created_at, NOW()),
       COALESCE(updated_at, NOW())
FROM portfolio_category;
DROP TABLE portfolio_category;
ALTER TABLE portfolio_category_new RENAME TO portfolio_category;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_category_slug_idx
    ON portfolio_category(slug);
SELECT setval(pg_get_serial_sequence('portfolio_category', 'id'), COALESCE(MAX(id), 1), TRUE) FROM portfolio_category;
"""


def rebuild_category_table(apps, schema_editor):
    """Run vendor-specific SQL to rebuild category table with cleaned constraints."""
    vendor = schema_editor.connection.vendor
    # For PostgreSQL, skip the raw rebuild to avoid dropping FK-dependent tables.
    if vendor != 'sqlite':
        return

    # SQLite path (legacy cleanup)
    sql_block = CATEGORY_REBUILD_SQLITE

    statements = [s.strip() for s in sql_block.split(';') if s.strip()]
    for statement in statements:
        schema_editor.execute(statement)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0028_alter_profile_email_and_more'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_category_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
