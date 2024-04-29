from sys import argv, exit as sys_exit
from pprint import pprint

from .parser import expr
from .eval import eval
from peco import parse

try:
    file_name = argv[1]
except IndexError:
    print(f'aozaki usage: aozaki script.ao')
    sys_exit(1)

with open(file_name) as fp:
    text = fp.read()

state = parse(text.strip(), expr)
if not state.ok:
    print('Failed to parse, remaining:')
    print(text[state.pos:])
    print('---------------------------')
    print('Stack:')
    pprint(state.stack)
    sys_exit(1)

ast = state.stack[0]
print('AST')
print('===================')
pprint(ast)

print()
print('Execution')
print('===================')

res = eval(ast, {})
print(res)

