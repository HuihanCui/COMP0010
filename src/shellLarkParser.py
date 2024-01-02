from lark import Lark, Transformer


# Define the transformer to process the parse tree
class ShellCommandTransformer(Transformer):
    # Define methods for each grammar rule
    def command(self, args):
        return {"command": args}

    def seq(self, args):
        return {"seq": args}

    def call(self, args):
        return {"call": args}

    def pipe(self, args):
        return {"pipe": args}

    def quoted(self, args):
        return {"quoted": args}

    def singlequoted(self, args):
        content = []
        for arg in args:
            content.append(arg)
        return {"single_quoted": content}

    def doublequoted(self, args):
        content = []
        for arg in args:
            content.append(arg)
        return {"double_quoted": content}

    def backquoted(self, args):
        content = []
        for arg in args:
            content.append(arg)
        return {"backquoted": content}

    def inner(self, args):
        return {"inner": args}

    def normal(self, args):
        return {"normal": args}

    def io_redirection(self, args):
        return {"io_redirection": args}

    def input_redirection(self, args):
        return {"input_redirection": args}

    def output_redirection(self, args):
        return {"output_redirection": args}

    def heredoc_redirection(self, args):
        return {"heredoc_redirection": args}

    def append_redirection(self, args):
        return {"append_redirection": args}

    def FILENAME(self, args):
        return {"FILENAME": args}


# Define the grammar for the parsing command line
LARK_GRAMMAR = r"""
    command: pipe | seq | call
    seq: command ";" _WS? command
    call: (normal | quoted | io_redirection)*
    pipe: (call "|" _WS? call) | (pipe "|" _WS? call)

    normal: /[^\n'\"`;|<>]+/

    quoted: singlequoted | doublequoted | backquoted
    singlequoted: "'" (inner | doublequoted | backquoted)* "'"
    doublequoted: "\"" (inner | singlequoted | backquoted)* "\""
    backquoted: "`" (inner | singlequoted | doublequoted)* "`"

    inner: /[^'"`\n<>]+/

    io_redirection: input_redirection | output_redirection | append_redirection | heredoc_redirection
    input_redirection: "<" _WS? filename
    output_redirection: ">" _WS? filename
    append_redirection: ">>" _WS? filename
    heredoc_redirection: "<<" _WS? filename

    filename: /[\w\.\-\/]+/

    _WS: /[ \t]+/

    %import common.WS
    %import common.NEWLINE
    %ignore NEWLINE
"""


def larkParser(grammar, cmdline):
    try:
        parser = Lark(grammar, start="command", parser="earley")
        # Parse the command line
        parsed = parser.parse(cmdline)
        # Transform the parse tree
        transformed = ShellCommandTransformer().transform(parsed)
    except Exception as e:
        raise ValueError(f"Error using lark parser: {e}")
    return transformed["command"][0]
