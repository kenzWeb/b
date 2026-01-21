

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('success', 'Оплачено'), ('failed', 'Ошибка оплаты')], default='pending', max_length=10, verbose_name='Статус оплаты')),
                ('order_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='ID заказа')),
                ('certificate_number', models.CharField(blank=True, max_length=12, null=True, verbose_name='Номер сертификата')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course')),
            ],
        ),
    ]
