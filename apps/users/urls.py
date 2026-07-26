from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    RegisterView, ProfileView, ProfileEditView,
    SendFriendRequestView, AcceptFriendRequestView,
    DeclineFriendRequestView, RemoveFriendView,
    FriendsListView, FriendRequestsView,
    UserSearchView,
)

urlpatterns = [
    # Авторизация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/',   auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Профиль
    path('profile/edit/',          ProfileEditView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', ProfileView.as_view(),    name='profile'),

    # Друзья
    path('friends/',                               FriendsListView.as_view(),       name='my_friends'),
    path('profile/<str:username>/friends/',        FriendsListView.as_view(),       name='friends_list'),
    path('profile/<str:username>/add-friend/',     SendFriendRequestView.as_view(), name='send_friend_request'),
    path('profile/<str:username>/remove-friend/',  RemoveFriendView.as_view(),      name='remove_friend'),
    path('friend-requests/',                       FriendRequestsView.as_view(),    name='friend_requests'),
    path('friend-requests/<int:pk>/accept/',       AcceptFriendRequestView.as_view(), name='accept_friend_request'),
    path('friend-requests/<int:pk>/decline/',      DeclineFriendRequestView.as_view(), name='decline_friend_request'),

    # Поиск
    path('search/', UserSearchView.as_view(), name='user_search'),
]
