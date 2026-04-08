# main/urls.py

from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.dashboard_home, name='dashboard_home'),

    path('works/', views.WorkListView.as_view(), name='work_list'),
    path('works/create/', views.WorkCreateView.as_view(), name='work_create'),
    path('works/<int:pk>/', views.WorkDetailView.as_view(), name='work_detail'),
    path('works/<int:pk>/edit/', views.WorkUpdateView.as_view(), name='work_edit'),
    path('works/<int:pk>/delete/', views.WorkDeleteView.as_view(), name='work_delete'),

    path('criterions/', views.CriterionListView.as_view(), name='criterion_list'),
    path('criterions/create/', views.CriterionCreateView.as_view(), name='criterion_create'),
    path('criterions/<int:pk>/', views.CriterionDetailView.as_view(), name='criterion_detail'),
    path('criterions/<int:pk>/edit/', views.CriterionUpdateView.as_view(), name='criterion_update'),
    path('criterions/<int:pk>/delete/', views.CriterionDeleteView.as_view(), name='criterion_delete'),
    
    path('fields/<int:pk>/', views.FieldDetailView.as_view(), name='field_detail'),
    path('fields/<int:pk>/delete/', views.FieldDeleteView.as_view(), name='field_delete'),
    path('fields/create/', views.FieldCreateView.as_view(), name='field_create'),
    path('fields/<int:pk>/edit/', views.FieldUpdateView.as_view(), name='field_update'),
    path('fields/', views.FieldListView.as_view(), name='field_list'),

    path('levels/', views.LevelListView.as_view(), name='level_list'),
    path('levels/create/', views.LevelCreateView.as_view(), name='level_create'),
    path('levels/<int:pk>/', views.LevelDetailView.as_view(), name='level_detail'),
    path('levels/<int:pk>/edit/', views.LevelUpdateView.as_view(), name='level_update'),
    path('levels/<int:pk>/delete/', views.LevelDeleteView.as_view(), name='level_delete'),


    path('periods/', views.PeriodListView.as_view(), name='period_list'),
    path('periods/create/', views.PeriodCreateView.as_view(), name='period_create'),
    path('periods/<int:pk>/', views.PeriodDetailView.as_view(), name='period_detail'),
    path('periods/<int:pk>/edit/', views.PeriodUpdateView.as_view(), name='period_update'),
    path('periods/<int:pk>/delete/', views.PeriodDeleteView.as_view(), name='period_delete'),
    path('users/create/', views.user_create_page, name='user_create'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/achievements/create/', views.teacher_achievement_create_page, name='teacher_achievement_create'),
    path('teacher/achievements/get_criteria/<int:work_id>/', views.get_criteria_json, name='get_criteria_json'),
    path('teacher/achievements/get_fields/<int:criterion_id>/', views.get_fields_html, name='get_fields_html'),
    path('teacher/achievements/save/', views.teacher_achievement_save, name='teacher_achievement_save'),
    path('teacher/achievements/<int:pk>/delete/', views.TeacherAchievementDeleteView.as_view(), name='teacher_achievement_delete'),
    path('teacher/achievements/<int:pk>/edit/', views.teacher_achievement_edit, name='teacher_achievement_edit'),

    path('director/', views.director_dashboard, name='director_dashboard'),
    path('director/export/', views.director_export, name='director_export'),
]