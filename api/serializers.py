from rest_framework import serializers
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from students.models import Enrollment
import re

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate_password(self, value):
        """Валидация пароля на соответствие требованиям безопасности"""
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
        """Создание пользователя с хешированием пароля."""
        user = User.objects.create_user(
            username=validated_data['email'], 
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    
    img = serializers.SerializerMethodField()
    start_date = serializers.DateField(format="%d-%m-%Y")
    end_date = serializers.DateField(format="%d-%m-%Y")

    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'hours', 'img', 'start_date', 'end_date', 'price')

    def get_img(self, obj):
        """Возвращает абсолютный путь к изображению."""
        request = self.context.get('request')
        if obj.img:
            return request.build_absolute_uri(obj.img.url)
        return None

class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""
    description = serializers.CharField(source='text_content')

    class Meta:
        model = Lesson
        fields = ('id', 'name', 'description', 'video_link', 'hours')

class EnrollmentSerializer(serializers.ModelSerializer):
    """Сериализатор для записи"""
    course = CourseSerializer()
    payment_status = serializers.CharField(source='get_status_display') 
    
    class Meta:
        model = Enrollment
        fields = ('id', 'payment_status', 'course')
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        ret['payment_status'] = instance.status
        return ret
