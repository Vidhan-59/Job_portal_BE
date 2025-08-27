from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Job

User = get_user_model()

class JobSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField(read_only=True)
    hr_team_member_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('posted_by', 'created_at', 'updated_at')

    def get_applications_count(self, obj):
        return obj.applications.count()

    def create(self, validated_data):
        hr_team_member_ids = validated_data.pop('hr_team_member_ids', [])
        job = Job.objects.create(**validated_data)
        if hr_team_member_ids:
            hr_members = User.objects.filter(
                id__in=hr_team_member_ids,
                role__in=['recruiting_hr', 'hr_team_member', 'main_hr']
            )
            job.hr_team_members.set(hr_members)
        return job