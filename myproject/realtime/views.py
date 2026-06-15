from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .consumers import online_users
from users.models import User
from users.serializers import UserProfileSerializer

class OnlineUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users_online = User.objects.filter(id__in=online_users)
        serializer = UserProfileSerializer(users_online, many=True)
        return Response(serializer.data)