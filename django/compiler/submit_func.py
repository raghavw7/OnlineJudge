import datetime

import docker
import subprocess
import os
from django.conf import settings
import time
import logging
from django.shortcuts import HttpResponse
from .models import Problem, TestCase, Submission, User
from . import testcase_parser
import json
logger = logging.getLogger()


def submit_it(request, prob_id, lang, code):
    base_code_directory = os.path.join(settings.BASE_DIR, 'codes/')

    cpp_directory = os.path.join(base_code_directory, 'cpp/')
    python_directory = os.path.join(base_code_directory, 'python/')
    java_directory = os.path.join(base_code_directory, 'java/')

    problem = Problem.objects.get(id = prob_id)

    try:
        testcase = TestCase.objects.filter(problem=problem)
    except TestCase.DoesNotExist:
        testcase = None
        print(testcase)
    output = ''


    """

    docker_client = docker.from_env()
    containers = docker_client.containers.list(all=True)
    for container in containers:
        print(container.name)
    """


    extension = ''
    filename = ''
    compile = ""
    clean = ""
    cont_name = ''
    docker_img = ''
    exe = ''
    codefile = ''
    filepath = ''

    wrapper_script_path = ''


    if lang == 'CPP':
        if os.path.isdir(cpp_directory) is False:
            os.mkdir(cpp_directory)

        with open(cpp_directory + 'tempcode1.cpp', 'w') as tempcodefile:
            tempcodefile.write(code)

        # Prepare Docker Execution Files

        # filename = str(uuid)filename

        filename = "tempcode1"
        # submissionfile = cpp_directory + str(str(problem.id) + submission_id + '.cpp')

        extension = ".cpp"
        cont_name = "oj-cpp"
        compile = f"g++ -o {filename} {filename}.cpp"
        clean = f"{filename} {filename}.cpp"
        docker_img = "gcc:11.2.0"
        exe = f"{filename}"

        file = filename + extension
        filepath = os.path.join(cpp_directory, file)
        # filepath = settings.FILES_DIR + "/" + "codes/" + file
        # codefile = open(filepath, 'w')
        # codefile.write(code)
        # codefile.close()


    elif lang == 'python':
        print('Python')
        return python_directory
        print(python_directory)

        with open(python_directory + 'temp_code.py', 'w') as file:
            file.write(code)

        extension = '.py'
        filename = 'tempcode1'

        compile = f"python"
        clean = f"{filename}.py"
        cont_name = 'oj-py3-dev'
        docker_img = 'python'
        exe = f"python {filename}.py"

        file = filename + extension
        filepath = os.path.join(python_directory, file)
        codefile = open(filepath, 'w')
        codefile.write(code)
        codefile.close()

        wrapper_script_path = os.path.join(python_directory, f'{filename}_wrapper.py')

        with open(wrapper_script_path, 'w') as wrapper_file:
            wrapper_file.write("""
# -*- coding: utf-8 -*-
""")
            wrapper_file.write(code)

            wrapper_file.write("""
import sys
import json

args_raw = sys.stdin.readline()
args_list = json.loads(args_raw)

print(solution(*args_list))
            """)

        # filepath = settings.FILES_DIR + "/" + "codes/" + file
        # codefile = open(filepath, 'w')
        # codefile.write(code)
        # codefile.close()

    elif lang == 'Java':

        print("Java")
        print("java_directory")

        if not os.path.isdir(java_directory):
            os.mkdir(java_directory)

        filename = "Main"
        # submissionfile = cpp_directory + str(str(problem.id) + submission_id + '.cpp')

        extension = ".java"
        cont_name = "oj-java"
        compile = f"javac {filename}.java"
        clean = f"{filename}.java {filename}.class"
        docker_img = "openjdk"
        exe = f"java {filename}"

        file = filename + extension
        filepath = os.path.join(java_directory, file)
        # filepath = settings.FILES_DIR + "/" + "codes/" + file
        # codefile = open(filepath, 'w')
        # codefile.write(code)
        # codefile.close()

        # Check whether the docker container is running or not

    # code.strip

    # codefile = open(filepath, 'w')
    # codefile.write(code)
    # codefile.close()



    try:
        container = docker_client.containers.get(cont_name)
        container_state = container.attrs['State']
        container_is_running = (container_state['Status'] == 'running')
        if not container_is_running:
            container.start()
            # subprocess.run(f"docker run -dt --name {cont_name} {docker_img}", shell=True)

    except docker.errors.NotFound:
        subprocess.run(f"docker run -dt --name {cont_name} {docker_img}", shell=True)


    copy_process = subprocess.run(f"docker cp {wrapper_script_path} {cont_name}:/{filename}_wrapper.py", shell=True)


    #copying the code file to the docker container directory
    subprocess.run(f"docker cp {filepath} {cont_name}:/{file}", shell=True)

    cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)

    output = cmp.stdout
    print(output)


    if cmp.returncode != 0:
        # compiler error
        subprocess.run(f"docker exec {cont_name} rm {file}", shell=True)
        pass

    else:
        start = time.time()

        try:

            input_signature = problem.input_signature
            results = []
            for tc in testcase:
                inputs = tc.input
                print(inputs)
                ex_output = tc.output
                test_case_inputs = []
                if isinstance(inputs, list) and len(inputs) == len(input_signature):
                    test_case_inputs = inputs
                else:
                    test_case_inputs = [inputs]


                exec_command = f"docker exec -i {cont_name} python /{filename}_wrapper.py"

                input_data = f"{json.dumps(test_case_inputs)}"
                inp = json.loads(input_data)
                try:
                    res = subprocess.run(exec_command, input=input_data, capture_output=True, text=True, shell=True, timeout=5)
                    output = res.stdout.strip()
                    output_type = type(ex_output)
                    output = output_type(output)
                    # print(output)
                    # print(ex_output)
                    is_correct = (output == ex_output)
                    results.append(is_correct)
                except subprocess.TimeoutExpired:
                    subprocess.run(f"docker exec {cont_name} rm /{filename}_wrapper.py", shell=True)
                    return "Execution Timeout"


            runtime = time.time() - start
            subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)

            user = request.user
            print(user)
            print(user.username)
            # user = User.objects.get()
            submission = Submission(problem=problem, user=user, time_stamp=datetime.datetime.now())
            submission.save()
            print(submission.problem)

            if all(results):
                submission.verdict = 'Accepted'
                submission.save()
                return "passed"
            else:
                submission.verdict = 'Failed'
                submission.save()
                return "failed"

        except (RuntimeError, TypeError, NameError) as e:
            runtime = time.time() - start
            # verdict =
            print(e)
            subprocess.run(f"docker container kill {cont_name}", shell=True)
            subprocess.run(f"docker start {cont_name}", shell=True)
            subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)


