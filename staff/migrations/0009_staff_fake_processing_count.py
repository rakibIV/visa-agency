from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_remove_staff_ranking_staff_monthly_rank_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='fake_processing_count',
            field=models.PositiveIntegerField(default=0, help_text='Manual/fake addition to lifetime processing visa count.'),
        ),
    ]
