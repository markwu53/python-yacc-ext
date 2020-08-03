from pbase import *
import plexdata
import pyaccdata
import pdata
from plexafter import *
from pyaccafter import *

def run():
    pdata.phase = "lex"
    with open("pyacc2.txt") as fd: plexdata.char_source = fd.read()
    token_source = lexer()
    #for e in token_source: print(e)

    pdata.phase = "yacc"
    pyaccdata.defined_terms = set()
    pyaccdata.token_source = token_source
    result = parse()

    for e in flatten(result.r): print(e)

if __name__ == "__main__":
    run()
