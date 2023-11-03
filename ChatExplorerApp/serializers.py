from rest_framework import serializers
from ChatExplorerApp.Models.chatmodel import ChatModel
from ChatExplorerApp.Models.commentmodel import CommentModel
from ChatExplorerApp.Models.usermodel import UserModel
from django.contrib.auth.models import User


class ChatModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatModel
        fields = '__all__'         
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)  
        try:
            user = UserModel.objects.get(userId=instance.userId)
            representation['user_name'] = user.firstName + " " +user.lastName   
        except UserModel.DoesNotExist:
            if instance.userId == "taiwa-bot":
                representation['user_name'] = "taiwa-bot"
            else:
                representation['user_name'] = ""

        return representation
    
class CommentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['id','comment', 'session_id', 'user_id' ,'response']




    def to_representation(self, instance):
        representation = super().to_representation(instance)  
        try:
            user = User.objects.get(id=instance.commented_user_id)
            representation['user_name'] = user.username   
        except UserModel.DoesNotExist:
            if instance.userId == "taiwa-bot":
                representation['user_name'] = "taiwa-bot"
            else:
                representation['user_name'] = ""

        return representation