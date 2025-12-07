from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0033_create_default_project_types'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE portfolio_language DROP COLUMN IF EXISTS name;
            ALTER TABLE portfolio_knowledgebase DROP COLUMN IF EXISTS name;
            ALTER TABLE portfolio_projecttype DROP COLUMN IF EXISTS name;
            ALTER TABLE portfolio_projecttype DROP COLUMN IF EXISTS description;
            """,
            reverse_sql="""
            ALTER TABLE portfolio_language ADD COLUMN IF NOT EXISTS name varchar(100) NULL;
            ALTER TABLE portfolio_knowledgebase ADD COLUMN IF NOT EXISTS name varchar(100) NULL;
            ALTER TABLE portfolio_projecttype ADD COLUMN IF NOT EXISTS name varchar(100) NULL;
            ALTER TABLE portfolio_projecttype ADD COLUMN IF NOT EXISTS description text NULL;
            """
        ),
    ]
