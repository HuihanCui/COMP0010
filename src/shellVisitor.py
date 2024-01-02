from abc import ABC, abstractmethod
from collections import deque
from shellCommandFactory import CommandFactory


# Parser strategy
class CommandClassifier:
    def __init__(self):
        self.parsers = {
            "seq": SeqElement,
            "pipe": PipeElement,
            "call": CallElement,
        }

    def parse(self, parsed_dict, out):
        for cmdline in parsed_dict:
            for symbol, ecls in self.parsers.items():
                if symbol in cmdline:
                    return ecls(cmdline[symbol], out)
        raise ValueError("Invalid command line")


# The Visitor Class
class ClassifierVisitor():
    def visitPipe(self, element):
        element.entry()

    def visitSeq(self, element):
        element.entry()

    def visitCall(self, element):
        element.entry()


# Define the Element Interface
class ClassiferElement(ABC):
    def __init__(self, parsed_dict, out):
        self.parsed_dict = parsed_dict
        self.out = out

    @abstractmethod
    def accept(self, visitor):
        pass

    @abstractmethod
    def entry(self):
        pass

    def exceptions(self, classname, commandtype):
        try:
            classname(self.parsed_dict, self.out).execute()
        except Exception as e:
            raise ValueError(f"Error executing {commandtype} command: {e}")


# Sequence Element Class
class SeqElement(ClassiferElement):
    def accept(self, visitor):
        visitor.visitSeq(self)

    def entry(self):
        self.exceptions(SeqCommand, "sequence")


# Pipe Element Class
class PipeElement(ClassiferElement):
    def accept(self, visitor):
        visitor.visitPipe(self)

    def entry(self):
        self.exceptions(PipeCommand, "pipeline")


# Call Element Class
class CallElement(ClassiferElement):
    def accept(self, visitor):
        visitor.visitCall(self)

    def entry(self):
        self.exceptions(CallCommand, "call")


class CommandInterface():
    def __init__(self, commands, out):
        self.commands = commands
        self.out = out

    def execute(self):
        pass


# Sequence Command Class
class SeqCommand(CommandInterface):
    def execute(self):
        tempout = self.out.copy()
        for command in self.commands:
            element = CommandClassifier().parse([command], tempout)
            element.accept(ClassifierVisitor())
            self.out.extend(tempout)
            tempout.clear()


# Pipe Command Class
class PipeCommand(CommandInterface):
    def execute(self):
        for i, command in enumerate(self.commands):
            leftOut = deque()
            element = CommandClassifier().parse([command], leftOut)
            element.accept(ClassifierVisitor())

            # Check if the command is the last one in pipeline
            if i < len(self.commands) - 1:
                contents = list(leftOut)
                self.commands[i + 1]["call"]["contents"] = contents
        self.out.extend(leftOut)


# Call Command Class
class CallCommand(CommandInterface):
    def handle_io_redirection(self, io_redirection):
        input_redirection, output_redirection = None, None
        if io_redirection:
            for io in io_redirection:
                if io[0] == 'input':
                    if input_redirection:
                        raise ValueError('Multiple input redirections')
                    input_redirection = (io[1], io[2])
                elif io[0] == 'output':
                    if output_redirection:
                        raise ValueError('Multiple output redirections')
                    output_redirection = (io[1], io[2])
        return input_redirection, output_redirection

    def process_backquote(self, backquote, extra_dict):
        if isinstance(backquote, str):
            CommandFactory(backquote, self.out, extra_dict).execute()
        else:
            element = CommandClassifier().parse(backquote, self.out)
            element.accept(ClassifierVisitor())

        substituted = ''.join(self.out).rstrip("\n").replace("\n", " ")
        self.out.clear()
        return substituted

    def execute(self):
        before_backquote = self.commands.get("before_backquote")
        backquote = self.commands.get("backquote")
        after_backquote = self.commands.get("after_backquote")
        disqualified = self.commands.get("disqualified")
        io_redirection = self.commands.get("io_redirection")
        cmdline = self.commands.get("command")
        contents = self.commands.get("contents")
        in_redir, out_redir = self.handle_io_redirection(io_redirection)
        extra_dict = {
            "inputFile": in_redir,
            "outputFile": out_redir,
            "contents": contents
        }

        # Handle qualified command substitution
        if backquote and not disqualified:
            substituted = self.process_backquote(backquote, extra_dict)
            cmdline = before_backquote + substituted + after_backquote
        CommandFactory(cmdline, self.out, extra_dict).execute()
