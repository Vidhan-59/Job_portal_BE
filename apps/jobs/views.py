from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from apps.core.permissions import IsRecruitingHR
from .models import Job
from .serializers import JobSerializer

User = get_user_model()

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'experience_level', 'status', 'location']
    search_fields = ['title', 'company_name', 'skills_required']
    ordering_fields = ['created_at', 'salary_min', 'salary_max']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            # Students can only see active jobs
            return Job.objects.filter(status='active')
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            # HR users can only see jobs they created
            return Job.objects.filter(posted_by=user)
        else:
            # Other roles (if any) see no jobs
            return Job.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsRecruitingHR()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'student':
            # Students can only see active jobs
            return Job.objects.filter(status='active')
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            # HR users can only see jobs they created
            return Job.objects.filter(posted_by=user , status='active')
        else:
            # Other roles (if any) see no jobs
            return Job.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsRecruitingHR])
def close_job(request, pk):
    try:
        job = Job.objects.get(pk=pk, posted_by=request.user)
        job.status = 'closed'
        job.save()
        return Response({'message': 'Job closed successfully'})
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsRecruitingHR])
def hr_team_members(request):
    hr_members = User.objects.filter(role__in=['recruiting_hr', 'hr_team_member', 'main_hr'])
    data = [{'id': user.id, 'name': f"{user.first_name} {user.last_name}"} 
            for user in hr_members]
    return Response(data)