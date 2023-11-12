from django.contrib.auth import get_user_model
from django.db import models

from images.models import Image

User = get_user_model()


class Comment(models.Model):
    commented_post = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    commentator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='my_comments',
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return (f'Comment by {self.commentator.get_username()} on '
                f'{self.commented_post.name}')
