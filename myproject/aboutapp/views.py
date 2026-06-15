from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import About
from .serializers import AboutSerializer

class AboutView(generics.RetrieveAPIView):
    queryset = About.objects.all()
    serializer_class = AboutSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        # Якщо запису немає – створити порожній (або повернути 404)
        obj, created = About.objects.get_or_create(id=1)
        return obj