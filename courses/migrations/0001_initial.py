

import courses.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Название курса')),
                ('description', models.CharField(blank=True, max_length=100, verbose_name='Описание курса')),
                ('hours', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(10)], verbose_name='Продолжительность (часы)')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(100)], verbose_name='Цена')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(verbose_name='Дата окончания')),
                ('img', models.ImageField(upload_to=courses.models.course_image_path, validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg'])], verbose_name='Обложка курса')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Заголовок')),
                ('text_content', models.TextField(verbose_name='Текстовое содержание')),
                ('video_link', models.URLField(blank=True, verbose_name='Видеоссылка SuperTube')),
                ('hours', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(4)], verbose_name='Длительность')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.course')),
            ],
        ),
    ]
