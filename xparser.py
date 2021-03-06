from collections import namedtuple
from functools import reduce, partial

R = namedtuple("R", "s p r")
T = namedtuple("T", "t v")

def nothing(p): return R(True, p, [])
def tx(x): return R(True, x.p, x.r)
def fx(x): return R(False, x.p, x.r)
def bind(x, f): return (lambda y: R(y.s,y.p,[x.r,y.r]) if y.s else fx(x))(f(x.p)) if x.s else fx(x)
def sbind(p, x, f): return (lambda y: y if y.s else fx(nothing(p)))(bind(x, f))
def pbind(x, f): return x if x.s else f(x.p)
def S(*fs): return lambda p: reduce(partial(sbind, p), fs, nothing(p))
def P(*fs): return lambda p: reduce(pbind, fs, fx(nothing(p)))
def O(f): return P(f, nothing)
def Z(f):
    def fp(p):
        x = nothing(p)
        while x.s:
            x = bind(x, f)
        return tx(x)
    return fp
def M(f): return S(f, Z(f))
def N(f, g): return lambda p: (lambda x: R(False, p, []) if x.s else g(p))(f(p))
def post(pp, f): return lambda p: (lambda x: pp(x, p) if x.s else x)(f(p))
def postr(pp, f): return post(lambda x, p: R(x.s, x.p, pp(x.r)), f)
def flatten(r): return [y for x in r for y in flatten(x)] if isinstance(r, list) else [r]

def tokenize_char_source(char_source): return [T("c", ch) for ch in char_source]
def get_item(p, s): return R(False, p, []) if p == len(s) else R(True, p + 1, [s[p]])
def check_item(good, f): return post(lambda x, p: x if good(x.r[0]) else R(False, p, []), f)

def parse_lex(tokens):

    def get_token(p): return get_item(p, tokens)
    def check_token(good): return check_item(good, get_token)
    def make_token(t): return lambda r: [T(t, "".join([e.v for e in flatten(r)]))]
    def s(c): return check_token(lambda tc: c==tc.v)
    def N1(f): return N(f, get_token)
    def CC(pr): return check_token(lambda tc: pr(tc.v))

    any = get_token
    is_alpha = CC(str.isalpha)
    is_digit = CC(str.isdigit)
    is_space = CC(str.isspace)

    line_comment_end = P(S(s("\r"),s("\n")),S(s("\n"),s("\r")),s("\r"),s("\n"))
    line_comment_char = N1(P(s("\r"), s("\n")))
    block_comment_char = N1(S(s("*"),s("/")))
    quote = s("'")
    dquote = s('"')

    remove_types = ["space", "line_comment", "block_comment"]

    make_token_identifier = make_token("identifier")
    make_token_ysymbol = make_token("ysymbol")
    make_token_ykeyword = make_token("ykeyword")
    make_token_space = make_token("space")
    make_token_line_comment = make_token("line_comment")
    make_token_block_comment = make_token("block_comment")
    make_token_symbol = make_token("symbol")

    def lex(p): return Z(one_token)(p)
    def one_token(p): return P(postr(make_token_identifier,identifier),postr(make_token_space,space),postr(make_token_ysymbol,ysymbol),postr(make_token_ykeyword,ykeyword),postr(make_token_line_comment,line_comment),postr(make_token_block_comment,block_comment),postr(make_token_symbol,symbol))(p)
    def identifier(p): return S(identifier_first_char,Z(identifier_next_char))(p)
    def identifier_first_char(p): return P(is_alpha,s("_"))(p)
    def identifier_next_char(p): return P(identifier_first_char,is_digit)(p)
    def space(p): return M(is_space)(p)
    def ysymbol(p): return S(quote,any,quote)(p)
    def ykeyword(p): return S(dquote,identifier,dquote)(p)
    def symbol(p): return any(p)
    def line_comment(p): return S(s("/"),s("/"),Z(line_comment_char),line_comment_end)(p)
    def block_comment(p): return S(s("/"),s("*"),Z(block_comment_char),s("*"),s("/"))(p)

    return [e for e in flatten(lex(0).r) if e.t not in remove_types]

def parse_yacc(tokens):
    def get_token(p): return get_item(p, tokens)
    def check_token(good): return check_item(good, get_token)
    def ttype(type): return check_token(lambda t: t.t == type)
    def s(c): return postr(p1,check_token(lambda tc: c==tc.v))

    p1 = lambda r: [r[0].v]
    pzero = lambda r: ["Z({})".format(flatten(r)[0])]
    pmore = lambda r: ["M({})".format(flatten(r)[0])]
    poptional = lambda r: ["O({})".format(flatten(r)[0])]
    pskip = lambda r: [flatten(r)[1]]
    pcollect = lambda r: flatten(r)

    def pjoin(r):
        x = flatten(r)
        return ["".join(x)]

    def ps1(r):
        ch = r[0].v[1:-1]
        ret = "s('{}')".format(ch) if ch == '"' else 's("{}")'.format(ch)
        return [ret]

    def ps2(r):
        k = r[0].v[1:-1]
        ret = 'kword("{}")'.format(k)
        return [ret]

    def pseq(r):
        x = flatten(r)
        if len(x) == 1:
            ret = x[0]
        else:
            ret = "S({})".format(",".join(x))
        return [ret]

    def ppost(r):
        x = flatten(r)
        if len(x) == 2:
            ret = "postr({1},{0})".format(*x)
        else:
            ret = x[0]
        return [ret]

    def pcombine(r):
        x = flatten(r)
        if len(x) == 1:
            ret = x[0]
        else:
            ret = "P({})".format(",".join(x))
        return [ret]

    def pdef(r):
        ret ="    def {0}(p): return {2}(p)".format(*flatten(r))
        return [ret]

    def papply(r):
        x = flatten(r)
        ret = x[0]
        for func in x[1:]:
            ret = "postr({},{})".format(func, ret)
        return [ret]

    def add_used_terms(r):
        used_terms.add(r[0].v)
        return r
    def add_defined_terms(r):
        defined_terms.add(r[0].v)
        return r

    y_symbol = postr(ps1, ttype("ysymbol"))
    y_keyword = postr(ps2, ttype("ykeyword"))
    y_identifier = postr(p1, postr(add_used_terms, ttype("identifier")))
    y_entry_name = postr(p1, postr(add_defined_terms, ttype("identifier")))

    def y_grammar(p): return M(y_entry)(p)
    def y_entry(p): return postr(pdef,S(y_entry_name,s("="),y_entry_def,s(";")))(p)
    def y_entry_def(p): return postr(pcombine,S(y_sequence,y_or_sequences))(p)
    def y_or_sequences(p): return postr(pcollect,Z(y_or_sequence))(p)
    def y_or_sequence(p): return postr(pskip,S(s("|"),y_sequence))(p)
    def y_sequence(p): return postr(ppost,S(y_seq_objects,O(y_post_processing)))(p)
    def y_post_processing(p): return postr(pskip,S(p_post_op,y_processing))(p)
    def p_post_op(p): return postr(pjoin,S(s("-"),s(">")))(p)
    def y_seq_objects(p): return postr(pseq,M(y_seq_object))(p)
    def y_seq_object(p): return P(postr(pzero,S(y_term,s("*"))),postr(pmore,S(y_term,s("+"))),postr(poptional,S(y_term,s("?"))),postr(papply,S(y_term,M(y_apply))),y_term,y_symbol,postr(poptional,S(y_keyword,s("?"))),y_keyword)(p)
    def y_apply(p): return postr(pskip,S(s("."),y_func))(p)
    def y_func(p): return y_identifier(p)
    def y_term(p): return P(y_identifier,postr(pskip,S(s("("),y_entry_def,s(")"))))(p)
    def y_processing(p): return y_identifier(p)
    
    used_terms = set()
    defined_terms = set()
 
    result = y_grammar(0)

    undefined_terms = sorted(list(used_terms - defined_terms))
    print("Undefined Terms:")
    for e in undefined_terms: print(e)
    print()

    return R(result.s, result.p, flatten(result.r))

def run():
    with open("pyacc.txt") as fd: char_source = fd.read()
    tokens = tokenize_char_source(char_source)

    tokens = parse_lex(tokens)
    #for e in tokens: print(e)

    result = parse_yacc(tokens)
    print(len(tokens), result.s, result.p)
    for e in result.r: print(e)

if __name__ == "__main__":
    run()
