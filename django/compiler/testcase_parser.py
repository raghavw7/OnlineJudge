import ast
def parse_test_case(input_str, output_str):

    # input_str = input_str.replace('[', '').replace(']', '')
    input_parts = input_str.rsplit('\r\n')
    input_part = []
    # for part in input_parts:
    #     print(part)
    for part in input_parts:
        a = part
        if '=' in a:
            a = a.rsplit('=')[1]
        input_part.append(a)
        print(ast.literal_eval(a))

    for part in input_part:
        print(part)
    parsed_inputs = [ast.literal_eval(part) for part in input_part]

    parsed_output = ast.literal_eval(output_str)

    return tuple(parsed_inputs) if len(parsed_inputs) > 1 else parsed_inputs[0], parsed_output

