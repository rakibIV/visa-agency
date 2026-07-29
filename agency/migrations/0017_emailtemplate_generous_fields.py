from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0016_companyinformation_manual_approved_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplate',
            name='is_generous',
            field=models.BooleanField(default=False, help_text='Flag for generous email template with simple layout.'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='top_left_logo',
            field=models.CharField(blank=True, default='', help_text='Optional logo URL or choice for top left.', max_length=500),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='top_center_logo',
            field=models.CharField(blank=True, default='', help_text='Optional logo URL or choice for top center.', max_length=500),
        ),
    ]
