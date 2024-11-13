import json
import random

from django.shortcuts import render, redirect
from .models import Problem, User, TestCase, Submission
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .run_solutions_form import Run_Solution_Form, Add_Problem_Form, Edit_Problem_Form, Add_Test_Case_Form
import subprocess
import os
from django.contrib import messages
from django.conf import settings

import json
from django.http import JsonResponse
from django.core.paginator import Paginator

# Create your views here.

import uuid
import traceback

from . import compile_func
from . import submit_func
from . import submit_flask


import logging
logger = logging.getLogger()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('index')

    else:
        form = CustomUserCreationForm()

    return render(request, 'Registration/register.html', {'form':form})

def index(request):
    user=""
    if request.user.is_authenticated:
        user = {"user_name": request.user.username, }
    else:
        user = "Anon"
    return render(request, 'index_old.html', {"user_":user})

def probelem_set(request):

    # problems = []
    problems = Problem.objects.all()

    paginator = Paginator(problems, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, 'problem_set.html', {'problems': problems, 'page_obj': page_obj})


# @login_required()
def problems(request, prob_id):
    problem = Problem.objects.get(id=prob_id)
    form = Run_Solution_Form()
    return render(request, 'problem_description_react.html', {'problem_id': problem.id, 'executed':False, 'form': form, 'problem': problem})

def compile(lang, code, inputs):

    base_code_directory = os.path.join(settings.BASE_DIR, 'codes/')
    cpp_directory = os.path.join(base_code_directory, 'cpp/')
    python_directory = os.path.join(base_code_directory, 'python/')
    java_directory = os.path.join(base_code_directory, 'java/')
     # print(lang)

    print("inside compile")


    if lang == 'CPP':
        # compile_cpp()
        print('CPP')
        logger.info("inside if lang cpp")
        print(cpp_directory)
        logger.info(cpp_directory)
        output = 'a'
        if os.path.isdir(cpp_directory) is False:
            logger.info("inside compile if cpp_directory")
            os.mkdir(cpp_directory)


        with open(cpp_directory + 'tempcode1.cpp', 'w') as tempcodefile:
            tempcodefile.write(code)

        tempcppfile = cpp_directory + 'tempcode1.cpp'
        tempexefile = cpp_directory + 'temp_program'


        # compile_cmd = ['g++', 'tempcode1.cpp', '-o', 'temp_program']
        compile_cmd = ['g++', tempcppfile, '-o', tempexefile]

        try:
            compile_output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT, text=True)

            # run_cmd = ['./temp_program']
            run_cmd = [tempexefile]
            run_output = subprocess.run(run_cmd, input=inputs, capture_output=True, text=True)

            output = run_output.stdout
            return run_output.stdout

        except subprocess.CalledProcessError as e:
            output = e.output


        # cpp_process = subprocess.run([], capture_output=True)
        # print(cpp_process)
        # return cpp_process.stdout

        return HttpResponse(output)

        # return 'compiling C++ code...'

    elif lang == 'python':
        # compile_python()
        print('Python')
        print(python_directory)

        with open(python_directory + 'temp_code.py', 'w') as file:
            file.write(code)

        print(inputs)
        inputs = str(inputs)
        py_file = python_directory + 'temp_code.py'
        py_process = subprocess.run(['python', py_file], input=inputs, text=True, capture_output=True)

        res = str(py_process.stdout)
        res = res.replace('\r', ' ').replace('\n', '')
        print(str(py_process.stdout))
        print(py_process.stderr)
        return res

        # return 'compiling Python code...'

    elif lang == 'Java':
        # compile_java()
        print('Java')
        # return 'compiling Java code...'

    # return lang
    return HttpResponse("Unsupported language")


@csrf_exempt
def run_solution_react(request):
    if request.method == 'POST':
        try:
            # return JsonResponse({'result': "passed"}, status=200)
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            problem_id = data.get('problemId')
            # inputss = problem_id
            # inputss = data.get('inputs')

            # result = compile_func.compile_func(language, code, inputss)
            # result = submit_func.submit_it(request, problem_id,language, code)

            result = submit_flask.submit_it(request, problem_id,language, code)

            return JsonResponse({'result': result}, status=200)
        except Exception as e:
            logger.error("Error in run_solution_react %s\n%s", e, traceback.format_exc())
            return JsonResponse({'error':str(e)}, status=500)

    return JsonResponse({'error': 'Invalid Request'}, status=400)


@login_required
def add_problem(request):

    form = Add_Problem_Form()
    if request.method == 'POST':
        print('posted')
        form = Add_Problem_Form(request.POST)
        if form.is_valid():
            print("inside......")

            title_check = form.cleaned_data.get('title')
            if Problem.objects.filter(title=title_check).exists():
                return HttpResponse("Title already exists")
                # return render(request, 'compiler/add_problem.html', {'form': form})

            new_problem = form.save()
            messages.success(request, 'problem {} added successfully!'.format(new_problem.title))
            return redirect('problems', new_problem.id)
        # return redirect('problem_set')
    else:
        print("why isn't it valid")
        return render(request, 'compiler/add_problem.html', {'form': form})

@login_required()
def edit_problem(request, prob_id):

    problem = Problem.objects.get(id = prob_id)
    # problem = problem or None
    # form = Edit_Problem_Form(instance=problem)

    if request.method == 'POST':
        print('putted')
        form = Edit_Problem_Form(request.POST, instance=problem)
        if form.is_valid():
            print('putted')
            problem = form.save()
            messages.success(request, 'Problem {} updated successfully'.format(problem.title))
        else:
            print("form errors, ", form.errors)
        return redirect('problems', problem.id)
    else:
        form = Edit_Problem_Form(instance=problem)
        print('why going here?')
    return render(request, 'compiler/edit_problem.html', {'form': form, 'problem_id':problem.id})


@login_required()
def delete_problem(request, prob_id):

    problem = Problem.objects.get(id = prob_id)

    # if request.user.id  == problem.author.id:
    problem.delete()

    return render(request, 'profile.html', {})


@login_required()
def add_testcase(request, prob_id):

    problem = Problem.objects.get(id = prob_id)
    form = Add_Test_Case_Form()

    if request.method == 'POST':
        print("Posted")
        form = Add_Test_Case_Form(request.POST)

        if form.is_valid():
            testcase = form.save()
            # testcase.problem = problem
            print("saved")
            messages.success(request, 'testcase for {} added successfully!'.format(testcase.problem.title))
            return redirect('problems', problem.id)

    else:
        return render(request, 'compiler/add_testcase.html', {'form':form, 'problem':problem})


@login_required()
def delete_testcase(request, tc_id):

    tc = TestCase.objects.get(id = tc_id)

    # if request.user.id  == problem.author.id:
    tc.delete()

    return render(request, 'profile.html', {})

import math
def random_sprint(request):

    problem_set = Problem.objects.all()
    random_problems = []
    while len(random_problems) < 10:
        random_no = math.ceil(random.random()*30)
        problem = Problem.objects.get(id=random_no)
        if problem in random_problems:
            continue
        else:
            random_problems.append(problem)
        # random_problems.append(random_no)

    print(random_problems)

    return render(request, 'randomsprint.html', {'random_problems':random_problems})


def leaderboard_page(request):

    return render(request, 'leaderboard.html', {})

def leaderboard(request):

    users = User.objects.all()
    # toppers = User.objects.all().order_by('-date_joined')[:1]
    # toppers = toppers[:10]
    toppers = User.objects.all().order_by('-problems_solved')[:10]


    return JsonResponse({'toppers': list(toppers.values('username'))}, status=200)

    # return render(request, 'leaderboard.html', {'toppers':toppers})


def top_problems(request):

    # top_problems = Problem.objects.all().order_by('votes')[:10]
    top_problems = Problem.objects.all()
    return JsonResponse({'top_problems': list(top_problems.values('title'))}, status=200)

def top_problems_page(request):

    return render(request, 'top_problems.html', {})


def test_cases(request, prob_id):

    problem = Problem.objects.get(id=prob_id)
    testcases = TestCase.objects.filter(problem=problem)

    return JsonResponse({'testcases': list(testcases.values('input', 'output'))}, status=200)


def submissions(request):

    submission = Submission.objects.filter(user=request.user)

    return JsonResponse({'submissions': list(submission.values('problem', 'verdict', 'time_stamp'))}, status=200)