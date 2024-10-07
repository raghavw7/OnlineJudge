import json
import random

from django.shortcuts import render, redirect
from .models import Problem, User
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

from . import compile_func
from . import submit_func



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


    # for problem in problems:
        # print(problem.title)
        # print(problem.description)
    return render(request, 'problem_set.html', {'problems': problems, 'page_obj': page_obj})


# @login_required()
def problems(request, prob_id):

    # problem_id = prob_id or 1
    problem = Problem.objects.get(id=prob_id)
    form = Run_Solution_Form()
    return render(request, 'problem_description_react.html', {'problem_id': problem.id, 'executed':False, 'form': form, 'problem': problem})


@csrf_exempt
def run_solutions2(request):

    form = Run_Solution_Form(request.POST)
    problem_id =  1
    if request.method == 'POST':
        problem_id = 1
        form = Run_Solution_Form(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            lang = form.cleaned_data['language']
            input = form.cleaned_data['input']

            output = compile(lang, code, input)
            return HttpResponse(output)

    else:
        return render(request, 'run_solution.html', {'form':form})
    return HttpResponse('No post request')
    # prob = Problem.objects.get(problem_id = problem_id)
    # logic to execute code and get the results:

    # compile(code, input, output)

    # judge(output, {output from database})

    # render results
        # return render(request, 'problem_description.html', {'problem_id':problem_id, 'executed':True})

    # return render(request, 'problem_description.html', {'problem_id': problem_id, 'executed': True})

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


def submit(prob_id, language, code, inputs='a'):

    # user = request.user
    problem = Problem.objects.get(id = prob_id)
    # testcase = TestCase.objects.get(problem = problem)

    base_code_directory = os.path.join(settings.BASE_DIR, 'codes/')

    cpp_directory = os.path.join(base_code_directory, 'cpp/')
    python_directory = os.path.join(base_code_directory, 'python/')
    java_directory = os.path.join(base_code_directory, 'java/')

    output_directory = os.path.join(settings.BASE_DIR, 'outputs/')

    cpp_output_directory = os.path.join(output_directory, 'cpp/')
    python_output_directory = os.path.join(output_directory, 'python/')


    if not os.path.isdir(base_code_directory):
        os.mkdir(base_code_directory)

    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)

    if language == 'CPP':

        if os.path.isdir(cpp_directory) is False:
            os.mkdir(cpp_directory)
        if os.path.isdir(cpp_output_directory) is False:
            os.mkdir(cpp_output_directory)

        submission_id = str(uuid.uuid4().hex)
        # submissionfile = cpp_directory + str(user.id + submission_id + '.cpp')
        submissionfile = cpp_directory + str(str(problem.id) + submission_id + '.cpp')

        # submissiontemp = cpp_directory + str(user.id + submission_id + 'program')
        submissiontemp = cpp_output_directory + str(str(problem.id) + submission_id + 'program')

        with open(submissionfile, 'w') as codefile:
            codefile.write(code)


        compile_cmd = ['g++', submissionfile, '-o', submissiontemp]

        try:

            compile_output = subprocess.check_output(compile_cmd, stderr=subprocess.STDOUT, text=True)

            run_cmd = [submissiontemp]
            run_output = subprocess.run(run_cmd, input=inputs, capture_output = True, text=True)

            output = run_output.stdout
            return run_output.stdout

        except subprocess.CalledProcessError as e:
            output = e

        return output

    elif language == 'Python':

        if os.path.isdir(python_directory) is False:
            os.mkdir(python_directory)

        if not os.path.isdir(python_output_directory):
            os.mkdir(python_output_directory)

        submission_id = str(uuid.uuid4().hex)
        submissionfile = python_directory + str(str(problem.id) + submission_id + '.py')

        with open(submissionfile, 'w') as python_file:
            python_file.write(code)

        try:
            py_process = subprocess.run(['python', submissionfile], input=inputs, text=True, capture_output=True)
            output = py_process.stdout

        except subprocess.CalledProcessError as e:
            output = e

        return output


    elif language == 'Java':
        pass


    print("submitted")
    return HttpResponse("submitted")



def run_solution(request, prob_id):

    # code = 'hello'
    # language = 'py'
    # input = 'world'

    if request.method == 'POST':
        form = Run_Solution_Form(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            language = form.cleaned_data.get('language')
            inputs = form.cleaned_data.get('input')


            out = 'a'
            if 'compile_run' in request.POST:
                # return HttpResponse(compile(language, code, inputs))
                # out = compile(language, code, inputs)
                out = compile_func.compile_it(language, code, inputs)

            if 'compile_submit' in request.POST:
                # out = submit(request, prob_id, language, code, inputs)
                out = submit_func.submit_it(request, prob_id, language, code)

            return HttpResponse(out)

    return HttpResponse(('duhh'))


@csrf_exempt
def run_solution_react(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
            language = data.get('language')
            problem_id = data.get('problemId')
            inputs = problem_id



            result = compile(language, code, inputs)

            # return JsonResponse({'result': result}, status=200)
            return JsonResponse({'result': result}, status=200)
        except Exception as e:
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