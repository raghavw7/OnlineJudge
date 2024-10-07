from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import auth


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
    # code = models.TextField(max_length=4000)
    # test_cases = models.CharField(max_length=50)
    inputs = models.TextField(max_length=100, blank=True, null=True)
    outputs = models.TextField(max_length=100, blank=True, null=True)
    # votes = models.IntegerField(default=0)
    # for future:
    # attempted =  models.BooleanField()


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.CharField(max_length=4000)
    output = models.CharField(max_length=4000)

class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField()
    verdict = models.CharField(max_length=30, default='Failed')

    # For future:
    # run_time =
    # memory_usage =
    # test_cases_passed =