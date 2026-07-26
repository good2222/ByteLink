# ============================================================
# ФАЙЛ: apps/chats/views.py
# Обработчики страниц мессенджера
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import ChatRoom, ChatMessage

# Получаем активную модель пользователя
User = get_user_model()


# ============================================================
# VIEW: ChatListView — Список всех диалогов
# ============================================================
class ChatListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chats/chat_list.html'
    context_object_name = 'chat_rooms'

    def get_queryset(self):
        # Возвращаем только диалоги текущего пользователя
        return self.request.user.chat_rooms.all()


# ============================================================
# VIEW: StartChatView — Начать диалог с пользователем
# ============================================================
class StartChatView(LoginRequiredMixin, View):
    def get(self, request, username):
        # Получаем пользователя-собеседника по username
        other_user = get_object_or_404(User, username=username)

        # Нельзя начать переписку с самим собой
        if other_user == request.user:
            return redirect('chat_list')

        # Ищем существующий диалог между текущим пользователем и собеседником
        chat_room = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()

        # Если диалога еще нет — создаем новый и добавляем обоих участников
        if not chat_room:
            chat_room = ChatRoom.objects.create()
            chat_room.participants.add(request.user, other_user)

        # Перенаправляем на страницу открытого диалога
        return redirect('chat_detail', pk=chat_room.pk)


# ============================================================
# VIEW: ChatDetailView — Окно активного чата
# ============================================================
class ChatDetailView(LoginRequiredMixin, DetailView):
    model = ChatRoom
    template_name = 'chats/chat_detail.html'
    context_object_name = 'chat_room'

    def get_object(self, queryset=None):
        # Проверяем, что запрашиваемый чат действительно принадлежит пользователю (защита от взлома)
        return get_object_or_404(ChatRoom, pk=self.kwargs['pk'], participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Все диалоги для левого меню
        context['chat_rooms'] = self.request.user.chat_rooms.all()
        # Собеседник текущего чата
        context['other_user'] = self.object.get_other_user(self.request.user)
        return context
