from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Work, Criterion, Level, Period, Field, User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'first_name', 'last_name', 'department', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('department', 'patronymic', 'role'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительные поля', {
            'fields': ('department', 'patronymic', 'role'),
        }),
    )

admin.site.register(User, CustomUserAdmin)

# Регистрация остальных моделей с простым отображением
@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'work', 'get_ratio')
    list_filter = ('work',)
    search_fields = ('name',)
    
    def get_ratio(self, obj):
        return f"{obj.ratio}"
    get_ratio.short_description = 'Коэффициент'

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'field', 'ratio')
    list_filter = ('field',)

@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start_date', 'end_date', 'status')
    list_filter = ('status',)
    search_fields = ('name',)

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'caption', 'criterion', 'type')
    list_filter = ('criterion', 'type')
    search_fields = ('caption',)
