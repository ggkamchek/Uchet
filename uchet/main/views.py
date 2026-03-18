from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import os
import uuid
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.core import serializers
import json

from .models import User, Work, Criterion, Field, Level, Achievement, AchievementFieldValue, Period


# Проверка прав доступа (только администратор)
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

# Миксин для защиты CBV
class AdminRequiredMixin:
    @method_decorator(user_passes_test(is_admin))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def role_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == User.RoleChoices.ADMIN:
            return redirect('dashboard_home')
        elif request.user.role == User.RoleChoices.USER:
            return redirect('teacher_dashboard')
    return redirect('login')

# Главная страница дашборда
@user_passes_test(is_admin)
def dashboard_home(request):
    context = {
        'latest_works': Work.objects.all().order_by('-id')[:5],
        'latest_criterions': Criterion.objects.all().order_by('-id')[:5],
        'latest_fields': Field.objects.all().order_by('-id')[:5],
        'latest_levels': Level.objects.all().order_by('-id')[:5],
        'latest_periods': Period.objects.all().order_by('-id')[:5],
    }
    return render(request, 'main/dashboard_home.html', context)

# ---------- Работы (Work) ----------
class WorkListView(AdminRequiredMixin, ListView):
    model = Work
    template_name = 'main/work/work_list.html'
    context_object_name = 'works'

class WorkCreateView(AdminRequiredMixin, CreateView):
    model = Work
    fields = ['name']
    template_name = 'main/work/work_form.html'
    success_url = reverse_lazy('work_list')

class WorkDetailView(AdminRequiredMixin, DetailView):
    model = Work
    template_name = 'main/work/work_detail.html'
    context_object_name = 'work'

class WorkUpdateView(AdminRequiredMixin, UpdateView):
    model = Work
    fields = ['name']
    template_name = 'main/work/work_form.html'
    success_url = reverse_lazy('work_list')

class WorkDeleteView(AdminRequiredMixin, DeleteView):
    model = Work
    template_name = 'main/work/work_confirm_delete.html'
    success_url = reverse_lazy('work_list')

# ---------- Критерии (Criterion) ----------
class CriterionListView(AdminRequiredMixin, ListView):
    model = Criterion
    template_name = 'main/criterion/criterion_list.html'
    context_object_name = 'criterions'

class CriterionCreateView(AdminRequiredMixin, CreateView):
    model = Criterion
    fields = ['name', 'work']
    template_name = 'main/criterion/criterion_form.html'
    success_url = reverse_lazy('criterion_list')

    def get_initial(self):
        """Предзаполняет поле work, если передан параметр work в GET"""
        initial = super().get_initial()
        work_id = self.request.GET.get('work')
        if work_id:
            try:
                initial['work'] = Work.objects.get(pk=work_id)
            except Work.DoesNotExist:
                pass
        return initial

class CriterionDetailView(AdminRequiredMixin, DetailView):
    model = Criterion
    template_name = 'main/criterion/criterion_detail.html'
    context_object_name = 'criterion'

class CriterionUpdateView(AdminRequiredMixin, UpdateView):
    model = Criterion
    fields = ['name', 'work']
    template_name = 'main/criterion/criterion_form.html'
    success_url = reverse_lazy('criterion_list')

class CriterionDeleteView(AdminRequiredMixin, DeleteView):
    model = Criterion
    template_name = 'main/criterion/criterion_confirm_delete.html'
    success_url = reverse_lazy('criterion_list')

# ---------- Поля (Field) ----------
class FieldListView(AdminRequiredMixin, ListView):
    model = Field
    template_name = 'main/field/field_list.html'
    context_object_name = 'fields'

class FieldCreateView(AdminRequiredMixin, CreateView):
    model = Field
    fields = ['caption', 'criterion', 'type']   # type — выбор из text/chooser/photo
    template_name = 'main/field/field_form.html'
    success_url = reverse_lazy('field_list')

    def get_initial(self):
        initial = super().get_initial()
        criterion_id = self.request.GET.get('criterion')
        if criterion_id:
            try:
                initial['criterion'] = Criterion.objects.get(pk=criterion_id)
            except Criterion.DoesNotExist:
                pass
        return initial

class FieldDetailView(AdminRequiredMixin, DetailView):
    model = Field
    template_name = 'main/field/field_detail.html'
    context_object_name = 'field'

class FieldUpdateView(AdminRequiredMixin, UpdateView):
    model = Field
    fields = ['caption', 'criterion', 'type']
    template_name = 'main/field/field_form.html'
    success_url = reverse_lazy('field_list')

class FieldDeleteView(AdminRequiredMixin, DeleteView):
    model = Field
    template_name = 'main/field/field_confirm_delete.html'
    success_url = reverse_lazy('field_list')

# ---------- Уровни (Level) ----------
class LevelListView(AdminRequiredMixin, ListView):
    model = Level
    template_name = 'main/level/level_list.html'
    context_object_name = 'levels'

class LevelCreateView(AdminRequiredMixin, CreateView):
    model = Level
    fields = ['caption', 'field', 'ratio']
    template_name = 'main/level/level_form.html'
    success_url = reverse_lazy('level_list')

    def get_initial(self):
        initial = super().get_initial()
        field_id = self.request.GET.get('field')
        if field_id:
            try:
                initial['field'] = Field.objects.get(pk=field_id)
            except Field.DoesNotExist:
                pass
        return initial

class LevelDetailView(AdminRequiredMixin, DetailView):
    model = Level
    template_name = 'main/level/level_detail.html'
    context_object_name = 'level'

class LevelUpdateView(AdminRequiredMixin, UpdateView):
    model = Level
    fields = ['caption', 'field', 'ratio']
    template_name = 'main/level/level_form.html'
    success_url = reverse_lazy('level_list')

class LevelDeleteView(AdminRequiredMixin, DeleteView):
    model = Level
    template_name = 'main/level/level_confirm_delete.html'
    success_url = reverse_lazy('level_list')

# ---------- Периоды (Period) ----------
class PeriodListView(AdminRequiredMixin, ListView):
    model = Period
    template_name = 'main/period/period_list.html'
    context_object_name = 'periods'

class PeriodCreateView(AdminRequiredMixin, CreateView):
    model = Period
    fields = ['name', 'start_date', 'end_date', 'status']
    template_name = 'main/period/period_form.html'
    success_url = reverse_lazy('period_list')

class PeriodDetailView(AdminRequiredMixin, DetailView):
    model = Period
    template_name = 'main/period/period_detail.html'
    context_object_name = 'period'

class PeriodUpdateView(AdminRequiredMixin, UpdateView):
    model = Period
    fields = ['name', 'start_date', 'end_date', 'status']
    template_name = 'main/period/period_form.html'
    success_url = reverse_lazy('period_list')

class PeriodDeleteView(AdminRequiredMixin, DeleteView):
    model = Period
    template_name = 'main/period/period_confirm_delete.html'
    success_url = reverse_lazy('period_list')

    # Миксин для проверки роли преподавателя (teacher)
class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.RoleChoices.USER

# Декоратор для FBV
def teacher_required(view_func):
    decorated_view_func = login_required(view_func)
    return user_passes_test(lambda u: u.is_authenticated and u.role == User.RoleChoices.USER)(decorated_view_func)

    
# ---------- Преподавательская панель ----------
@teacher_required
def teacher_dashboard(request):
    achievements = Achievement.objects.filter(user=request.user).select_related(
        'work', 'period'
    ).prefetch_related(
        'field_values__field',
        'field_values__field__levels'
    ).order_by('-time_of_addition')
    return render(request, 'main/teacher/teacher_dashboard.html', {'achievements': achievements})

class TeacherAchievementListView(TeacherRequiredMixin, ListView):
    model = Achievement
    template_name = 'main/teacher/teacher_achievement_list.html'
    context_object_name = 'achievements'

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user).order_by('-time_of_addition')

@teacher_required
def teacher_achievement_select_work(request):
    works = Work.objects.all()
    return render(request, 'main/teacher/teacher_select_work.html', {'works': works})

@teacher_required
def teacher_achievement_create(request, work_id, criterion_id):
    work = get_object_or_404(Work, pk=work_id)
    criterion = get_object_or_404(Criterion, pk=criterion_id, work=work)

    # Получаем активный период
    try:
        active_period = Period.objects.get(status=True)
    except Period.DoesNotExist:
        messages.error(request, 'Нет активного периода. Невозможно добавить достижение.')
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        # Создаём достижение
        achievement = Achievement.objects.create(
            user=request.user,
            work=work,
            period=active_period,
            time_of_addition=timezone.now()
        )

        # Поля только для выбранного критерия
        fields = Field.objects.filter(criterion=criterion).prefetch_related('levels')

        for field in fields:
            field_key = f'field_{field.id}'
            if field.type == 'text':
                value = request.POST.get(field_key, '').strip()
                if value:
                    AchievementFieldValue.objects.create(
                        achievement=achievement,
                        field=field,
                        value=value
                    )
            elif field.type == 'chooser':
                level_id = request.POST.get(field_key)
                if level_id:
                    try:
                        level = Level.objects.get(pk=level_id, field=field)
                        AchievementFieldValue.objects.create(
                            achievement=achievement,
                            field=field,
                            value=str(level_id)
                        )
                    except Level.DoesNotExist:
                        pass
            elif field.type == 'photo':
                if field_key in request.FILES:
                    uploaded_file = request.FILES[field_key]
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'achievement_photos')
                    os.makedirs(upload_dir, exist_ok=True)
                    ext = os.path.splitext(uploaded_file.name)[1]
                    filename = f"{achievement.id}_{field.id}_{uuid.uuid4().hex}{ext}"
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    relative_path = os.path.join('achievement_photos', filename)
                    AchievementFieldValue.objects.create(
                        achievement=achievement,
                        field=field,
                        value=relative_path
                    )

        messages.success(request, 'Достижение успешно добавлено')
        return redirect('teacher_dashboard')

    # GET запрос: показываем форму для выбранного критерия
    fields = Field.objects.filter(criterion=criterion).prefetch_related('levels')
    context = {
        'work': work,
        'criterion': criterion,
        'fields': fields,
    }
    return render(request, 'main/teacher/teacher_achievement_form.html', context)

@teacher_required
def teacher_achievement_select_criterion(request, work_id):
    work = get_object_or_404(Work, pk=work_id)
    criteria = Criterion.objects.filter(work=work)
    return render(request, 'main/teacher/teacher_select_criterion.html', {'work': work, 'criteria': criteria})

class TeacherAchievementDeleteView(TeacherRequiredMixin, DeleteView):
    model = Achievement
    template_name = 'main/teacher/teacher_achievement_confirm_delete.html'
    success_url = reverse_lazy('teacher_dashboard')

    def get_queryset(self):
        # Только свои достижения
        return Achievement.objects.filter(user=self.request.user)
    
@teacher_required
def teacher_achievement_create_page(request):
    works = Work.objects.all()
    return render(request, 'main/teacher/teacher_achievement_create.html', {'works': works})

@teacher_required
@require_GET
def get_criteria_json(request, work_id):
    try:
        work = Work.objects.get(pk=work_id)
        criteria = work.criterions.all().values('id', 'name')
        return JsonResponse(list(criteria), safe=False)
    except Work.DoesNotExist:
        return JsonResponse({'error': 'Work not found'}, status=404)

@teacher_required
@require_GET
def get_fields_html(request, criterion_id):
    try:
        criterion = Criterion.objects.get(pk=criterion_id)
        fields = criterion.fields.all().prefetch_related('levels')
        return render(request, 'main/partials/fields_form.html', {'fields': fields})
    except Criterion.DoesNotExist:
        return HttpResponseBadRequest('Criterion not found')
    
@teacher_required
def teacher_achievement_save(request):
    if request.method == 'POST':
        work_id = request.POST.get('work')
        criterion_id = request.POST.get('criterion')

        if not work_id or not criterion_id:
            messages.error(request, 'Выберите работу и критерий')
            return redirect('teacher_achievement_create')

        work = get_object_or_404(Work, pk=work_id)
        criterion = get_object_or_404(Criterion, pk=criterion_id, work=work)

        # Получаем активный период
        active_period = Period.objects.filter(status=True).first()
        if not active_period:
            messages.error(request, 'Нет активного периода')
            return redirect('teacher_achievement_create')

        # Создаём достижение
        achievement = Achievement.objects.create(
            user=request.user,
            work=work,
            period=active_period,
            time_of_addition=timezone.now()
        )

        # Получаем все поля выбранного критерия
        fields = criterion.fields.all()
        for field in fields:
            field_key = f'field_{field.id}'
            if field.type == 'text':
                value = request.POST.get(field_key, '').strip()
                if value:
                    AchievementFieldValue.objects.create(achievement=achievement, field=field, value=value)
            elif field.type == 'chooser':
                level_id = request.POST.get(field_key)
                if level_id:
                    try:
                        level = Level.objects.get(pk=level_id, field=field)
                        AchievementFieldValue.objects.create(achievement=achievement, field=field, value=str(level_id))
                    except Level.DoesNotExist:
                        pass
            elif field.type == 'photo':
                if field_key in request.FILES:
                    uploaded_file = request.FILES[field_key]
                    # Сохранение файла
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'achievement_photos')
                    os.makedirs(upload_dir, exist_ok=True)
                    ext = os.path.splitext(uploaded_file.name)[1]
                    filename = f"{achievement.id}_{field.id}_{uuid.uuid4().hex}{ext}"
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    relative_path = os.path.join('achievement_photos', filename)
                    AchievementFieldValue.objects.create(achievement=achievement, field=field, value=relative_path)

        messages.success(request, 'Достижение успешно добавлено')
        return redirect('teacher_dashboard')
    else:
        return redirect('teacher_achievement_create')
    
class TeacherAchievementEditView(TeacherRequiredMixin, UpdateView):
    model = Achievement
    fields = []  # пока пусто, потом можно добавить редактирование
    template_name = 'main/teacher/teacher_achievement_edit.html'
    success_url = reverse_lazy('teacher_dashboard')

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)