from rest_framework import serializers
from ChatExplorerApp.Models.chatmodel import ChatModel
from ChatExplorerApp.Models.usermodel import UserModel


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