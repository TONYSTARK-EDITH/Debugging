# Generated by Django 3.2.9 on 2021-11-26 04:09

import Interpreter.models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminPriv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SmallIntegerField(choices=[(0, 'Default'), (1, 'Easy'), (2, 'Medium'), (3, 'High')], default=0)),
                ('time', models.CharField(default='26.11.2021 09:39:54', max_length=1000)),
                ('results', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=1000), blank=True, default=list, size=16)),
                ('players_survived', models.SmallIntegerField(choices=[(16, 'Default'), (8, 'Easy'), (4, 'Medium'), (2, 'High'), (1, 'Survivor')], default=16)),
            ],
            options={
                'verbose_name_plural': 'AdminPriv',
            },
        ),
        migrations.CreateModel(
            name='Compiler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('client_id', models.CharField(max_length=1000)),
                ('client_secret_key', models.CharField(max_length=1000)),
                ('selected', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Compiler',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, default='', max_length=1000)),
                ('question_code', models.TextField(default='')),
                ('question_type', models.SmallIntegerField(choices=[(1, 'Easy'), (2, 'Medium'), (4, 'High')], default=1)),
                ('question_time', models.SmallIntegerField(choices=[(1, '10 min'), (2, '20 min'), (4, '30 min')], default=1)),
                ('lang', models.SmallIntegerField(choices=[(1, 'Python'), (2, 'Java'), (3, 'C')], default=1)),
            ],
            options={
                'verbose_name_plural': 'Questions',
            },
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_online', models.BooleanField(default=False)),
                ('program_completed', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=10)),
                ('program_code', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True), blank=True, default=list, size=10)),
                ('program_time', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, default=Interpreter.models.timer, size=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Players',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='TestCases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testcases', models.TextField()),
                ('question_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Interpreter.questions')),
            ],
            options={
                'verbose_name_plural': 'TestCases',
            },
        ),
    ]