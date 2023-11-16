from django.db import models


class UserModel(models.Model):
    userId = models.CharField(max_length=50)
    orgId = models.CharField(max_length=50)
    email = models.EmailField()
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    # Metadata as a JSON field
    metadata = models.JSONField()

    class Meta:
        app_label = 'ChatExplorerApp'  # Specify the app label

    def __str__(self):
        return self.email  # Return the email as the model's string representation
