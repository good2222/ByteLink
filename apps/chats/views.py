from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import ChatRoom, ChatMessage

User = get_user_model()


# 1. Список всех моих чатов
class ChatListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chats/chat_list.html'
    context_object_name = 'chat_rooms'

    def get_queryset(self):
        # Возвращает только те чаты, где состоит текущий пользователь
        return self.request.user.chat_rooms.all()


# 2. Начать чат с пользователем (по его username или ID)
class StartChatView(LoginRequiredMixin, View):
    def get(self, request, username):
        other_user = get_object_or_404(User, username=username)
        if other_user == request.user:
            return redirect('chat_list')

        # Ищем существующий диалог между двумя пользователями
        chat_room = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()

        # Если диалога еще нет — создаем новый
        if not chat_room:
            chat_room = ChatRoom.objects.create()
            chat_room.participants.add(request.user, other_user)

        # Перенаправляем на страницу этого диалога
        return redirect('chat_detail', pk=chat_room.pk)


# 3. Страница конкретного диалога
class ChatDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chats/chat_detail.html'
    context_object_name = 'chat_room'

    def get_object(self, queryset=None):
        # Проверяем, что текущий пользователь действительно участник этого чата!
        return get_object_or_404(ChatRoom, pk=self.kwargs['pk'], participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем список всех ваших диалогов для бокового меню слева
        context['chat_rooms'] = self.request.user.chat_rooms.all()
        # Передаем вашего собеседника
        context['other_user'] = self.object.get_other_user(self.request.user)
        return context