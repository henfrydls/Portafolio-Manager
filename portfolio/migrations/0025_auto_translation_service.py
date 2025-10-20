from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('portfolio', '0024_cleanup_legacy_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='translation_timeout',
            field=models.PositiveIntegerField(default=10, verbose_name='Tiempo de espera (segundos)'),
        ),
        migrations.CreateModel(
            name='AutoTranslationRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('language_code', models.CharField(max_length=10)),
                ('source_language', models.CharField(max_length=10)),
                ('provider', models.CharField(blank=True, max_length=50)),
                ('duration_ms', models.PositiveIntegerField(default=0)),
                ('auto_generated', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('success', 'Completado'), ('failed', 'Fallido')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Registro de traducción automática',
                'verbose_name_plural': 'Registros de traducción automática',
                'ordering': ['-updated_at'],
                'unique_together': {('content_type', 'object_id', 'language_code')},
            },
        ),
    ]
