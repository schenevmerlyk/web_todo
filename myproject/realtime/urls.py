from django.urls import path
from .views import OnlineUsersView

urlpatterns = [
    path('online-users/', OnlineUsersView.as_view(), name='online-users'),
]