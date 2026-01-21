from django.contrib import admin
from .models import Course, Lesson

class LessonInline(admin.StackedInline):
    """
    Инлайн-редактирование уроков внутри курса.
    Позволяет добавлять до 5 уроков прямо на странице курса.
    """
    model = Lesson
    extra = 0
    max_num = 5

class CourseAdmin(admin.ModelAdmin):
    """
    Административная панель для управления курсами.
    Отображает список курсов с пагинацией по 5 элементов.
    Позволяет редактировать курс и связанные уроки.
    """
    list_display = ('name', 'description', 'hours', 'price', 'start_date', 'end_date')
    list_per_page = 5
    inlines = [LessonInline]
    
    
    
    
    

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
