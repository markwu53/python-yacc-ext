from pbase import *
import plexdata
import pyaccdata
import pdata
from plexafter import *
from pyaccafter import *

def gencode(phase):
    pdata.phase = phase
    with open("p{}.txt".format(phase)) as fd: plexdata.char_source = fd.read()
    token_source = lexer()
    #for e in token_source: print(e)
    used_terms = {term for t,term in token_source if t == "identifier"}
    pyaccdata.token_source = token_source
    pyaccdata.defined_terms = set()
    result = parse()
    for e in flatten(result.r): print(e)
    undefined_terms = sorted(list(used_terms-pyaccdata.defined_terms))
    for e in undefined_terms: print(e)

if __name__ == "__main__":
    gencode("lex")
    gencode("yacc")
