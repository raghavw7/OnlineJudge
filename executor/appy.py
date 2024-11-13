from flask import Flask, request, jsonify
import docker
import logging
import os
app = Flask(__name__)
client = docker.DockerClient(base_url="unix://var/run/docker.sock")  # Connect to Docker on the host

# Set up logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "")
    inputs = data.get("inputs", "")
    if not code:
        return jsonify({"error": "No code provided"}), 400
#     host_script_path = '/tmp/temp_script.py'
#     container_script_path = '/scripts/temp_script.py'
#
#     with open(host_script_path, 'w') as f:
#         # Write the user code and the wrapper to handle inputs
#         f.write(f"{code}\n\n")
#         f.write("""
# import sys
# import json
#
# # Read inputs from stdin
# args_raw = sys.stdin.read()
# args_list = json.loads(args_raw)
#
# # Call the solution function and print result
# print(solution(*args_list))
# """)

    try:
        # Create and start a temporary container to execute the code
        logger.info("Starting container to execute code.")
        container = client.containers.run(
            "python:3.10",                        # Using Python 3.10 image for execution
            command=["python", "-c", code],       # Run code as a command list for better reliability
            detach=True,
            stdin_open=True,# Run container in detached mode
            stdout=True,
            stderr=True,             # Capture stdout and stderr
            # volumes={host_script_path: {'bind': container_script_path, 'mode':'ro'}}
            # remove=True                           # Auto-remove container after execution
        )
        # if inputs:
        #     logger.info(f"Passing inputs to container: {inputs}")
        #     container.exec_run(f"echo '{inputs}' | python -c {code}")
        #     container.exec_run(f"echo '{inputs}' | python {container_script_path}", stdout=True, stderr=True)
        #     # container.exec_run(f"echo '{inputs}' | python {container_script_path}", stdout=True, stderr=True)

        # Wait for the container to finish execution
        logger.info("Waiting for container to complete execution.")
        container.wait()                           # Wait until container finishes execution

        # Retrieve logs
        logs = container.logs().decode("utf-8")    # Decode logs
        logger.info(f"Execution logs: {logs}")     # Log the output for debugging

        container.remove()

        # Return output
        return jsonify({"output": logs}), 200
    except docker.errors.ContainerError as e:
        return jsonify({"error": f"Container error: {e.stderr.decode('utf-8')}"}), 500
    except docker.errors.ImageNotFound:
        return jsonify({"error": "Image not found"}), 404
    except docker.errors.APIError as e:
        return jsonify({"error": f"Docker API error: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # Log any unexpected errors
        return jsonify({"error": str(e)}), 500
    # finally:
    #     # Clean up temp file
    #     if os.path.exists('/tmp/temp_script.py'):
    #         os.remove('/tmp/temp_script.py')
