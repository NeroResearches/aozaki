from .parser import parse_ast
from .eval import eval

def mk_import(ctx):
    def import_(path):
        with open(path) as fp:
            text = fp.read()
        return eval(parse_ast(text), ctx)
    return import_

def mk_context(ctx=None):
    if ctx is None:
        ctx = {}

    ctx['if'] = lambda cond: lambda on_true: lambda on_false: on_true({}) if cond else on_false({})
    ctx['cons'] = lambda el: lambda rem: (el, *rem)
    ctx['nil'] = ()
    ctx['len'] = len
    ctx['uncons'] = lambda seq: (seq[0], seq[1:])
    ctx['empty?'] = lambda x: len(x) == 0
    ctx['true'] = True
    ctx['gt'] = lambda x: lambda y: x > y
    ctx['lt'] = lambda x: lambda y: x < y
    ctx['tail'] = lambda seq: seq[1:]
    ctx['false'] = False
    ctx['concat'] = lambda x: lambda y: (*x, *y)

    ctx['eq'] = lambda x: lambda y: x == y
    ctx['not'] = lambda x: not x

    ctx['at'] = lambda index: lambda arr: arr[index]

    ctx['import'] = mk_import(ctx)

    return ctx

