from aozaki.peco.peco import *
import string

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
skip = lambda s: free(sym(s))

name_start = alt(letter, sym('_'))
name_rest = alt(name_start, digit, one_of('\'?'))
name = seq(name_start, many(name_rest))

var = seq(cite(name), to(lambda n: ('var', n)))
op = lambda c: free(cite(sym(c)))

mkbop = to(lambda x, op, y: (op, x, y))
mkappl = to(lambda f, arg: ('apply', f, arg))
mkstruct = to(lambda names: ('defstruct', names))

factor = lambda s: factor(s)
term = lambda s: term(s)
expr = lambda s: expr(s)
power = lambda s: power(s)
special = lambda s: special(s)

struct_fields = list_of(free(cite(name)), skip(','))
struct = seq(
    skip('{'),
    group(opt(struct_fields)),
    opt(skip(',')),
    skip('}'),
    mkstruct,
)

bind_pat = seq(free(cite(name)), to(lambda n: ('bind', n)))
skip_pat = seq(skip('_'), to(lambda: ('any',)))

pat = lambda s: pat(s)
struct_fields_pat = list_of(
    free(seq(
        cite(name),
        skip(':'),
        ws,
        pat,
        to(lambda n, p: (n, p))
    )),
    skip(',')
)
struct_pat = seq(
    skip('{'),
    group(opt(struct_fields_pat)),
    opt(skip(',')),
    skip('}'),
    to(lambda fields_pat: ('matchstruct', fields_pat))
)

pat = left(alt(
    skip_pat,
    bind_pat,
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

mkfunc = to(lambda p, e: ('defunc', p, e))
function = seq(pat, skip(':'), expr, mkfunc)
factor = alt(
    function,
    struct,
    free(number),
    free(var),
    free(string),
    seq(skip('('), expr, skip(')')),
)
special = left(alt(
    let,
    do,
    case_of,
    seq(special, some(space), factor, mkappl),
    factor,
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
comment = seq(
    sym('--'),
    non(sym('\n')),
)
expr = left(alt(
    seq(addsub, skip('$'), expr, to(lambda f, arg: ('apply', f, arg))),
    seq(comment, expr),
    addsub,
))


