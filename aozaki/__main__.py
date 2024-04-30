from pprint import pprint
from pathlib import Path

from .parser import parse_ast
from .eval import eval
from .utils import mk_context

from argparse import ArgumentParser

parser = ArgumentParser(
    prog='aozaki',
    description='Simple dynamically typed programming language',
)
parser.add_argument(
    '-e',
    '--empty-context',
    help='Make context of evaluation empty (without builtins)',
    action='store_true',
)
parser.add_argument('filename', help='file to execute', nargs='?')

args = parser.parse_args()

if args.empty_context:
    ctx = {}
else:
    ctx = mk_context()

if args.filename is None:
    raise NotImplementedError("REPL is not yet supported")

res = ctx['import'](args.filename)
print('======================')
print('Evaluation result')
print('======================')
print(res)


