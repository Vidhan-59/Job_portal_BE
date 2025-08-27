from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Meeting

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    applicant_name = serializers.SerializerMethodField()
    applicant_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting.application.field.model
        fields = ['id', 'job_title', 'applicant_name', 'status', 'applicant_email']
    
    def get_applicant_name(self, obj):
        return f"{obj.applicant.first_name} {obj.applicant.last_name}"
    
    def get_applicant_email(self, obj):
        return obj.applicant.email

class MeetingSerializer(serializers.ModelSerializer):
    attendee_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
        help_text="List of user IDs to add as attendees"
    )
    attendees = UserSerializer(many=True, read_only=True)
    application_details = ApplicationSerializer(source='application', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    interviewer_name = serializers.SerializerMethodField()
    interviewer_email = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'application', 'application_details', 'title', 'description',
            'meeting_type', 'start_time', 'end_time', 'meeting_link', 'status',
            'attendee_ids', 'attendees', 'created_by', 'created_by_details',
            'interviewer_name', 'interviewer_email', 'created_at', 'updated_at', 
            'duration_minutes', 'is_upcoming', 'is_past'
        ]
        read_only_fields = ('created_by', 'created_at', 'updated_at')

    def get_duration_minutes(self, obj):
        """Calculate meeting duration in minutes"""
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return int(duration.total_seconds() / 60)
        return 0

    def get_is_upcoming(self, obj):
        """Check if meeting is in the future"""
        return obj.start_time > timezone.now()

    def get_is_past(self, obj):
        """Check if meeting has already ended"""
        return obj.end_time < timezone.now()

    def get_interviewer_name(self, obj):
        """Get the primary interviewer name (usually the creator)"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return ""

    def get_interviewer_email(self, obj):
        """Get the primary interviewer email (usually the creator)"""
        if obj.created_by:
            return obj.created_by.email
        return ""

    def validate(self, data):
        """Custom validation for meeting data"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError(
                    "End time must be after start time"
                )
            
            if start_time < timezone.now():
                raise serializers.ValidationError(
                    "Start time cannot be in the past"
                )
        
        return data

    def create(self, validated_data):
        """Create meeting with proper attendee handling"""
        attendee_ids = validated_data.pop('attendee_ids', [])
        
        # Create the meeting first
        meeting = Meeting.objects.create(**validated_data)
        
        # Add attendees using the proper method
        if attendee_ids:
            attendees = User.objects.filter(id__in=attendee_ids)
            meeting.attendees.set(attendees)
        
        # Always add the applicant as an attendee
        applicant = meeting.application.applicant
        meeting.attendees.add(applicant)
        
        # Add the creator as an attendee if not already included
        creator = self.context['request'].user
        meeting.attendees.add(creator)
        
        return meeting

    def update(self, instance, validated_data):
        """Update meeting with proper attendee handling"""
        attendee_ids = validated_data.pop('attendee_ids', None)
        
        # Update the meeting fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update attendees if provided
        if attendee_ids is not None:
            attendees = User.objects.filter(id__in=attendee_ids)
            instance.attendees.set(attendees)
            # Ensure applicant and creator are always included
            instance.attendees.add(instance.application.applicant)
            instance.attendees.add(instance.created_by)
        
        return instance

class MeetingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    attendees_count = serializers.SerializerMethodField()
    application_details = ApplicationSerializer(source='application', read_only=True)
    interviewer_name = serializers.SerializerMethodField()
    interviewer_email = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_upcoming = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'meeting_type', 'start_time', 'end_time',
            'status', 'attendees_count', 'application_details',
            'interviewer_name', 'interviewer_email', 'duration_minutes', 
            'is_upcoming', 'created_at'
        ]
    
    def get_attendees_count(self, obj):
        return obj.attendees.count()
    
    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def get_is_upcoming(self, obj):
        return obj.start_time > timezone.now()
    
    def get_interviewer_name(self, obj):
        """Get the primary interviewer name (usually the creator)"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return ""

    def get_interviewer_email(self, obj):
        """Get the primary interviewer email (usually the creator)"""
        if obj.created_by:
            return obj.created_by.email
        return ""