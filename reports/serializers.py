from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'user', 'project', 'comment', 'reason', 'created_at']
        read_only_fields = ['user', 'created_at']

    def validate(self, data):
        if not data.get('project') and not data.get('comment'):
            raise serializers.ValidationError("You must report a project or a comment")
        
        if data.get('project') and data.get('comment'):
            raise serializers.ValidationError("You can't report a project and a comment at the same time")
        
        return data