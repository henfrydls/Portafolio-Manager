# -*- coding: utf-8 -*-
from django.db import migrations


TECHNOLOGY_REBUILD_SQLITE = """
CREATE TABLE IF NOT EXISTS portfolio_technology_new (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    identifier VARCHAR(60) NOT NULL UNIQUE,
    icon VARCHAR(50) NOT NULL DEFAULT '',
    color VARCHAR(7) NOT NULL DEFAULT '#000000'
);
INSERT INTO portfolio_technology_new (id, identifier, icon, color)
SELECT id,
       COALESCE(NULLIF(identifier, ''), 'technology-' || id),
       COALESCE(icon, ''),
       COALESCE(color, '#000000')
FROM portfolio_technology;
DROP TABLE portfolio_technology;
ALTER TABLE portfolio_technology_new RENAME TO portfolio_technology;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_technology_identifier_idx
    ON portfolio_technology(identifier);
"""

TECHNOLOGY_REBUILD_POSTGRES = """
CREATE TABLE IF NOT EXISTS portfolio_technology_new (
    id SERIAL PRIMARY KEY,
    identifier VARCHAR(60) NOT NULL UNIQUE,
    icon VARCHAR(50) NOT NULL DEFAULT '',
    color VARCHAR(7) NOT NULL DEFAULT '#000000'
);
INSERT INTO portfolio_technology_new (id, identifier, icon, color)
SELECT id,
       COALESCE(NULLIF(identifier, ''), 'technology-' || id),
       COALESCE(icon, ''),
       COALESCE(color, '#000000')
FROM portfolio_technology;
DROP TABLE portfolio_technology;
ALTER TABLE portfolio_technology_new RENAME TO portfolio_technology;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_technology_identifier_idx
    ON portfolio_technology(identifier);
SELECT setval(pg_get_serial_sequence('portfolio_technology', 'id'), COALESCE(MAX(id), 1), TRUE) FROM portfolio_technology;
"""

PROJECTTYPE_REBUILD_SQLITE = """
CREATE TABLE IF NOT EXISTS portfolio_projecttype_new (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    slug VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
INSERT INTO portfolio_projecttype_new (id, slug, is_active, "order", created_at, updated_at)
SELECT id,
       COALESCE(NULLIF(slug, ''), 'project-type-' || id),
       COALESCE(is_active, 1),
       COALESCE("order", 0),
       created_at,
       updated_at
FROM portfolio_projecttype;
DROP TABLE portfolio_projecttype;
ALTER TABLE portfolio_projecttype_new RENAME TO portfolio_projecttype;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_projecttype_slug_idx
    ON portfolio_projecttype(slug);
"""

PROJECTTYPE_REBUILD_POSTGRES = """
CREATE TABLE IF NOT EXISTS portfolio_projecttype_new (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
INSERT INTO portfolio_projecttype_new (id, slug, is_active, "order", created_at, updated_at)
SELECT id,
       COALESCE(NULLIF(slug, ''), 'project-type-' || id),
       COALESCE(is_active, TRUE),
       COALESCE("order", 0),
       created_at,
       updated_at
FROM portfolio_projecttype;
DROP TABLE portfolio_projecttype;
ALTER TABLE portfolio_projecttype_new RENAME TO portfolio_projecttype;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_projecttype_slug_idx
    ON portfolio_projecttype(slug);
SELECT setval(pg_get_serial_sequence('portfolio_projecttype', 'id'), COALESCE(MAX(id), 1), TRUE) FROM portfolio_projecttype;
"""

LANGUAGE_REBUILD_SQLITE = """
CREATE TABLE IF NOT EXISTS portfolio_language_new (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,
    proficiency VARCHAR(10) NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0
);
INSERT INTO portfolio_language_new (id, code, proficiency, "order")
SELECT id,
       COALESCE(NULLIF(code, ''), 'lang-' || id),
       COALESCE(proficiency, 'Native'),
       COALESCE("order", 0)
FROM portfolio_language;
DROP TABLE portfolio_language;
ALTER TABLE portfolio_language_new RENAME TO portfolio_language;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_language_code_idx
    ON portfolio_language(code);
"""

LANGUAGE_REBUILD_POSTGRES = """
CREATE TABLE IF NOT EXISTS portfolio_language_new (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    proficiency VARCHAR(10) NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0
);
INSERT INTO portfolio_language_new (id, code, proficiency, "order")
SELECT id,
       COALESCE(NULLIF(code, ''), 'lang-' || id),
       COALESCE(proficiency, 'Native'),
       COALESCE("order", 0)
FROM portfolio_language;
DROP TABLE portfolio_language;
ALTER TABLE portfolio_language_new RENAME TO portfolio_language;
CREATE UNIQUE INDEX IF NOT EXISTS portfolio_language_code_idx
    ON portfolio_language(code);
SELECT setval(pg_get_serial_sequence('portfolio_language', 'id'), COALESCE(MAX(id), 1), TRUE) FROM portfolio_language;
"""


def rebuild_tables(apps, schema_editor):
    """Run vendor-specific SQL to rebuild legacy tables with cleaned constraints."""
    vendor = schema_editor.connection.vendor
    # For PostgreSQL, skip the raw rebuild to avoid dropping FK-dependent tables.
    if vendor != 'sqlite':
        return

    # SQLite path (legacy cleanup)
    sql_blocks = [
        TECHNOLOGY_REBUILD_SQLITE,
        PROJECTTYPE_REBUILD_SQLITE,
        LANGUAGE_REBUILD_SQLITE,
    ]

    for block in sql_blocks:
        statements = [s.strip() for s in block.split(';') if s.strip()]
        for statement in statements:
            schema_editor.execute(statement)


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0023_translate_multilingual_models'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_tables,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelOptions(
                    name='technology',
                    options={
                        'ordering': ['translations__name'],
                        'verbose_name': 'Tecnologia',
                        'verbose_name_plural': 'Tecnologias',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
