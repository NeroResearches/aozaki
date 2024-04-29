from functools import reduce
from collections.abc import Mapping

def apply_dicts(dicts):
    return reduce(lambda x, y: {**x, **y}, dicts, {})

def struct(names, ctx={}):
    if not names:
        return {}
    def inner(x):
        nctx = {names[0]: x, **ctx}
        if len(names) == 1:
            return nctx
        return struct(names[1:], nctx)
    return inner

def pat_match_struct(x, fields, ctx):
    for field_name, field_pat in fields:
        if field_name not in x:
            return False, ctx
        value = x[field_name]

        res, ctx = pat_match(value, field_pat, ctx)
        if not res:
            return False, ctx
    return True, ctx

def pat_match(x, pat, ctx):
    pat_tp, *args = pat
    if pat_tp == 'num':
        return (isinstance(x, (int, float)) and x == args[0], ctx)
    elif pat_tp == 'any':
        return True, ctx
    elif pat_tp == 'str':
        return (isinstance(x, str) and x == args[0], ctx)
    elif pat_tp == 'matchstruct':
        if not isinstance(x, Mapping):
            return False, ctx
        return pat_match_struct(x, args[0], ctx)
    elif pat_tp == 'bind':
        return True, {**ctx, args[0]: x}
    raise NotImplementedError(f"Unknown pattern type {pat_tp!r}: {args!r} (args)")

def case_of(value, arms, ctx):
    for pat, expr in arms:
        success, new_ctx = pat_match(value, pat, ctx)
        if success:
            return eval(expr, new_ctx)
    raise ValueError(f"Uncovered case of patterns on {value} (arms = {arms})")

def bind_pat_match(pat, value, ctx):
    success, new_ctx = pat_match(value, pat, ctx)
    if success:
        return new_ctx
    raise ValueError(f"Unmatched let-pattern {pat} on {value}")

def let(pats, in_, ctx):
    for pat, expr in pats:
        value = eval(expr, ctx)
        ctx = bind_pat_match(pat, value, ctx)
    return eval(in_, ctx)

def do_sequential(seq, ctx):
    last = {}
    for seq_tp, *args in seq:
        if seq_tp == 'dobind':
            value = eval(args[1], ctx)
            ctx = bind_pat_match(args[0], value, ctx)
        elif seq_tp == 'expr':
            last = eval(args[0], ctx)
    return last

def eval(ast, ctx):
    match ast:
        case ('+', lhs, rhs):
            return eval(lhs, ctx) + eval(rhs, ctx)
        case ('-', lhs, rhs):
            return eval(lhs, ctx) - eval(rhs, ctx)
        case ('*', lhs, rhs):
            return eval(lhs, ctx) * eval(rhs, ctx)
        case ('^', lhs, rhs):
            return eval(lhs, ctx) ** eval(rhs, ctx)
        case ('num' | 'str', val):
            return val
        case ('doseq', seq):
            return do_sequential(seq, ctx)
        case ('defstruct', names):
            return struct(names)
        case ('caseof', val, arms):
            return case_of(eval(val, ctx), arms, ctx)
        case ('let', pats, in_):
            return let(pats, in_, ctx)
        case ('var', name):
            if name in ctx:
                return ctx[name]
            raise NameError(f"Unknown variable {name!r}")
        case ('apply', func, arg):
            f = eval(func, ctx)
            val = eval(arg, ctx)
            return f(val)
        case ('defunc', pat, body):
            def func(x):
                new_ctx = bind_pat_match(pat, x, ctx)
                return eval(body, new_ctx)
            return func
        case tp:
            raise ValueError(f"Unknown command {tp!r} with args {args}")
