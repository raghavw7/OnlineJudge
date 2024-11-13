from flask import Flask, request, jsonify
import docker
import logging
import json
import tempfile
import os
import tarfile
import io

app = Flask(__name__)
client = docker.DockerClient(base_url="unix://var/run/docker.sock")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cpp_type(value):
    if isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        elem_type = get_cpp_type(value[0]) if value else "int"
        return f"vector<{elem_type}>"

    return "auto"

# #include <iostream>
# #include <string>
# #include <vector>
# #include <type_traits>
#
# using namespace std;

def generate_cpp_main(inputs):
    main_code = []

    # Define the to_string_wrapper function outside of main
    main_code.append("""
#include <iostream>
#include <string>
#include <vector>
#include <type_traits>

using namespace std;

template<typename T>
string to_string_wrapper(const T& val) {
    if constexpr (std::is_same<T, int>::value || std::is_same<T, float>::value || std::is_same<T, double>::value) {
        return std::to_string(val);
    } else if constexpr (std::is_same<T, std::string>::value) {
        return val;
    } else {
        return "Unsupported type";
    }
}
""")

    # Start of main function
    main_code.append("int main() {")
    main_code.append("    vector<string> results;")

    # Generate the main logic to call the solution function and capture output
    for inp in inputs:
        # Get the type of each argument
        arg_types = [get_cpp_type(val) for val in inp]

        # Convert each value to the corresponding C++ argument format
        args = []
        for i, (arg_type, val) in enumerate(zip(arg_types, inp)):
            if isinstance(val, list):
                # Convert list of strings to C++ vector syntax
                args.append('{' + ', '.join([f'"{v}"' for v in val]) + '}')
            else:
                args.append(f'static_cast<{arg_type}>("{str(val)}")' if arg_type == "string" else str(val))

        # Add the code to invoke the solution with the generated arguments
        main_code.append(f'    results.push_back(to_string_wrapper(solution({", ".join(args)})));')

    # Print all results at once
    main_code.append("    // Output all results")
    main_code.append("    for (const auto& result : results) {")
    main_code.append("        cout << result << endl;")
    main_code.append("    }")

    # End of main function
    main_code.append("    return 0;")
    main_code.append("}")

    return "\n".join(main_code)


@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get("code", "")
    inputs = data.get("inputs", "")
    language = data.get("language", "")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if not inputs:
        return jsonify({"error: No inputs"}), 400

    inputs = json.loads(inputs)
    logger.info(language)
    try:
        # Run the wrapped code in the Python container using the -c option

        if(language == 'python'):
            logger.info("Starting container to execute python code.")
            # Wrap the user's code and inject the inputs directly into the script
            wrapped_code_python = f"""
import json
# User's solution function
{code}

# Define inputs and call solution
inputs = {inputs}

result = []
for inp in inputs:
    result.append(solution(*inp))
# result = solution(*inputs)
print(result)
"""
            logger.info(wrapped_code_python)
            output = client.containers.run(
                "python:3.10",
                command=["python", "-c", wrapped_code_python],  # Execute the wrapped code directly
                stdout=True,
                stderr=True
            ).decode("utf-8")

            # Retrieve the logs (output of the script)
            # output = container.logs().decode("utf-8")
            logger.info(f"Execution output: {output}")

            # Clean up container
            # container.remove()

            return jsonify({"output": output}), 200

        elif language == 'cpp':

            main_function = generate_cpp_main(inputs)
            wrapped_code_cpp = f"""
//user's solution function
#include <iostream>
#include <string>
#include <vector>
#include <type_traits>

{code}
{main_function}
"""
            logger.info(wrapped_code_cpp)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as cpp_file:
                cpp_file_path = cpp_file.name
                cpp_file.write(wrapped_code_cpp.encode("utf-8"))

            # Create a tar archive containing the C++ file
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                tar.add(cpp_file_path, arcname="temp_script.cpp")
            tar_stream.seek(0)

            # Start a gcc container
            container = client.containers.run("gcc:11.2.0", detach=True, tty=True)
            logger.info("Started gcc container.")

            # Copy the tar archive into the container
            container.put_archive("/tmp", tar_stream)

            # Compile and execute the C++ code within the container
            output = container.exec_run(
                cmd="bash -c 'g++ /tmp/temp_script.cpp -o /tmp/a.out && /tmp/a.out'",
                stdout=True,
                stderr=True
            ).output.decode("utf-8")

            # Clean up the container and temporary file
            container.stop()
            container.remove()
            os.remove(cpp_file_path)

            logger.info(f"C++ execution output: {output}")
            return jsonify({"output": output}), 200


    except docker.errors.ContainerError as e:
        return jsonify({"error": f"Container error: {e.stderr.decode('utf-8')}"}), 500
    except docker.errors.ImageNotFound:
        return jsonify({"error": "Image not found"}), 404
    except docker.errors.APIError as e:
        return jsonify({"error": f"Docker API error: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
