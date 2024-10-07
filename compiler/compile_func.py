import docker
import subprocess
import os
from django.conf import settings
import time
import logging
from django.shortcuts import HttpResponse
logger = logging.getLogger()

def compile_it(lang, code, inputs):

    base_code_directory = os.path.join(settings.BASE_DIR, 'codes/')

    cpp_directory = os.path.join(base_code_directory, 'cpp/')
    python_directory = os.path.join(base_code_directory, 'python/')
    java_directory = os.path.join(base_code_directory, 'java/')



    docker_client = docker.from_env()
    containers = docker_client.containers.list(all=True)
    for container in containers:
        print(container.name)

    extension = ''
    filename = ''
    compile = ""
    clean = ""
    cont_name = ''
    docker_img = ''
    exe = ''


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
        codefile = open(filepath, 'w')
        codefile.write(code)
        codefile.close()


    elif lang == 'Python':
        print('Python')
        print(python_directory)

        with open(python_directory + 'temp_code.py', 'w') as file:
            file.write(code)

        extension = '.py'
        filename = 'tempcode1'


        compile = f"python"
        clean = f"{filename}.py"
        cont_name = 'oj-py3'
        docker_img = 'python'
        exe = f"python {filename}.py"

        file = filename + extension
        filepath = os.path.join(python_directory, file)
        # filepath = settings.FILES_DIR + "/" + "codes/" + file
        codefile = open(filepath, 'w')
        codefile.write(code)
        codefile.close()

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
        codefile = open(filepath, 'w')
        codefile.write(code)
        codefile.close()

        #Check whether the docker container is running or not
    try:
        container = docker_client.containers.get(cont_name)
        container_state = container.attrs['State']
        container_is_running = (container_state['Status'] == 'running')
        if not container_is_running:
            container.start()
            # subprocess.run(f"docker run -dt --name {cont_name} {docker_img}", shell=True)

    except docker.errors.NotFound:
        subprocess.run(f"docker run -dt --name {cont_name} {docker_img}", shell=True)


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
            # res = subprocess.run(f"docker exec {cont_name} sh -c 'echo \"{inpute}\" | {exe}'", capture_output=True, shell=True)

            inputs = 5
            exec_command = f"sh -c \"echo {inputs} | /{filename}\""
            # res = subprocess.run(f"docker exec {cont_name} {exec_command}.py", capture_output=True)
            res = subprocess.run(f"docker exec {cont_name} {exe}", capture_output=True)


            runtime = time.time() - start
            subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)
            res = res.replace('\r', ' ').replace('\n', '')
            print(res)
            return res.stdout
        except subprocess.TimeoutExpired:
            runtime = time.time() - start
            # verdict =
            subprocess.run(f"docker container kill {cont_name}", shell=True)
            subprocess.run(f"docker start {cont_name}", shell=True)
            subprocess.run(f"docker exec {cont_name} rm {clean}", shell=True)


        output = "fuddu"


        return HttpResponse(output)

    return HttpResponse("Unsupported language")

