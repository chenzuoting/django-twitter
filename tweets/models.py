from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now


class Tweet(models.Model):
    # Only use on_delete=models.SET_NULL on foreign key
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='User that posts this tweet',
    )
    content = models.CharField(max_length=255)
    # auto_now_add: automatically update this field on creation
    created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Add composite index
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now do not have timezone info, so use utc_now() to replace to UTC
        # return (datetime.now() - self.created_at).seconds // 3600
        return (utc_now() - self.created_at).total_seconds() // 3600

    def __str__(self):
        # For print(tweet instance)
        return f'{self.created_at} {self.user}: {self.content}'