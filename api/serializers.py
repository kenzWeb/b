from rest_framework import serializers
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from students.models import Enrollment
import re

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate_password(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Password must be at least 3 characters long.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[_#!%]', value):
            raise serializers.ValidationError("Password must contain at least one of the following special characters: _, #, !, %")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'], # Use email as username
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CourseSerializer(serializers.ModelSerializer):
    # Using specific formats if needed, usage of URLField for img
    img = serializers.SerializerMethodField()
    start_date = serializers.DateField(format="%d-%m-%Y")
    end_date = serializers.DateField(format="%d-%m-%Y")

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'hours', 'img', 'start_date', 'end_date', 'price')

    def get_img(self, obj):
        request = self.context.get('request')
        if obj.img:
            return request.build_absolute_uri(obj.img.url)
        return None

class LessonSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='text_content')

    class Meta:
        model = Lesson
        fields = ('id', 'name', 'description', 'video_link', 'hours')

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    payment_status = serializers.CharField(source='get_status_display') # Or just raw status? Spec says: "pending(ожидает оплаты) | success(оплачен)..." so maybe display value or just key. Example shows strings like "pending".
    # Wait, Example view: "payment_status": "pending" (or readable?). "pending(ожидает оплаты)" suggests the example value might be the English key with description in parens in the prompt text.
    # But usually APIs return machine readable keys. The example logic says: `payment_status: {pending...}`.
    # The example Json shows: `"payment_status": "success"` (implied). I'll return the key for now.
    
    class Meta:
        model = Enrollment
        fields = ('id', 'payment_status', 'course')
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Spec format for payment_status might be just the key
        ret['payment_status'] = instance.status
        return ret
