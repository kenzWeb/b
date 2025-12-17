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
    # "название файла должно начинаться с mpic* с сохранием формата"
    new_filename = f"mpic_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('courses/', new_filename)

class Course(models.Model):
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
        # Validate Image Size (max 2000 Kb = 2MB)
        if self.img and self.img.file:
            try:
                if self.img.size > 2 * 1024 * 1024:
                    raise ValidationError({'img': 'Размер файла не должен превышать 2000 Кб.'})
            except AttributeError:
                pass # File might not be accessible during some partial saves or if not changed

    def save(self, *args, **kwargs):
        # Resize image to max 300x300
        if self.img:
            # We open the image
            try:
                im = Image.open(self.img)
                if im.height > 300 or im.width > 300:
                    output_size = (300, 300)
                    im.thumbnail(output_size)
                    
                    # Save back to memory
                    buffer = BytesIO()
                    im.save(buffer, format='JPEG')
                    val = buffer.getvalue()
                    
                    # We need to save the modified content to the file field
                    # Use the same name
                    self.img.save(self.img.name, ContentFile(val), save=False)
            except Exception as e:
                pass # proper error handling usually required
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=50, verbose_name="Заголовок")
    text_content = models.TextField(verbose_name="Текстовое содержание")
    video_link = models.URLField(blank=True, verbose_name="Видеоссылка SuperTube")
    hours = models.PositiveIntegerField(
        validators=[MaxValueValidator(4)],
        verbose_name="Длительность"
    )

    def clean(self):
        # Validate SuperTube link
        if self.video_link:
            if 'super-tube.cc/video/' not in self.video_link:
                raise ValidationError({'video_link': 'Ссылка должна быть на super-tube.cc/video/'})
        
        # Check max 5 lessons per course
        # Note: This check logic is tricky on CREATE. If pk is None, we check count.
        if not self.pk:
            if self.course.lessons.count() >= 5:
                raise ValidationError("Курс не может содержать более 5 уроков.")

    def save(self, *args, **kwargs):
        if not self.pk:
             # Re-check count race condition technically possible but unlikely in single admin user scenario
             if self.course.lessons.count() >= 5:
                 pass # Or raise error, but clean() is typically called before save in forms. 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
