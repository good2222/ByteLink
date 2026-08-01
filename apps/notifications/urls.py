from django.urls import path
from .views import NotificationListView, MarkAllReadView

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification_list'),
    path('notifications/read-all/', MarkAllReadView.as_view(), name='mark_all_read'),
]