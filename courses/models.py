from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def course_image_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"mpic_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('courses/', new_filename)

class Course(models.Model):
    """Модель курса"""
    name = models.CharField(max_length=30, verbose_name="Название курса")
    description = models.CharField(max_length=100, blank=True, verbose_name="Описание курса")
    hours = models.PositiveIntegerField(
        validators=[MaxValueValidator(10)],
        verbose_name="Продолжительность (часы)"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(100)],
        verbose_name="Цена"
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    img = models.ImageField(
        upload_to=course_image_path,
        validators=[FileExtensionValidator(['jpg', 'jpeg'])],
        verbose_name="Обложка курса"
    )

    def clean(self):
        """Валидация данных модели"""
        
        if self.img and self.img.file:
            try:
                if self.img.size > 2 * 1024 * 1024:
                    raise ValidationError({'img': 'Размер файла не должен превышать 2000 Кб.'})
            except AttributeError:
                pass 

    def save(self, *args, **kwargs):
        """Сохранение модели"""
        
        if self.img:
            
            try:
                im = Image.open(self.img)
                if im.height > 300 or im.width > 300:
                    output_size = (300, 300)
                    im.thumbnail(output_size)
                    
                    
                    buffer = BytesIO()
                    im.save(buffer, format='JPEG')
                    val = buffer.getvalue()
                    
                    
                    
                    self.img.save(self.img.name, ContentFile(val), save=False)
            except Exception as e:
                pass 
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Удаление курса"""
        if self.enrollments.exists():
            raise ValidationError("Нельзя удалить курс, на который записаны студенты.")
        super().delete(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление курса (название)."""
        return self.name

class Lesson(models.Model):
    """Модель урока"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=50, verbose_name="Заголовок")
    text_content = models.TextField(verbose_name="Текстовое содержание")
    video_link = models.URLField(blank=True, verbose_name="Видеоссылка SuperTube")
    hours = models.PositiveIntegerField(
        validators=[MaxValueValidator(4)],
        verbose_name="Длительность"
    )

    def clean(self):
        """Валидация данных урока"""
        
        if self.video_link:
            if 'super-tube.cc/video/' not in self.video_link:
                raise ValidationError({'video_link': 'Ссылка должна быть на super-tube.cc/video/'})
        
        
        
        if not self.pk:
            if self.course.lessons.count() >= 5:
                raise ValidationError("Курс не может содержать более 5 уроков.")

    def save(self, *args, **kwargs):
        """Сохранение урока с дополнительной проверкой количества."""
        if not self.pk:
             
             if self.course.lessons.count() >= 5:
                 pass 
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Удаление урока"""
        if self.course.enrollments.exists():
            raise ValidationError("Нельзя удалить урок, если на курс записаны студенты.")
        super().delete(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление урока (название)."""
        return self.name
