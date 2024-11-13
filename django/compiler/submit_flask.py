import logging
from django.shortcuts import HttpResponse
from .models import Problem, TestCase, Submission, User
# from . import testcase_parser
import json
import requests
import os
from django.conf import settings
from django.http import JsonResponse
import datetime
logger = logging.getLogger()


def submit_it(request, prob_id, lang, code):

    base_code_directory = os.path.join(settings.BASE_DIR, 'codes/')

    cpp_directory = os.path.join(base_code_directory, 'cpp/')
    python_directory = os.path.join(base_code_directory, 'python/')
    java_directory = os.path.join(base_code_directory, 'java/')

    problem = Problem.objects.get(id = prob_id)

    problem = Problem.objects.get(id=prob_id)
    testcase = testcase = TestCase.objects.filter(problem=problem)
    input_signature = problem.input_signature

    if lang == 'python':

        with open(python_directory + 'temp_code.py', 'w') as file:
            file.write(code)
        with open(python_directory + 'tempcode1.py', 'w') as file:
            file.write(code)


    tc_inputs_list = []
    for tc in testcase:
        if isinstance(tc.input, list) and len(tc.input) == len(input_signature):
            tc_inputs_list.append(tc.input)
        else:
            tc_inputs_list.append([tc.input])
        # tc_inputs_list.append(tc.input)

    inputs_list = f"{json.dumps(tc_inputs_list)}"
    error_flag = ''
    results = []
        # inputs_json = json.dumps(inputs)
        # inputs_e = json.loads(inputs)
    try:

        # response = requests.post('http://code-executor:5000/execute', json={'code': code})
        # response = requests.post('http://localhost:5000/execute', json={'code': code, 'inputs': inputs_list, 'language': lang})
        response = requests.post('http://code-executor:5000/execute', json={'code': code, 'inputs': inputs_list, 'language': lang})

        # response = requests.post('http://code-executor:5000/execute', json={'code':code, 'language':lang, 'inputs':tc_inputs})
        if response.status_code == 200:
            result = True
            output = response.json().get("output")
            if lang == 'cpp':
                # output = output.replace('\n', ',').rstrip(',')
                output = output.split('\n')
                # output = '[\'' + output + '\']'
            elif lang == 'python':
                output = json.loads(output)
            for i in range(0, len(testcase)):
                out = output[i]
                if type(out) != type(testcase[i].output):
                    out = type(testcase[i].output)(out)
                tc_output = testcase[i].output
                is_correct = out == tc_output
                results.append(is_correct)

        else:
            # return f"Error: {response.json().get('error')}"
            error_flag = f"Error: {response.json().get('error')}"
            print(error_flag)
    except requests.exceptions.RequestException as e:
        error_flag = f"Execution service unavailable: {str(e)}"
        # return


    #create submission
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

