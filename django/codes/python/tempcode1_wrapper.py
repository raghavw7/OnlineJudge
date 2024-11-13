
# -*- coding: utf-8 -*-
def solution(name):
    if(name == 'Mike'):
        return "Hello, Mike! It's nice to see you again!"
    else:
        return "I'm sorry, {}. I think you're not Mike.".format(name)
import sys
import json

# args_raw = sys.stdin.readline()
# args_list = json.loads(args_raw)

# print(solution(*args_list))
print(solution('Stephen'))
            