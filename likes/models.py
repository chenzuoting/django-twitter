from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    # https://docs.djangoproject.com/en/3.1/ref/contrib/contenttypes/#generic-relations
    # comment id or tweet id
    object_id = models.PositiveIntegerField()
    # Refer to all models
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
    )
    # user liked content_object at created_at
    # like.content_object will take in content_type and object_id, return comment or tweet
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This will create <user, content_type, object_id>, we can use to get
        # all the likes from one user. We will not have this function if we do
        # <content_type, object_id, user>
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (
            # Get all likes for one content_object and order by created time
            ('content_type', 'object_id', 'created_at'),
            # Get all likes from one user and order by created time
            ('user', 'content_type', 'created_at'),
        )

    def __str__(self):
        return '{} - {} liked {} {}'.format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,
        )
