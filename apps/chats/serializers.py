from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.chats.models import ChatRoom, ChatMessage

User = get_user_model()


class ChatUserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.CharField(source='get_avatar_url', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url']


class MessageSerializer(serializers.ModelSerializer):
    sender = ChatUserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField(read_only=True)
    last_message = MessageSerializer(read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'other_user', 'last_message', 'created_at']

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other = obj.get_other_user(request.user)
            if other:
                return ChatUserSerializer(other).data
        return None