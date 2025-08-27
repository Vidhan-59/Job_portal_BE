from rest_framework import serializers
from .models import Application, ApplicationHistory
from apps.authentication.serializers import (
    UserSerializer,
    StudentProfileSerializer,
)

class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.SerializerMethodField()
    job_title = serializers.SerializerMethodField()
    applicant_details = UserSerializer(source='applicant', read_only=True)
    applicant_profile = StudentProfileSerializer(source='applicant.studentprofile', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('applicant', 'applied_at', 'updated_at')

    def get_applicant_name(self, obj):
        return f"{obj.applicant.first_name} {obj.applicant.last_name}"

    def get_job_title(self, obj):
        return obj.job.title

class ApplicationHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationHistory
        fields = '__all__'

    def get_changed_by_name(self, obj):
        return f"{obj.changed_by.first_name} {obj.changed_by.last_name}"
