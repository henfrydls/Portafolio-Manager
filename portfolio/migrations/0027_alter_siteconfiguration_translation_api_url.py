from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0026_alter_siteconfiguration_translation_api_key_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteconfiguration',
            name='translation_api_url',
            field=models.CharField(blank=True, default='http://libretranslate:5000', max_length=255, verbose_name='Translation service URL'),
        ),
    ]
