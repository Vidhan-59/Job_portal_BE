from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from apps.core.permissions import IsHROrReadOnly
from .models import Meeting
from .serializers import MeetingSerializer, MeetingListSerializer
from apps.authentication.models import User

class MeetingListCreateView(generics.ListCreateAPIView):
    """List and create meetings with advanced filtering"""
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'meeting_type', 'application', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['start_time', 'end_time', 'created_at', 'title']
    ordering = ['-start_time']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MeetingListSerializer
        return MeetingSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Get query parameters for filtering
        upcoming = self.request.query_params.get('upcoming', None)
        past = self.request.query_params.get('past', None)
        today = self.request.query_params.get('today', None)
        this_week = self.request.query_params.get('this_week', None)
        
        # Base queryset based on user role
        if user.role == 'student':
            queryset = Meeting.objects.filter(attendees=user)
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            # HR users can only see meetings for jobs they created
            queryset = Meeting.objects.filter(application__job__posted_by=user)
        else:
            queryset = Meeting.objects.all()
        
        # Apply time-based filters
        now = timezone.now()
        
        if upcoming == 'true':
            queryset = queryset.filter(start_time__gt=now)
        elif past == 'true':
            queryset = queryset.filter(end_time__lt=now)
        elif today == 'true':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(
                start_time__gte=today_start,
                start_time__lt=today_end
            )
        elif this_week == 'true':
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            queryset = queryset.filter(
                start_time__gte=week_start,
                start_time__lt=week_end
            )
        
        return queryset.select_related('application', 'created_by').prefetch_related('attendees')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsHROrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class MeetingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a specific meeting"""
    serializer_class = MeetingSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Meeting.objects.filter(attendees=user)
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            # HR users can only see meetings for jobs they created
            return Meeting.objects.filter(application__job__posted_by=user)
        return Meeting.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsHROrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        # Update status to rescheduled if time changed
        instance = serializer.instance
        if (instance.start_time != serializer.validated_data.get('start_time') or 
            instance.end_time != serializer.validated_data.get('end_time')):
            serializer.save(status='rescheduled')
        else:
            serializer.save()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsHROrReadOnly])
def reschedule_meeting(request, pk):
    """Reschedule a specific meeting"""
    try:
        meeting = get_object_or_404(Meeting, pk=pk)
        
        # Support both formats: start_time/end_time OR scheduled_date
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        scheduled_date = request.data.get('scheduled_date')
        notes = request.data.get('notes', '')
        
        # If scheduled_date is provided, use it to calculate start and end times
        if scheduled_date:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                # Set default duration of 30 minutes if not specified
                default_duration = timedelta(minutes=30)
                start_time = scheduled_datetime
                end_time = scheduled_datetime + default_duration
            except ValueError:
                return Response(
                    {'error': 'Invalid scheduled_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif not start_time or not end_time:
            return Response(
                {'error': 'Either start_time and end_time OR scheduled_date is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate times
        if start_time and end_time:
            try:
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {'error': 'Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if start_time >= end_time:
                return Response(
                    {'error': 'End time must be after start time'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if start_time < timezone.now():
                return Response(
                    {'error': 'Start time cannot be in the past'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Update meeting
        if start_time:
            meeting.start_time = start_time
        if end_time:
            meeting.end_time = end_time
        
        meeting.status = 'rescheduled'
        
        # Add notes if provided (you might want to add a notes field to your Meeting model)
        if notes:
            # For now, we'll add notes to description, but ideally you should add a notes field
            if meeting.description:
                meeting.description += f"\n\nReschedule Notes: {notes}"
            else:
                meeting.description = f"Reschedule Notes: {notes}"
        
        meeting.save()
        
        serializer = MeetingSerializer(meeting)
        return Response({
            'message': 'Meeting rescheduled successfully',
            'meeting': serializer.data
        })
        
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsHROrReadOnly])
def cancel_meeting(request, pk):
    """Cancel a specific meeting"""
    try:
        meeting = get_object_or_404(Meeting, pk=pk)
        meeting.status = 'cancelled'
        meeting.save()
        
        serializer = MeetingSerializer(meeting)
        return Response({
            'message': 'Meeting cancelled successfully',
            'meeting': serializer.data
        })
        
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsHROrReadOnly])
def complete_meeting(request, pk):
    """Mark a meeting as completed"""
    try:
        meeting = get_object_or_404(Meeting, pk=pk)
        meeting.status = 'completed'
        meeting.save()
        
        serializer = MeetingSerializer(meeting)
        return Response({
            'message': 'Meeting marked as completed',
            'meeting': serializer.data
        })
        
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class MeetingStatsView(APIView):
    """Get meeting statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Base queryset
        if user.role == 'student':
            meetings = Meeting.objects.filter(attendees=user)
        elif user.role in ['recruiting_hr', 'hr_team_member', 'main_hr']:
            # HR users can only see meetings for jobs they created
            meetings = Meeting.objects.filter(application__job__posted_by=user)
        else:
            meetings = Meeting.objects.all()
        
        now = timezone.now()
        
        stats = {
            'total_meetings': meetings.count(),
            'upcoming_meetings': meetings.filter(start_time__gt=now).count(),
            'past_meetings': meetings.filter(end_time__lt=now).count(),
            'today_meetings': meetings.filter(
                start_time__date=now.date()
            ).count(),
            'this_week_meetings': meetings.filter(
                start_time__gte=now - timedelta(days=now.weekday()),
                start_time__lt=now + timedelta(days=7-now.weekday())
            ).count(),
            'by_status': {},
            'by_type': {}
        }
        
        # Status breakdown
        for status_choice in Meeting.STATUS_CHOICES:
            stats['by_status'][status_choice[0]] = meetings.filter(
                status=status_choice[0]
            ).count()
        
        # Type breakdown
        for type_choice in Meeting.MEETING_TYPE_CHOICES:
            stats['by_type'][type_choice[0]] = meetings.filter(
                meeting_type=type_choice[0]
            ).count()
        
        return Response(stats)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_attendee(request, pk):
    """Add an attendee to a meeting"""
    try:
        meeting = get_object_or_404(Meeting, pk=pk)
        attendee_id = request.data.get('attendee_id')
        
        if not attendee_id:
            return Response(
                {'error': 'attendee_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendee = User.objects.get(id=attendee_id)
            meeting.attendees.add(attendee)
            
            serializer = MeetingSerializer(meeting)
            return Response({
                'message': f'{attendee.first_name} {attendee.last_name} added to meeting',
                'meeting': serializer.data
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def remove_attendee(request, pk):
    """Remove an attendee from a meeting"""
    try:
        meeting = get_object_or_404(Meeting, pk=pk)
        attendee_id = request.data.get('attendee_id')
        
        if not attendee_id:
            return Response(
                {'error': 'attendee_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            attendee = User.objects.get(id=attendee_id)
            
            # Don't allow removing the applicant or creator
            if attendee == meeting.application.applicant:
                return Response(
                    {'error': 'Cannot remove the applicant from the meeting'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if attendee == meeting.created_by:
                return Response(
                    {'error': 'Cannot remove the meeting creator'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            meeting.attendees.remove(attendee)
            
            serializer = MeetingSerializer(meeting)
            return Response({
                'message': f'{attendee.first_name} {attendee.last_name} removed from meeting',
                'meeting': serializer.data
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Meeting.DoesNotExist:
        return Response(
            {'error': 'Meeting not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
