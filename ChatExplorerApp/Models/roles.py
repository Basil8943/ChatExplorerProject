from django.db import models

class RoleModel(models.Model):
    rollname = models.CharField(max_length=50)
    # other fields in the Roles model

    def __str__(self):
        return self.rollname

    class Meta:
        app_label = 'ChatExplorerApp'

class UserRoleModel(models.Model):
    user_id = models.IntegerField()
    rolltype_id = models.IntegerField()

    def __str__(self):
        return self.id  

    class Meta:
        app_label = 'ChatExplorerApp'