from aozaki.peco.peco import *
import string

tok = lambda f: memo(seq(ws, f))
ws = many(space)
mk_num = to(lambda x: ('num', int(x)))
number = seq(cite(some(digit)), mk_num)

map_esc0 = lambda s, t: seq(sym(s), to(lambda: t))
hex_digit = one_of(string.hexdigits)

mk_str = to(lambda inner: ('str', ''.join(inner)))
hex_escape = seq(cite(hex_digit), cite(hex_digit), to(lambda l, r: chr(int(l + r, 16))))
escape_seq = alt(
    cite(sym('"')),
    map_esc0('n', '\n'),
    map_esc0('r', '\r'),
    map_esc0('t', '\t'),
    seq(sym('x'), hex_escape),
)
string_inner = many(alt(
    seq(sym('\\'), escape_seq),
    cite(non(sym('"'))),
))
string = seq(
    sym('"'),
    seq(group(string_inner), mk_str),
    sym('"'),
)

free = lambda f: memo(seq(ws, f))
skip = lambda s: tok(sym(s))
mkvar = to(lambda n: ('var', n))

name_start = alt(letter, sym('_'))
name_rest = alt(name_start, digit, one_of('\'?'))
name = alt(
    cite(seq(name_start, many(name_rest))),
    seq(skip('@'), string, to(lambda old: old[1]))
)

op = lambda c: free(cite(sym(c)))

mkbop = to(lambda x, op, y: (op, x, y))
mkappl = to(lambda f, arg: ('apply', f, arg))
mkstruct = to(lambda names: ('defstruct', names))

factor = lambda s: factor(s)
term = lambda s: term(s)
expr = lambda s: expr(s)
power = lambda s: power(s)
special = lambda s: special(s)

struct_fields = list_of(free(name), skip(','))
struct = seq(
    skip('{'),
    group(opt(struct_fields)),
    opt(skip(',')),
    skip('}'),
    mkstruct,
)

bind_pat = seq(free(name), to(lambda n: ('bind', n)))
skip_pat = seq(skip('_'), to(lambda: ('any',)))

pat = lambda s: pat(s)

struct_field_pat_sugar = seq(
    memo(name),
    to(lambda n: (n, ('bind', n)))
)
struct_field_pat_verbose = seq(    
    memo(name),
    skip(':'),
    ws,
    pat,
    to(lambda n, p: (n, p)),
)
struct_fields_pat = list_of(
    free(alt(struct_field_pat_verbose, struct_field_pat_sugar)),
    skip(',')
)
struct_pat = seq(
    skip('{'),
    group(opt(struct_fields_pat)),
    opt(skip(',')),
    skip('}'),
    to(lambda fields_pat: ('matchstruct', fields_pat))
)
tup_pat = seq(
    skip('('),
    group(opt(list_of(pat, skip(',')))),
    opt(skip(',')),
    skip(')'),
    to(lambda pats: ('tuple', pats))
)

pat = left(alt(
    skip_pat,
    bind_pat,
    tup_pat,
    free(number),
    free(string),
    struct_pat,
))

case_arm = seq(
    pat,
    skip('->'),
    expr,
    to(lambda pat, expr: (pat, expr))
)
case_of = seq(
    skip('case'),
    skip('('),
    expr,
    skip(')'),
    skip('of'),
    skip('{'),
    group(opt(list_of(case_arm, skip(',')))),
    opt(skip(',')),
    skip('}'),
    to(lambda expr, arms: ('caseof', expr, arms))
)

do_bind = seq(
    skip('let'),
    some(space),
    pat,
    skip('='),
    expr,
    to(lambda pat, expr: ('dobind', pat, expr))
)
do_stmt = seq(
    alt(
        do_bind,
        seq(expr, to(lambda e: ('expr', e))),
    ),
    skip(';'),
)
do = seq(
    skip('do'),
    skip('{'),
    group(many(do_stmt)),
    skip('}'),
    to(lambda seq: ('doseq', seq))
)


let_sep = skip(';')
let_field_match = seq(
    pat,
    skip('='),
    expr,
    let_sep,
    to(lambda p, e: (p, e))
)

let = seq(
    skip('let'),
    some(space),
    group(some(let_field_match)),
    skip('in'),
    some(space),
    expr,
    to(lambda pats, in_: ('let', pats, in_))
)

tup = seq(
    skip('('),
    group(opt(list_of(expr, skip(',')))),
    opt(skip(',')),
    skip(')'),
    to(lambda tupl: ('tuple', tupl))
)
mkfunc = to(lambda p, e: ('defunc', p, e))
function = seq(pat, skip(':'), expr, mkfunc)
factor = alt(
    function,
    struct,
    free(number),
    free(seq(name, mkvar)),
    free(string),
    seq(skip('('), memo(expr), skip(')')),
    tup,
)

dot_op = lambda s: dot_op(s)

dot_rhs = alt(
    seq(name, to(lambda n: ('str', n))),
    number,
)
dot_op = left(alt(
    seq(dot_op, op('.'), dot_rhs, mkbop),
    seq(
        dot_op,
        seq(
            skip('`'),
            factor,
            skip('`'),
        ),
        factor,
        to(lambda lhs, f, rhs: ('apply', ('apply', f, lhs), rhs)),
    ),
    factor,
))

special = left(alt(
    let,
    do,
    case_of,
    seq(special, some(space), dot_op, mkappl),
    dot_op,
))
power = left(alt(
    seq(special, op('^'), power, mkbop),
    special,
))
term = left(alt(
    seq(term, alt(op('*'), op('/')), power, mkbop),
    power,
))
addsub = lambda s: addsub(s)
addsub = left(alt(
    seq(addsub, alt(op('+'), op('-')), term, mkbop),
    term,
))
expr = left(alt(
    seq(addsub, skip('$'), expr, to(lambda f, arg: ('apply', f, arg))),
    addsub,
))

def parse_ast(text, parser=expr):
    text = prepare(text)
    state = parse(text, parser)
    if not state.ok:
        raise SyntaxError(f"Cannot parse {text[state.pos:]!r} (stack = {state.stack!r})")
    return state.stack[0]

def prepare(s):
    s = s.strip()
    lines = []

    for l in s.split('\n'):
        if l.strip().startswith('--'):
            continue
        lines.append(l)
    return '\n'.join(lines)



