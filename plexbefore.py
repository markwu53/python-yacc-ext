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

make_token_identifier = make_token("identifier")
make_token_ysymbol = make_token("ysymbol")
make_token_ykeyword = make_token("ykeyword")
make_token_space = make_token("space")
make_token_line_comment = make_token("line_comment")
make_token_block_comment = make_token("block_comment")
make_token_symbol = make_token("symbol")