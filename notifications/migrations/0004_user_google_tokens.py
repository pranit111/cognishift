# Generated manually - Google Calendar OAuth token fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_phoneotp_user_phone_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='google_access_token',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='user',
            name='google_refresh_token',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='user',
            name='google_token_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
