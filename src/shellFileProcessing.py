import sys
import os
from glob import glob
import fnmatch


class FileProcessingCommand:
    def __init__(self, args, out, extra_dict):
        self.args = args
        self.out = out
        self.inputFile = extra_dict.get("inputFile")
        self.contents = extra_dict.get("contents")

    def contents_with_newline(self, contents):
        if contents and not contents[-1].endswith("\n"):
            contents[-1] += "\n"
        return contents

    def expand_globbing(self, args):
        expanded_args = []
        for arg in args:
            if "*" in arg:
                expanded_args.extend(glob(arg))
            else:
                expanded_args.append(arg)
        return expanded_args

    def read_file(self, filename, name=False):
        filenames = self.expand_globbing(filename)
        fileContents = []
        for filename in filenames:
            try:
                with open(filename, 'r') as file:
                    lines = self.contents_with_newline(file.readlines())
                    if name:
                        lines.insert(0, filename)
                        fileContents.append(lines)
                    else:
                        fileContents.extend(lines)
            except IOError as e:
                raise ValueError(f"Error reading file: {e}")
        return fileContents

    def read_multiple_files(self, match_name, contents, directory=None):
        if not match_name:
            return None

        fileContents = []
        if contents:
            fileContents = self.read_file(match_name, True)
        else:
            # Set the base directory for searching
            baseDir = directory if directory else os.getcwd()
            # Walk through the directory tree
            for root, _, files in os.walk(baseDir):
                for pattern in match_name:
                    for filename in fnmatch.filter(files, pattern):
                        fullPath = os.path.join(root, filename)
                        relPath = os.path.relpath(fullPath, baseDir)
                        # Adjust the path relative to the given directory
                        path = directory + "/" + relPath if directory else "./" + relPath
                        fileContents.append(path)

        return fileContents

    def read_from_stdin(self, detect_string=None):
        stdin = []
        try:
            for line in sys.stdin:
                if detect_string and line.strip() == detect_string:
                    break
                stdin.append(line)
        except EOFError:
            raise ValueError("Error reading from stdin")
        return self.contents_with_newline(stdin)

    def read_stdin(self):
        # Process the contents from the previous command
        if self.contents:
            return self.contents_with_newline(self.contents)

        # Deal with Input Redirection and Here Documents
        if self.inputFile:
            if self.inputFile[1]:
                return self.read_from_stdin(self.inputFile[0])
            else:
                return self.read_file([self.inputFile[0]])

        # Nornally read from stdin
        return self.read_from_stdin()

    def get_contents(self, filename):
        if filename:
            contents = self.read_file([filename])
        else:
            contents = self.read_stdin()
        last = contents[-1]
        contents[-1] = last if last.endswith("\n") else last + "\n"
        return contents

    def handle_exceptions(self, operation):
        try:
            return operation()
        except FileNotFoundError as e:
            raise ValueError(f"File not found: {e}")
        except PermissionError as e:
            raise ValueError(f"Permission denied: {e}")
        except Exception as e:
            raise ValueError(f"Error: {e}")
