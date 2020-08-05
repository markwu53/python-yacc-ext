from pbase import *
from plexbase import *
from plexbefore import *
from plex import *

def lexer(): return [e for e in flatten(lex(0).r) if e.t not in remove_types]
