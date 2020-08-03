from collections import namedtuple

R = namedtuple("R", "s p r")
T = namedtuple("T", "t v")

def S(*fs):
    def fp(p):
        y = []
        for i,f in enumerate(fs):
            x = f(p if i == 0 else x.p)
            if not x.s:
                return R(False, p, [])
            y.append(x.r)
        return R(True, x.p, y)
    return fp

def P(*fs):
    def fp(p):
        for f in fs:
            x = f(p)
            if x.s:
                return x
        return R(False, p, [])
    return fp

#def M(f): return S(f, O(lambda p: M(f)(p)))
def M(f):
    def fp(p):
        x = f(p)
        y = []
        if not x.s:
            return x
        while x.s:
            y.append(x.r)
            x = f(x.p)
        return R(True, x.p, y)
    return fp

def nothing(p): return R(True, p, [])
def O(f): return P(f, nothing)
def Z(f): return O(M(f))
def N(f, g): return lambda p: (lambda x: R(False, p, []) if x.s else g(p))(f(p))
def post(pp, f): return lambda p: (lambda x: pp(x, p) if x.s else x)(f(p))
def postr(pp, f): return post(lambda x, p: R(x.s, x.p, pp(x.r)), f)
def flatten(r): return [y for x in r for y in flatten(x)] if isinstance(r, list) else [r]
def get_item(p, s): return R(False, p, []) if p == len(s) else R(True, p + 1, [s[p]])
def check_item(good, f): return post(lambda x, p: x if good(x.r[0]) else R(False, p, []), f)
