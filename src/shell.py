import sys
import os
from collections import deque
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer

from shellParsing import CommandParser
from syntaxHighlighting import Comp0010ShellLexer
from autoCompletion import ShellCompleter, COMMANDS


class Comp0010Shell:
    def __init__(self):
        self.out = deque()
        self.commands = COMMANDS
        self.session = PromptSession(
            lexer=PygmentsLexer(Comp0010ShellLexer),
            completer=ShellCompleter(self.commands)
        )

    # Call parser to parse the input command
    def eval(self, cmdline):
        parser = CommandParser(cmdline, self.out)
        parser.parse()

    # Get results after applications and print them out
    def run_command_line(self, cmdline):
        self.eval(cmdline)
        while len(self.out) > 0:
            print(self.out.popleft(), end="")

    # Support interactive and non-interactive shell execution
    def run_shell(self):
        # Command line argument processing
        argsNum = len(sys.argv) - 1
        if argsNum > 0:
            if argsNum != 2:
                raise ValueError("Wrong number of program arguments")
            if sys.argv[1] != "-c":
                raise ValueError(f"Unexpected program argument {sys.argv[1]}")
            self.run_command_line(sys.argv[2])
        else:
            # Interactive shell
            while True:
                try:
                    # Use readline's prompt mechanism
                    cmdline = self.session.prompt(os.getcwd() + "> ")
                    self.run_command_line(cmdline)
                except EOFError:
                    # Exit the shell on Ctrl-D (EOF)
                    print("End of file (EOF), exiting...")
                    print("The end")
                    break
                except KeyboardInterrupt:
                    # Exit the shell on Ctrl-C (Interrupt)
                    print("KeyboardInterrupted...")
                    print("The end")
                    break
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)


# Create a shell class and run
if __name__ == "__main__":
    shell = Comp0010Shell()
    shell.run_shell()
