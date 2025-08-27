from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
from apps.core.permissions import IsHROrReadOnly
from apps.jobs.models import Job
from apps.applications.models import Application
from apps.meetings.models import Meeting
from apps.jobs.serializers import JobSerializer
from apps.applications.serializers import ApplicationSerializer

class HRDashboardStatsView(APIView):
    """Get comprehensive HR Dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated, IsHROrReadOnly]
    
    def get(self, request):
        """Get HR Dashboard statistics"""
        now = timezone.now()
        last_month = now - timedelta(days=30)
        last_week = now - timedelta(days=7)
        
        # Get jobs created by the authenticated HR user only
        jobs = Job.objects.filter(posted_by=request.user)
        
        # Active jobs (jobs that are still open/active)
        active_jobs = jobs.filter(status='active').count()
        total_jobs = jobs.count()
        
        # Total applications for jobs created by this HR user
        total_applications = Application.objects.filter(job__posted_by=request.user).count()
        
        # Applications this month vs last month for response rate calculation
        applications_this_month = Application.objects.filter(
            job__posted_by=request.user,
            applied_at__gte=now.replace(day=1)
        ).count()
        
        applications_last_month = Application.objects.filter(
            job__posted_by=request.user,
            applied_at__gte=last_month.replace(day=1),
            applied_at__lt=now.replace(day=1)
        ).count()
        
        # Calculate response rate (applications that received any response)
        responded_applications = Application.objects.filter(
            job__posted_by=request.user,
            status__in=['reviewing', 'shortlisted', 'interview_scheduled', 'selected', 'rejected']
        ).count()
        
        response_rate = 0
        if total_applications > 0:
            response_rate = round((responded_applications / total_applications) * 100, 1)
        
        # Response rate change from last month
        last_month_applications = Application.objects.filter(
            job__posted_by=request.user,
            applied_at__gte=last_month.replace(day=1),
            applied_at__lt=now.replace(day=1)
        ).count()
        
        last_month_responded = Application.objects.filter(
            job__posted_by=request.user,
            applied_at__gte=last_month.replace(day=1),
            applied_at__lt=now.replace(day=1),
            status__in=['reviewing', 'shortlisted', 'interview_scheduled', 'selected', 'rejected']
        ).count()
        
        last_month_response_rate = 0
        if last_month_applications > 0:
            last_month_response_rate = round((last_month_responded / last_month_applications) * 100, 1)
        
        response_rate_change = response_rate - last_month_response_rate
        
        # Interviews scheduled
        scheduled_interviews = Meeting.objects.filter(status='scheduled').count()
        
        # Interviews this week vs last week
        this_week_interviews = Meeting.objects.filter(
            start_time__gte=now - timedelta(days=now.weekday()),
            start_time__lt=now + timedelta(days=7-now.weekday()),
            status='scheduled'
        ).count()
        
        last_week_interviews = Meeting.objects.filter(
            start_time__gte=last_week - timedelta(days=7),
            start_time__lt=last_week,
            status='scheduled'
        ).count()
        
        interviews_change = this_week_interviews - last_week_interviews
        
        # Recent activity
        recent_applications = Application.objects.filter(
            job__posted_by=request.user
        ).select_related('job', 'applicant').order_by('-applied_at')[:5]
        
        recent_meetings = Meeting.objects.filter(
            application__job__posted_by=request.user
        ).select_related('application', 'created_by').order_by('-created_at')[:5]
        
        # Application status breakdown
        application_status_breakdown = Application.objects.filter(
            job__posted_by=request.user
        ).values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Job status breakdown
        job_status_breakdown = Job.objects.filter(
            posted_by=request.user
        ).values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Meeting type breakdown
        meeting_type_breakdown = Meeting.objects.filter(
            application__job__posted_by=request.user
        ).values('meeting_type').annotate(
            count=Count('id')
        ).order_by('meeting_type')
        
        stats = {
            'overview': {
                'active_jobs': active_jobs,
                'total_jobs': total_jobs,
                'total_applications': total_applications,
                'scheduled_interviews': scheduled_interviews,
                'response_rate': response_rate,
                'response_rate_change': response_rate_change,
                'interviews_change': interviews_change
            },
            'recent_activity': {
                'recent_applications': ApplicationSerializer(recent_applications, many=True).data,
                'recent_meetings': [
                    {
                        'id': meeting.id,
                        'title': meeting.title,
                        'meeting_type': meeting.meeting_type,
                        'start_time': meeting.start_time,
                        'status': meeting.status,
                        'applicant_name': f"{meeting.application.applicant.first_name} {meeting.application.applicant.last_name}",
                        'job_title': meeting.application.job.title,
                        'created_by': f"{meeting.created_by.first_name} {meeting.created_by.last_name}"
                    }
                    for meeting in recent_meetings
                ]
            },
            'breakdowns': {
                'application_status': list(application_status_breakdown),
                'job_status': list(job_status_breakdown),
                'meeting_type': list(meeting_type_breakdown)
            },
            'trends': {
                'applications_this_month': applications_this_month,
                'applications_last_month': applications_last_month,
                'this_week_interviews': this_week_interviews,
                'last_week_interviews': last_week_interviews
            }
        }
        
        return Response(stats)

class HRDashboardJobsView(generics.ListAPIView):
    """Get jobs for HR Dashboard with statistics"""
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsHROrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_queryset(self):
        # HR users can only see jobs they created
        return Job.objects.filter(posted_by=self.request.user).prefetch_related('applications')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add application count to each job
        for job in queryset:
            job.application_count = job.applications.count()
            job.recent_applications = job.applications.order_by('-applied_at')[:3]
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Add summary statistics
        summary = {
            'total_jobs': queryset.count(),
            'active_jobs': queryset.filter(status='active').count(),
            'draft_jobs': queryset.filter(status='draft').count(),
            'closed_jobs': queryset.filter(status='closed').count(),
            'total_applications': sum(job.application_count for job in queryset)
        }
        
        return Response({
            'summary': summary,
            'jobs': serializer.data
        })

class HRDashboardApplicationsView(generics.ListAPIView):
    """Get applications for HR Dashboard with filtering"""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsHROrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job']
    
    def get_queryset(self):
        # HR users can only see applications for jobs they created
        return Application.objects.filter(
            job__posted_by=self.request.user
        ).select_related('job', 'applicant').order_by('-applied_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Add summary statistics
        summary = {
            'total_applications': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'reviewing': queryset.filter(status='reviewing').count(),
            'shortlisted': queryset.filter(status='shortlisted').count(),
            'interview_scheduled': queryset.filter(status='interview_scheduled').count(),
            'selected': queryset.filter(status='selected').count(),
            'rejected': queryset.filter(status='rejected').count(),
        }
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'summary': summary,
            'applications': serializer.data
        })
