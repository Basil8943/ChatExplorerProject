from django.db import models


class CommentModel(models.Model):
    comment = models.CharField(max_length=100)
    session_id = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    commented_user_id = models.IntegerField()

