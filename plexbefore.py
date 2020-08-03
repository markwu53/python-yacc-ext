from pbase import *
from plexbase import *

any = get_char
is_alpha = CC(str.isalpha)
is_digit = CC(str.isdigit)
is_space = CC(str.isspace)

line_comment_end = P(S(C("\r"),C("\n")),S(C("\n"),C("\r")),C("\r"),C("\n"))
line_comment_char = N1(P(C("\r"), C("\n")))
block_comment_char = N1(S(C("*"),C("/")))
quote = C("'")
dquote = C('"')

remove_types = ["space", "line_comment", "block_comment"]
