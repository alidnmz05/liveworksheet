from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, permissions
from .models import Worksheet
from .serializers import WorksheetSerializer


class WorksheetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorksheetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if 'public' in self.request.query_params:
            return Worksheet.objects.filter(is_public=True)
        return Worksheet.objects.filter(author=user)


router = DefaultRouter()
router.register('', WorksheetViewSet, basename='worksheet-api')

urlpatterns = router.urls
