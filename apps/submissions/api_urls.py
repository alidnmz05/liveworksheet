from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, permissions, serializers
from .models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'worksheet', 'assignment', 'submitted_at', 'score',
                  'total_questions', 'correct_count', 'is_graded')


class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user)


router = DefaultRouter()
router.register('', SubmissionViewSet, basename='submission-api')

urlpatterns = router.urls
