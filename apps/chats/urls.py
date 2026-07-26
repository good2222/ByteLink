from django.urls import path
from .views import ChatListView, StartChatView, ChatDetailView

urlpatterns = [
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/start/<str:username>/', StartChatView.as_view(), name='start_chat'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat_detail'),
]
