from pygments.lexer import RegexLexer
from pygments.token import Text, Operator, Keyword, String, Error


class Comp0010ShellLexer(RegexLexer):
    name = 'Comp0010Shell'
    aliases = ['comp0010shell']
    filenames = ['*.comp0010shell']

    tokens = {
        'root': [
            # Whitespace
            (r'\s+', Text),

            # Commands
            (r'\b(cd|pwd|ls|cat|echo|head|tail|grep|find|sort|uniq|cut|\
                --help|_cd|_pwd|_ls|_cat|_echo|_head|_tail|_grep|_find|\
                _sort|_uniq|_cut)\b', Keyword),

            # Operators
            (r'[;|<>]', Operator),

            # Redirections
            (r'(\>\>?)', Operator),
            (r'(\>\&|\&\>)', Operator),
            (r'(\>\&\d|\d\>\&)', Operator),
            (r'(\>\>|2\>\&1)', Operator),

            # Strings
            (r'"(\\\\|\\"|[^"])*"', String.Double),
            (r"'(\\\\|\\'|[^'])*'", String.Single),

            # Backquoted commands
            (r'`(.*?)`', String.Backtick),

            # Miscellaneous
            (r'[^\s;|<>]+', Text),

            # Catch-all for errors
            (r'.', Error),
        ]
    }
