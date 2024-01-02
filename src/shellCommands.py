import re
import os
from os import listdir
from shellDecorator import commandRegister, unsafe_command_decorator, commandRegistry
from shellFileProcessing import FileProcessingCommand
from shellExceptions import InvalidCommandlineArgument, ErrorExectuingApplication


# Handle the help message
@commandRegister("--help")
class HelpCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def execute(self):
        help_message = """
        Shell Guide:
        Commands: Call (basic), Sequence (';'), Pipe('|')
        Quoting: Single, double, and backquotes for command substitution
        IO Redirection: '<' for input redirection, '>' for output redirection
        Globbing: Uses '*' for filename expansion

        Application Syntax:
        cd [PATH]: Changes directory, PATH is a relative path
        pwd: Outputs the current working directory
        ls [PATH]: Lists files in PATH (or current directory if PATH is omitted)
        cat [FILE]...: Concatenates and displays FILE(s), or stdin if no file is given
        echo [ARG]...: Prints arguments to stdout
        head -n [NUM] [FILE]: Displays first NUM lines of FILE, default is 10 lines
        tail -n [NUM] [FILE]: Displays last NUM lines of FILE, default is 10 lines
        grep [PATTERN] [FILE]...: Searches for PATTERN in FILE(s) or stdin
        find [PATH] -name [PATTERN]: Searches PATH for files matching PATTERN
        sort [-r] [FILE]: Sorts FILE or stdin, -r for reverse order
        uniq [-i] [FILE]: Filters consecutive duplicate lines in FILE or stdin, -i for ignoring case
        cut -b [RANGES] [FILE]: Cuts out specified byte RANGES (numbers or ranges connected by '-') from FILE or stdin
        Unsafe version: '_' + command name (e.g. _pwd)
        """
        try:
            self.out.append(help_message + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("--help", e)


# Handle the pwd command
@commandRegister("pwd")
class PwdCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def execute(self):
        if len(self.args) != 0:
            raise InvalidCommandlineArgument("pwd")

        try:
            self.out.append(os.getcwd() + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("pwd", e)


# Handle the cd command
@commandRegister("cd")
class CdCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def execute(self):
        try:
            if len(self.args) != 1:
                raise InvalidCommandlineArgument("cd")
            os.chdir(self.args[0])
        except Exception as e:
            raise ErrorExectuingApplication("cd", e)


# Handle the ls command
@commandRegister("ls")
class LsCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def get_directory(self):
        if len(self.args) == 0:
            return os.getcwd()
        elif len(self.args) == 1:
            return self.args[0]
        else:
            raise InvalidCommandlineArgument("ls")

    # Handle potential globbing in ls command
    def handle_globbing(self, pattern):
        expanded_paths = self.expand_globbing(pattern)
        paths = "\n".join(expanded_paths)
        self.out.append(paths if paths.endswith("\n") else paths + "\n")

    def list_directory(self, directory):
        for f in listdir(directory):
            if not f.startswith("."):
                self.out.append(f + "\n")

    def execute(self):
        try:
            lsdir = self.get_directory()
            if "*" in lsdir:
                self.handle_globbing([lsdir])
            else:
                self.list_directory(lsdir)
        except Exception as e:
            raise ErrorExectuingApplication("ls", e)


# Handle the echo command
@commandRegister("echo")
class EchoCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def has_globbing(self):
        return any("*" in arg for arg in self.args)

    def execute(self):
        try:
            globbing = " ".join(self.expand_globbing(self.args))
            message = globbing if self.has_globbing() else " ".join(self.args)
            self.out.append(message + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("echo", e)


# Read one File or standard input
class LineBasedCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)
        self.lineNum = 10
        self.fileName = None

    # Parse the arguments further
    def parse_args(self):
        if len(self.args) > 1 and self.args[0] == '-n':
            try:
                self.lineNum = int(self.args[1])
                self.fileName = self.args[2] if len(self.args) > 2 else None
            except ValueError:
                raise InvalidCommandlineArgument("head/tail")
        elif self.args:
            self.fileName = self.args[0]

    def process_lines(self, contents):
        raise NotImplementedError("Must be implemented by subclasses")

    def execute(self):
        self.parse_args()
        try:
            contents = self.get_contents(self.fileName)
            for line in self.process_lines(contents):
                self.out.append(line if line.endswith("\n") else line + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("head/tail", e)


@commandRegister("head")
class HeadCommand(LineBasedCommand):
    def process_lines(self, contents):
        return contents[:self.lineNum]


@commandRegister("tail")
class TailCommand(LineBasedCommand):
    def process_lines(self, contents):
        return contents[len(contents) - self.lineNum:]


@commandRegister("cat")
class CatCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def execute(self):
        try:
            contents = []
            if self.args:
                for filename in self.args:
                    contents.extend(self.read_file([filename]))
            else:
                contents = self.read_stdin()

            for line in contents:
                self.out.append(line if line.endswith("\n") else line + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("cat", e)


@commandRegister("cut")
class CutCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def parse_ranges(self, args):
        # Extract and parse the byte range argument
        ranges_str = args[args.index('-b') + 1]
        ranges = []
        for part in ranges_str.split(','):
            if '-' in part:
                start, end = part.split('-')
                start = int(start) - 1 if start else 0
                end = int(end) if end else None
                ranges.append((start, end))
            else:
                index = int(part) - 1
                ranges.append((index, index + 1))
        return self.merge_ranges(ranges)

    def merge_ranges(self, ranges):
        # Merge to get the unioned ranges
        ranges.sort(key=lambda x: (x[0], x[1] if x[1] is not None else float('inf')))
        merged = []
        for start, end in ranges:
            part = merged[-1][1] if merged else None
            if not merged or (part is not None and start > part):
                merged.append((start, end))
            else:
                part = merged[-1][0]
                merged[-1] = (part, None if end is None else max(merged[-1][1], end))
        return merged

    def execute(self):
        if len(self.args) < 2 or self.args[0] != '-b':
            raise InvalidCommandlineArgument("cut")

        ranges = self.parse_ranges(self.args)
        filename = self.args[-1] if len(self.args) > 2 else None
        try:
            contents = self.get_contents(filename)
            for line in contents:
                result = []
                for start, end in ranges:
                    result.append(line[start: end] if end else line[start:])
                res = ''.join(result)
                self.out.append(res if res.endswith("\n") else res + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("cut", e)


@commandRegister("uniq")
class UniqCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def parse_args(self):
        self.ignore_case = '-i' in self.args
        valid_arg_num = 1
        if self.ignore_case:
            self.filename = self.args[-1] if len(self.args) > 1 else None
            valid_arg_num = 2
        else:
            self.filename = self.args[-1] if len(self.args) == 1 else None

        if len(self.args) > valid_arg_num:
            raise InvalidCommandlineArgument("uniq")

    def execute(self):
        try:
            self.parse_args()
            contents = self.get_contents(self.filename)
            # Compare each line with the previous line
            last_line = None
            for line in contents:
                line_to_compare = line.lower() if self.ignore_case else line
                if line_to_compare != last_line:
                    self.out.append(line)
                    last_line = line_to_compare
        except Exception as e:
            raise ErrorExectuingApplication("uniq", e)


@commandRegister("sort")
class SortCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def parse_args(self):
        self.reverse = '-r' in self.args
        valid_arg_num = 1
        if self.reverse:
            self.filename = self.args[-1] if len(self.args) > 1 else None
            valid_arg_num = 2
        else:
            self.filename = self.args[-1] if len(self.args) == 1 else None

        if len(self.args) > valid_arg_num:
            raise InvalidCommandlineArgument("sort")

    def execute(self):
        try:
            self.parse_args()
            contents = self.get_contents(self.filename)
            self.out.extend(sorted(contents, reverse=self.reverse))
        except Exception as e:
            raise ErrorExectuingApplication("sort", e)


# Read multiple Files or standard input
@commandRegister("grep")
class GrepCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def grep_files(self, pattern, filenames):
        contents = self.read_multiple_files(filenames, True)
        isMultipleFiles = len(contents) > 1
        for file in contents:
            filename = file[0]
            if isMultipleFiles:
                self.grep_and_append(file[1:], pattern, filename)
            else:
                self.grep_and_append(file, pattern)

    def grep_stdin(self, pattern):
        contents = self.read_stdin()
        self.grep_and_append(contents, pattern)

    def grep_and_append(self, contents, pattern, filename=None):
        for line in contents:
            if re.search(pattern, line):
                self.out.append(f"{filename}:{line}" if filename else line)

    def execute(self):
        if len(self.args) < 1:
            raise InvalidCommandlineArgument("grep")

        pattern = self.args[0]
        filenames = self.args[1:]
        try:
            if filenames:
                self.grep_files(pattern, filenames)
            else:
                self.grep_stdin(pattern)
        except Exception as e:
            raise ErrorExectuingApplication("grep", e)


@commandRegister("find")
class FindCommand(FileProcessingCommand):
    def __init__(self, args, out, extra_dict):
        super().__init__(args, out, extra_dict)

    def execute(self):
        invalid_args_a = (2 <= len(self.args) <= 3)
        invalid_args_b = (len(self.args) == 3 and self.args[1] != '-name')
        if not invalid_args_a or invalid_args_b:
            raise InvalidCommandlineArgument("find")

        path = self.args[0] if len(self.args) == 3 else None
        pattern = [self.args[-1]]

        try:
            contents = self.read_multiple_files(pattern, False, path)
            for filename in contents:
                self.out.append(filename + "\n")
        except Exception as e:
            raise ErrorExectuingApplication("find", e)

    def find_and_append(self, pattern, path):
        contents = self.read_multiple_files([pattern], False, path)
        for filename in contents:
            self.out.append(filename + "\n")


# Unsafe versions
@commandRegister("_pwd")
class UnsafePwdCommand(unsafe_command_decorator(PwdCommand)):
    pass


@commandRegister("_cd")
class UnsafeCdCommand(unsafe_command_decorator(CdCommand)):
    pass


@commandRegister("_ls")
class UnsafeLsCommand(unsafe_command_decorator(LsCommand)):
    pass


@commandRegister("_echo")
class UnsafeEchoCommand(unsafe_command_decorator(EchoCommand)):
    pass


@commandRegister("_head")
class UnsafeHeadCommand(unsafe_command_decorator(HeadCommand)):
    pass


@commandRegister("_tail")
class UnsafeTailCommand(unsafe_command_decorator(TailCommand)):
    pass


@commandRegister("_cat")
class UnsafeCatCommand(unsafe_command_decorator(CatCommand)):
    pass


@commandRegister("_cut")
class UnsafeCutCommand(unsafe_command_decorator(CutCommand)):
    pass


@commandRegister("_uniq")
class UnsafeUniqCommand(unsafe_command_decorator(UniqCommand)):
    pass


@commandRegister("_sort")
class UnsafeSortCommand(unsafe_command_decorator(SortCommand)):
    pass


@commandRegister("_grep")
class UnsafeGrepCommand(unsafe_command_decorator(GrepCommand)):
    pass


@commandRegister("_find")
class UnsafeFindCommand(unsafe_command_decorator(FindCommand)):
    pass
