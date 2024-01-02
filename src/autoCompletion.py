from prompt_toolkit.completion import Completer, Completion
import glob

COMMANDS = ["cd", "pwd", "ls", "cat", "echo", "head", "tail", "grep", "find",
            "sort", "uniq", "cut", "--help", "_cd", "_pwd", "_ls", "_cat",
            "_echo", "_head", "_tail", "_grep",
            "_find", "_sort", "_uniq", "_cut"]


# A customized autocomplete class
class ShellCompleter(Completer):
    def __init__(self, commands):
        self.commands = commands

    # Do autocomplete after getting the input words before cursor
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()

        # Command completions
        if '/' not in word_before_cursor:
            for command in self.commands:
                if command.startswith(word_before_cursor):
                    yield Completion(command, -len(word_before_cursor))

        # File and directory completions
        else:
            for filename in glob.glob(word_before_cursor + '*'):
                yield Completion(filename, -len(word_before_cursor))
