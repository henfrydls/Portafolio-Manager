# -*- coding: utf-8 -*-
from django.db import migrations


CATEGORY_REBUILD = """
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


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0028_alter_profile_email_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CATEGORY_REBUILD,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
