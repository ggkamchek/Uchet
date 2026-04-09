from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.RoleChoices.USER)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.RoleChoices.ADMIN)
        return self._create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        USER = 'teacher', 'Преподаватель'
        DIRECTOR = 'director', 'Руководитель'

    username = models.CharField(
        max_length=25,
        unique=True,
        db_column='Name',
        verbose_name='логин'
    )
    first_name = models.CharField(max_length=25, db_column='First_name')
    last_name = models.CharField(max_length=25, db_column='Last_name')
    department = models.CharField(max_length=5, db_column='Department')
    patronymic = models.CharField(max_length=25, db_column='Patronymic')
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.USER,
        db_column='Roles_ID'
    )
    email = models.EmailField(blank=True)

    objects = UserManager()

    class Meta:
        db_table = 'Users'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.role == self.RoleChoices.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)

class Work(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    name = models.CharField(max_length=255, unique=True, db_column='Name')

    class Meta:
        db_table = 'Works'

    def __str__(self):
        return self.name

class Period(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    end_date = models.DateTimeField(unique=True, db_column='End_date')
    name = models.CharField(max_length=20, unique=True, db_column='Name')
    start_date = models.DateTimeField(unique=True, db_column='Start_date')
    status = models.BooleanField(db_column='Status')

    class Meta:
        db_table = 'Periods'

    def __str__(self):
        return self.name

class Criterion(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    name = models.CharField(
        max_length=255,
        unique=True,
        db_column='Name',
        verbose_name='Название',
    )
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        db_column='WorksID',
        related_name='criterions',
        verbose_name='Работа',
    )
    ratio = models.FloatField(default=1.0, db_column='Ratio', verbose_name='Коэффициент')

    class Meta:
        db_table = 'criterions'

    def __str__(self):
        return self.name

class Field(models.Model):
    class TypeChoices(models.TextChoices):
        TEXT = 'text', 'текст'
        CHOOSER = 'chooser', 'выбиралка'
        PHOTO = 'photo', 'фото'

    id = models.AutoField(primary_key=True, db_column='ID')
    caption = models.CharField(max_length=255, db_column='Caption')
    criterion = models.ForeignKey(
        Criterion,
        on_delete=models.CASCADE,
        db_column='criterionsID',
        related_name='fields'
    )

    type = models.CharField(
        max_length=20,
        choices=TypeChoices.choices,
        default=TypeChoices.TEXT,
        db_column='Type'
    )

    class Meta:
        db_table = 'Fields'

    def __str__(self):
        return self.caption

class Level(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    caption = models.CharField(max_length=255, db_column='Caption')
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        db_column='FieldsID',
        related_name='levels'
    )
    ratio = models.FloatField(db_column='Ratio')

    class Meta:
        db_table = 'Levels'

    def __str__(self):
        return self.caption

class Achievement(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        db_column='PeriodsID',
        related_name='achievements'
    )
    time_of_addition = models.DateTimeField(db_column='Time_of_addition')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='Users_ID',
        related_name='achievements'
    )
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        db_column='WorksID',
        related_name='achievements'
    )
    def total_score(self):
        fvs = list(self.field_values.select_related('field__criterion').all())
        unique_criteria = set()
        chooser_pairs = []

        for field_value in fvs:
            field = field_value.field
            unique_criteria.add(field.criterion)
            if field.type != Field.TypeChoices.CHOOSER:
                continue
            try:
                level_id = int(field_value.value)
            except (TypeError, ValueError):
                continue
            chooser_pairs.append((field, level_id))

        level_by_key = {}
        if chooser_pairs:
            q = Q()
            for field, lid in chooser_pairs:
                q |= Q(pk=lid, field_id=field.id)
            level_by_key = {
                (lvl.field_id, lvl.pk): lvl for lvl in Level.objects.filter(q)
            }

        total = 0.0
        for field, lid in chooser_pairs:
            level = level_by_key.get((field.id, lid))
            if level is not None:
                total += level.ratio + field.criterion.ratio

        for criterion in unique_criteria:
            if not any(
                fv.field.criterion_id == criterion.pk
                and fv.field.type == Field.TypeChoices.CHOOSER
                for fv in fvs
            ):
                total += criterion.ratio

        return total

    class Meta:
        db_table = 'Achievements'

    def __str__(self):
        return f'Achievement {self.id}'

class AchievementFieldValue(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID')
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        db_column='Achievements_ID',
        related_name='field_values'
    )
    field = models.ForeignKey(
        Field,
        on_delete=models.CASCADE,
        db_column='Fields_ID',
        related_name='achievement_values'
    )
    value = models.CharField(max_length=1000, db_column='Value')

    class Meta:
        db_table = 'AchievementFieldValues'

    def __str__(self):
        return f'Value for AchiD {self.achievement_id} FieldD {self.field_id}'
