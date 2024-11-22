from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import auth
from datetime import datetime

class User(AbstractUser):
    # username = models.CharField()
    # first_name = models.CharField()
    # last_name = models.CharField()

    # email = models.EmailField()
    institution = models.CharField(max_length=120)
    # date_joined = models.DateTimeField()

    problems_solved = models.IntegerField(default=0)
    problems_added = models.IntegerField(default=0)
    problems_solved_easy = models.IntegerField(default=0)
    problems_solved_medium = models.IntegerField(default=0)
    problems_solved_hard = models.IntegerField(default=0)
    # score = models.IntegerField(default=0)


class Problem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=4000)
    difficulty = models.CharField(max_length=25)
    inputs = models.TextField(max_length=1000, blank=True, null=True)
    outputs = models.TextField(max_length=1000, blank=True, null=True)
    input_signature = models.JSONField(null=True, blank=True)
    output_type = models.CharField(max_length=50, null=True, blank=True)
    # votes = models.IntegerField(default=0)
    # for future:
    # attempted =  models.BooleanField()


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.JSONField(max_length=4000)
    output = models.JSONField(max_length=4000)

class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(default=datetime.now, blank=True)
    verdict = models.CharField(max_length=30, default='Failed')
    code = models.TextField(max_length=1000, null=True, blank=True)

    # For future:
    # run_time =
    # memory_usage =
    # test_cases_passed =