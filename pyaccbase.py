from pbase import get_item, check_item, R, post
import pyaccdata

def get_token(p): return get_item(p, pyaccdata.token_source)
def check_token(good): return check_item(good, get_token)
def ttype(type): return check_token(lambda t: t.t == type)
def s(a): return post(lambda x, p: x if x.r[0].v == a else R(False, p, []), ttype("symbol"))
