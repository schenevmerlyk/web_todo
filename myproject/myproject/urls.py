from django.urls import path
from .views import TodoListCreateView, TodoDetailView
from django.urls import path, include  

urlpatterns = [
    path('', TodoListCreateView.as_view(), name='todo-list'),
    path('<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),
    path('api/todo/', include('todo.urls')),
    path('api/users/', include('users.urls')),
    path('api/about/', include('aboutapp.urls')),
    path('api/realtime/', include('realtime.urls')),
    path('api/todo/', include('todo.urls')),
]