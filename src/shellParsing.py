import re
from shellVisitor import CommandClassifier, ClassifierVisitor
from shellLarkParser import larkParser, LARK_GRAMMAR


class CommandParser():
    def __init__(self, cmdline, out):
        self.cmdline = cmdline
        self.out = out
        self.initialize()

    def initialize(self):
        self.disqualified = None
        self.backquote = ""
        self.before_backquote = ""
        self.after_backquote = ""
        self.io_redirection = []

    # Handle all quoting cases
    def parse_quoted(self, quoted):
        # Handle the internal parts of a nested quoting
        def process_nested_quotes(quoted_section, outer_quote_type, outmost):
            inner_contents = []
            for inner_q in quoted_section:
                # No more quoting inside
                if 'inner' in inner_q:
                    inner_q = inner_q['inner'][0]
                    inner_contents.append(inner_q)

                # There is a pair of single quotes inside
                elif 'single_quoted' in inner_q:
                    content = process_nested_quotes(inner_q['single_quoted'], 'single_quoted', outmost)
                    content = "'" + content + "'" if outer_quote_type != 'single' else content
                    inner_contents.append(content)

                # There is a pair of double quotes inside
                elif 'double_quoted' in inner_q:
                    content = process_nested_quotes(inner_q['double_quoted'], 'double_quoted', outmost)
                    content = '"' + content + '"' if outer_quote_type != 'double' else content
                    inner_contents.append(content)

                # There is a pair of backquotes inside
                elif 'backquoted' in inner_q:
                    backquoted_content = process_nested_quotes(inner_q['backquoted'], 'backquoted', outmost)
                    # Nested backquotes not allowed
                    if outer_quote_type == 'backquoted' or outmost == 'backquoted':
                        raise ValueError("Invalid command substitution syntax")
                    # Disqualify if backquotes inside single quotes
                    if outmost == 'single_quoted':
                        self.disqualified = True
                    inner_contents.append(backquoted_content)

            # Integrate the nested contents
            result = ''.join(inner_contents)
            if outer_quote_type == 'backquoted':
                self.backquote = result
                return "`" + result + "`"
            return result

        # Process the contents for the entire command
        contents = []
        for q in quoted:
            outer_quote_type = next(iter(q))
            contents.append(process_nested_quotes(q[outer_quote_type], outer_quote_type, outer_quote_type))

        processed_content = ''.join(contents)
        return processed_content

    def parse_io_redirection(self, io_redirection, in_pipeline=False, last_in_pipe=False):
        redirections = []
        # Classify four different types of IO redirection
        for io in io_redirection:
            if 'input_redirection' in io:
                io_tuple = ('input', str(io['input_redirection'][0].children[0]), False)
            elif 'output_redirection' in io:
                io_tuple = ('output', str(io['output_redirection'][0].children[0]), False)
            elif 'heredoc_redirection' in io:
                io_tuple = ('input', str(io['heredoc_redirection'][0].children[0]), True)
            elif 'append_redirection' in io:
                io_tuple = ('output', str(io['append_redirection'][0].children[0]), True)
            redirections.append(io_tuple)

        output_redirs = [r for r in redirections if r[0] == 'output']

        # Check for ambiguous output redirection in a pipeline
        if in_pipeline and not last_in_pipe and output_redirs:
            raise ValueError("Output redirection in the middle of a pipeline")

        return redirections

    # Reconstruct parts of command according to their corresponding type
    def process_command_part(self, part, in_pipe, last_in_pipe):
        reconstructed = ""
        if 'normal' in part:
            reconstructed += re.sub(r'\s+', ' ', part['normal'][0].value)
        elif 'quoted' in part:
            reconstructed += self.parse_quoted(part['quoted'])
        elif 'io_redirection' in part:
            io = self.parse_io_redirection(part['io_redirection'], in_pipe, last_in_pipe)
            self.io_redirection.extend(io)
        return reconstructed

    # Parse the entire command line input, may contain several commands
    def parsed_command_list(self, command_structure, result, in_pipe=False, last_in_pipe=False):
        # Only call commands are inputted
        if "call" in command_structure:
            reconstructed = ""
            for inner in command_structure['call']:
                reconstructed += self.process_command_part(inner, in_pipe, last_in_pipe)

            # Handle command substitution
            if self.backquote:
                quote_parts = reconstructed.split("`"+self.backquote+"`", 1)
                self.before_backquote = quote_parts[0]
                self.after_backquote = quote_parts[1] if len(quote_parts) > 1 else ""
            else:
                self.before_backquote = reconstructed

            reconstructed = reconstructed.lstrip(" \t")
            before = self.before_backquote.lstrip(" \t")
            # Build a dictionary for each command
            reconstructed_dict = {
                "before_backquote": before if self.backquote else before.rstrip(" \t"),
                "backquote": self.backquote,
                "after_backquote": self.after_backquote.rstrip(" \t"),
                "disqualified": self.disqualified,
                "io_redirection": self.io_redirection,
                "command": reconstructed if self.backquote else reconstructed.rstrip(" \t")
            }

            # Return the parser inside the backquote
            if self.backquote and not self.disqualified:
                substituition_json = larkParser(LARK_GRAMMAR, self.backquote)
                result2 = []
                self.initialize()
                self.parsed_command_list(substituition_json, result2)
                reconstructed_dict["backquote"] = result2

            result.append({"call": reconstructed_dict})
            self.initialize()

        # Handle multiple call commands of a sequence command
        if "seq" in command_structure:
            seq_result = []
            for command in command_structure["seq"]:
                self.parsed_command_list(command["command"][0], seq_result, in_pipe, last_in_pipe)
            result.append({"seq": seq_result})

        # Separate and handle call commands of a pipe command
        if "pipe" in command_structure:
            first_part = command_structure["pipe"][0]
            second_part = command_structure["pipe"][1]
            last_in_pipe = second_part == command_structure["pipe"][-1]

            pipe_result = []
            self.parsed_command_list(first_part, pipe_result, True, False)
            self.parsed_command_list(second_part, pipe_result, True, last_in_pipe)
            result.append({"pipe": pipe_result})

        return result

    def executeVistor(self, parsed_dict):
        parser = CommandClassifier()
        element = parser.parse(parsed_dict, self.out)
        visitor = ClassifierVisitor()
        element.accept(visitor)

    def parse(self):
        try:
            command_json = larkParser(LARK_GRAMMAR, self.cmdline)
            # Get the reconstructed command line
            cmdline_parsed_dict = []
            self.parsed_command_list(command_json, cmdline_parsed_dict)
            self.executeVistor(cmdline_parsed_dict)
        except Exception as e:
            raise ValueError(f"Error parsing command line: {e}\n")
