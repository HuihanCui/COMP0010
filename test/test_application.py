import unittest
from collections import deque
import os
import subprocess
from io import StringIO
from unittest.mock import patch
import sys
sys.path.append('./src')
from shellCommands import HelpCommand, PwdCommand, LsCommand, CdCommand, CatCommand, EchoCommand, HeadCommand, TailCommand, GrepCommand, UniqCommand, CutCommand, FindCommand, SortCommand, UnsafeCdCommand, UnsafeLsCommand, UnsafePwdCommand, UnsafeCatCommand, UnsafeEchoCommand, UnsafeHeadCommand, UnsafeTailCommand, UnsafeGrepCommand, UnsafeCutCommand, UnsafeFindCommand, UnsafeSortCommand, UnsafeUniqCommand
from shellExceptions import ErrorExectuingApplication, InvalidCommandlineArgument

class TestPwd(unittest.TestCase):
    def test_pwd(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        pwdClass = PwdCommand([], out, extra_dict)
        pwdClass.execute()
        self.assertEqual(out.popleft(), os.getcwd() + "\n")

    def test_pwd_with_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        pwdClass = PwdCommand(["args"], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            pwdClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid pwd arguments")


class TestHelp(unittest.TestCase):
    def test_help(self):
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
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        helpClass = HelpCommand(["--help"], out, extra_dict)
        helpClass.execute()
        self.assertEqual(out.popleft(), help_message + "\n")


class TestLsCommand(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "echo \"''\" > test.txt",
                "mkdir dir1",
                "mkdir -p dir2/subdir",
                "echo AAA > dir1/file1.txt",
                "echo BBB >> dir1/file1.txt",
                "echo AAA >> dir1/file1.txt",
                "echo CCC > dir1/file2.txt",
                "for i in {1..20}; do echo $i >> dir1/longfile.txt; done",
                "echo AAA > dir2/subdir/file.txt",
                "echo aaa >> dir2/subdir/file.txt",
                "echo AAA >> dir2/subdir/file.txt",
                "touch dir1/subdir/.hidden",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        list = ["rm", "-r", "unittests"]
        p = subprocess.run(list, stdout=subprocess.DEVNULL)

        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_ls_no_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand([], out, extra_dict)
        lsClass.execute()
        self.assertEqual(list(out), ["test.txt\n", "dir2\n", "dir1\n"])

    def test_ls_one_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["dir1"], out, extra_dict)
        lsClass.execute()
        expected = ["file2.txt\n", "file1.txt\n", "longfile.txt\n"]
        self.assertEqual(list(out), expected)

    def test_ls_multiple_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["dir1", "dir2"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            lsClass.execute()
        expected = "Error executing ls application: Invalid ls arguments"
        self.assertEqual(f"{context.exception}", expected)

    def test_ls_invalid_arg(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["dir3"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            lsClass.execute()
        expected = "Error executing ls application: [Errno 2] No such file or directory: 'dir3'"
        self.assertEqual(f"{context.exception}", expected)

    def test_ls_hidden_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["dir2/subdir"], out, extra_dict)
        lsClass.execute()
        self.assertEqual(out.popleft(), "file.txt\n")

    def test_ls_globbing(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["*.txt"], out, extra_dict)
        lsClass.execute()
        self.assertEqual(out.popleft(), "test.txt\n")


class TestCd(unittest.TestCase):
    @classmethod
    def prepare(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        filesystem_setup = ";".join(
            [
                "cd unittests",
                "mkdir dir1",
                "mkdir dir2",
            ]
        )
        self.prepare(filesystem_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_cd(self):
        old_file_path = os.getcwd()
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cdClass = CdCommand(["dir1"], out, extra_dict)
        cdClass.execute()
        self.assertEqual(old_file_path + "/dir1", os.getcwd())

    def test_cd_no_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cdClass = CdCommand([], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            cdClass.execute()
        expected = "Error executing cd application: Invalid cd arguments"
        self.assertEqual(f"{context.exception}", expected)

    def test_cd_multiple_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cdClass = CdCommand(["dir1", "dir2"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            cdClass.execute()
        expected = "Error executing cd application: Invalid cd arguments"
        self.assertEqual(f"{context.exception}", expected)

    def test_cd_fake_directory(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cdClass = CdCommand(["dir3"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            cdClass.execute()
        expected = "Error executing cd application: [Errno 2] No such file or directory: 'dir3'"
        self.assertEqual(f"{context.exception}", expected)


class TestCat(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "echo 'AAA' > test1.txt",
                "echo BBB > test2.txt",
                "echo CCC > test3.txt",
                "mkdir dir1",
                "echo DDD > dir1/.test3.txt",
                "echo 'HELLO' > dir1/hello.txt",
                "mkdir dir2",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cat_stdin(self, mock_stdin):
        mock_stdin.write("Hello\nWorld\n")
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        catClass = CatCommand([], out, extra_dict)
        catClass.execute()
        self.assertEqual(list(out), ["Hello\n", "World\n"])

    def test_cat_invalid_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        catClass = CatCommand(["dir3/test.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            catClass.execute()
        expected = "Error executing cat application: Error reading file: [Errno 2] No such file or directory: 'dir3/test.txt'"
        self.assertEqual(f"{context.exception}", expected)

    def test_cat_invalid_folder(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        catClass = CatCommand(["dir5"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            catClass.execute()
        expected = "Error executing cat application: Error reading file: [Errno 2] No such file or directory: 'dir5'"
        self.assertEqual(f"{context.exception}", expected)

    def test_cat_valid_folder(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        catClass = CatCommand(["dir1"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            catClass.execute()
        expected = "Error executing cat application: Error reading file: [Errno 21] Is a directory: 'dir1'"
        self.assertEqual(f"{context.exception}", expected)

    def test_cat_two_files(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        catClass = CatCommand(["test1.txt", "test2.txt"], out, extra_dict)
        catClass.execute()
        self.assertEqual(list(out), ["AAA\n", "BBB\n"])


class TestEcho(unittest.TestCase):
    def test_echo_no_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        echoClass = EchoCommand([""], out, extra_dict)
        echoClass.execute()
        self.assertEqual(out.popleft(), "\n")

    def test_echo_with_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        echoClass = EchoCommand(["foo bar"], out, extra_dict)
        echoClass.execute()
        self.assertEqual(out.popleft(), "foo bar\n")

    def test_echo_globbing(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        lsClass = LsCommand(["*.txt"], out, extra_dict)
        lsClass.execute()
        self.assertEqual(list(out), ["requirements.txt\n"])


class TestHead(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = ["/bin/bash", "-c", cmdline]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "for i in {1..20}; do echo $i >> numbers.txt; done",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_head_fake_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["unittests/test.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            headClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: 'unittests/test.txt'"
        self.assertEqual(f"{context.exception}", expected)

    def test_head_n0(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["-n", "0", "numbers.txt"], out, extra_dict)
        headClass.execute()
        self.assertFalse(out)

    def test_head_n_negative(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["-n", "-2", "numbers.txt"], out, extra_dict)
        headClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(1, 19)])

    def test_head_n5(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["-n", "5", "numbers.txt"], out, extra_dict)
        headClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(1, 6)])

    @patch('sys.stdin', new_callable=StringIO)
    def test_head_stdin(self, mock_stdin):
        nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        numbers = "\n".join(nums)
        mock_stdin.write(numbers)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand([], out, extra_dict)
        headClass.execute()
        nums = ["1\n", "2\n", "3\n", "4\n", "5\n", "6\n", "7\n", "8\n", "9\n", "10\n"]
        self.assertEqual(list(out), nums)

    def test_head_two_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["15", "numbers.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            headClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '15'"
        self.assertEqual(f"{context.exception}", expected)

    def test_head_wrong_n(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-number", "5", "numbers.txt"]
        headClass = HeadCommand(args, out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            headClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '-number'"
        self.assertEqual(f"{context.exception}", expected)

    def test_head_n_string_number(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["-n", "five", "numbers.txt"], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            headClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid head/tail arguments")

    def test_head_n_over_limit(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        headClass = HeadCommand(["-n", "30", "numbers.txt"], out, extra_dict)
        headClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(1, 21)])


class TestTail(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)

        file_setup = ";".join(
            [
                "cd unittests",
                "for i in {1..20}; do echo $i >> numbers.txt; done",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_tail_fake_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand(["unittests/test.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            tailClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: 'unittests/test.txt'"
        self.assertEqual(f"{context.exception}", expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_tail_stdin(self, mock_stdin):
        nums = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        numbers = "\n".join(nums)
        mock_stdin.write(numbers)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand([], out, extra_dict)
        tailClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(3, 13)])

    def test_tail_two_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand(["15", "numbers.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            tailClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '15'"
        self.assertEqual(f"{context.exception}", expected)

    def test_tail_wrong_flag(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-number", "5", "numbers.txt"]
        tailClass = TailCommand(args, out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            tailClass.execute()
        expected = "Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '-number'"
        self.assertEqual(f"{context.exception}", expected)

    def test_tail_n_flag_string(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand(["-n", "five", "numbers.txt"], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            tailClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid head/tail arguments")

    def test_tail_n_flag_over_limit(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand(["-n", "30", "numbers.txt"], out, extra_dict)
        tailClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(11, 21)])

    def test_tail_n(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        tailClass = TailCommand(["-n", "4", "numbers.txt"], out, extra_dict)
        tailClass.execute()
        self.assertEqual(list(out), [f"{i}\n" for i in range(17, 21)])


class TestGrep(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "echo AAA > test1.txt",
                "echo ABB >> test1.txt",
                "echo CCC >> test1.txt",
                "echo BBB > test2.txt",
                "echo CCC > test3.txt",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    @patch('sys.stdin', new_callable=StringIO)
    def test_grep_find_matches_from_stdin_with_match_all(self, mock_stdin):
        lines = "\n".join(["AAA", "BBB", "CCC"])
        mock_stdin.write(lines)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand(["..."], out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), ["AAA\n", "BBB\n", "CCC\n"])

    @patch('sys.stdin', new_callable=StringIO)
    def test_grep_find_matches_from_stdin_with_partial_match(self, mock_stdin):
        lines = "\n".join(["AAA", "BBB", "CCC"])
        mock_stdin.write(lines)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand(["A.."], out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), ["AAA\n"])

    @patch('sys.stdin', new_callable=StringIO)
    def test_grep_find_matches_from_stdin_with_no_match(self, mock_stdin):
        lines = "\n".join(["AAA", "BBB", "CCC"])
        mock_stdin.write(lines)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand(["D.."], out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), [])

    def test_grep_with_partial_match1(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand(["A..", "test1.txt"], out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), ["AAA\n", "ABB\n"])

    def test_grep_with_partial_match2(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand(["D..", "test1.txt"], out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), [])

    def test_find_matches_from_files_with_multiple_files(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["...", "test2.txt", "test3.txt"]
        grepClass = GrepCommand(args, out, extra_dict)
        grepClass.execute()
        self.assertEqual(list(out), ["test2.txt:BBB\n", "test3.txt:CCC\n"])

    def test_grep_with_no_arguments(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        grepClass = GrepCommand([], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            grepClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid grep arguments")


class TestCut(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "mkdir dir1",
                "echo AAA > dir1/file1.txt",
                "echo BBB >> dir1/file1.txt",
                "echo AAA >> dir1/file1.txt",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_cut(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "1", "dir1/file1.txt"], out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["A\n", "B\n", "A\n"])

    def test_cut_interval(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "2-3", "dir1/file1.txt"], out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["AA\n", "BB\n", "AA\n"])

    def test_cut_open_interval(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "1-", "dir1/file1.txt"], out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["AAA\n", "BBB\n", "AAA\n"])

    def test_cut_overlapping(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-b", "2-,3-", "dir1/file1.txt"]
        cutClass = CutCommand(args, out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["AA\n", "BB\n", "AA\n"])

    def test_cut_read_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-b", "2-", "dir1/file1.txt"]
        cutClass = CutCommand(args, out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["AA\n", "BB\n", "AA\n"])

    @patch('sys.stdin', new_callable=StringIO)
    def test_cut_stdin(self, mock_stdin):
        text = "ABC\n"
        mock_stdin.write(text)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "2-"], out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["BC\n"])

    @patch('sys.stdin', new_callable=StringIO)
    def test_cut_union(self, mock_stdin):
        text = "ABC\n"
        mock_stdin.write(text)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "-1,2-"], out, extra_dict)
        cutClass.execute()
        self.assertEqual(list(out), ["ABC\n"])

    def test_cut_no_option(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["dir1/file1.txt"], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            cutClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid cut arguments")

    def test_cut_fake_directory(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        cutClass = CutCommand(["-b", "1", "dir1/file5.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            cutClass.execute()
        expected = "Error executing cut application: Error reading file: [Errno 2] No such file or directory: 'dir1/file5.txt'"
        self.assertEqual(f"{context.exception}", expected)


class TestFind(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd unittests",
                "echo AAA > test1.txt",
                "echo BBB > test2.txt",
                "echo CCC > test3.txt",
                "for i in {1..20}; do echo $i >> numbers.txt; done",
                "mkdir dir1",
                "echo DDD > dir1/.test3.txt",
                "echo HELLO > dir1/hello.txt",
                "mkdir dir2",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_find(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        findClass = FindCommand(["-name", "hello.txt"], out, extra_dict)
        findClass.execute()
        self.assertEqual(list(out), ["./dir1/hello.txt\n"])

    def test_find_dir(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["dir1", "-name", "hello.txt"]
        findClass = FindCommand(args, out, extra_dict)
        findClass.execute()
        self.assertEqual(list(out), ["dir1/hello.txt\n"])

    def test_find_dir_star(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        findClass = FindCommand(["dir1", "-name", "*.txt"], out, extra_dict)
        findClass.execute()
        self.assertEqual(list(out), ["dir1/hello.txt\n", "dir1/.test3.txt\n"])

    def test_find_no_matches(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["unittests", "-name", "test4.txt"]
        findClass = FindCommand(args, out, extra_dict)
        findClass.execute()
        self.assertEqual(list(out), [])

    def test_find_no_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        findClass = FindCommand([], out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            findClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid find arguments")

    def test_find_invalid_pattern(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["dir1", "-notName", "pattern"]
        findClass = FindCommand(args, out, extra_dict)
        with self.assertRaises(InvalidCommandlineArgument) as context:
            findClass.execute()
        self.assertEqual(f"{context.exception}", "Invalid find arguments")


class TestUniq(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        self.text1 = ("HELLO\nhello\nhello\nhello\nhello\nHello\nHEllo\nHeLlo\nHeLLo\nhello\nhEllO\nhElLo")
        file_setup = ";".join(
            [
                "cd unittests",
                f"echo '{self.text1}' > hello.txt",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_uniq_file_not_case_insensitive(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        uniqClass = UniqCommand(["hello.txt"], out, extra_dict)
        uniqClass.execute()
        texts = ["HELLO\n", "hello\n", "Hello\n", "HEllo\n", "HeLlo\n", "HeLLo\n", "hello\n", "hEllO\n", "hElLo\n"]
        self.assertEqual(list(out), texts)

    def test_uniq_file_case_insensitive(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        uniqClass = UniqCommand(["-i", "hello.txt"], out, extra_dict)
        uniqClass.execute()
        self.assertEqual(list(out), ["HELLO\n"])

    @patch('sys.stdin', new_callable=StringIO)
    def test_uniq_stdin(self, mock_stdin):
        text = "HELLO\nhello\nHello\nHEllo\nHeLlo\nHeLLo\nhello\n"
        mock_stdin.write(text)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        uniqClass = UniqCommand(["-i"], out, extra_dict)
        uniqClass.execute()
        self.assertEqual(list(out), ["HELLO\n"])

    def test_uniq_incorrect_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        uniqClass = UniqCommand(["test.txt", "-i"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            uniqClass.execute()
        self.assertEqual(f"{context.exception}", "Error executing uniq application: Error reading file: [Errno 2] No such file or directory: '-i'")


class TestSort(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        self.test1 = ("bbc\ncake\napple")
        self.alphabet = ('a\nb\nc\nd\ne\nf\ng\nh\ni\nj\nk\nl\nm\n'
                         'n\no\np\nq\nr\ns\nt\nu\nv\nw\nx\ny\nz')
        file_setup = ";".join(
            [
                "cd unittests",
                f"echo '{self.test1}' > test1.txt",
                f"echo '{self.alphabet}' > alphabet.txt",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_sort_read_file_fake_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        uniqClass = UniqCommand(["unittests/test4.txt"], out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            uniqClass.execute()
        self.assertEqual(f"{context.exception}", "Error executing uniq application: Error reading file: [Errno 2] No such file or directory: 'unittests/test4.txt'")

    def test_sort_read_file(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        sortClass = SortCommand(["test1.txt"], out, extra_dict)
        sortClass.execute()
        self.assertEqual(list(out), ["apple\n", "bbc\n", "cake\n"],)

    def test_sort_reverse(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        sortClass = SortCommand(["-r", "alphabet.txt"], out, extra_dict)
        sortClass.execute()
        self.assertListEqual(list(out), [
            "z\n",
            "y\n",
            "x\n",
            "w\n",
            "v\n",
            "u\n",
            "t\n",
            "s\n",
            "r\n",
            "q\n",
            "p\n",
            "o\n",
            "n\n",
            "m\n",
            "l\n",
            "k\n",
            "j\n",
            "i\n",
            "h\n",
            "g\n",
            "f\n",
            "e\n",
            "d\n",
            "c\n",
            "b\n",
            "a\n",
        ]
        )

    @patch('sys.stdin', new_callable=StringIO)
    def test_sort_stdin(self, mock_stdin):
        text = "c\no\nn\nt\ne\nn\nt\ns\n"
        mock_stdin.write(text)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        sortClass = SortCommand([], out, extra_dict)
        sortClass.execute()
        results = ["c\n", "e\n", "n\n", "n\n", "o\n", "s\n", "t\n", "t\n"]
        self.assertEqual(list(out), results)

    @patch('sys.stdin', new_callable=StringIO)
    def test_sort_stdin_reverse(self, mock_stdin):
        text = "c\no\nn\nt\ne\nn\nt\ns\n"
        mock_stdin.write(text)
        mock_stdin.seek(0)
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        sortClass = SortCommand(["-r"], out, extra_dict)
        sortClass.execute()
        results = ["t\n", "t\n", "s\n", "o\n", "n\n", "n\n", "e\n", "c\n"]
        self.assertEqual(list(out), results)

    def test_sort_multiple_args(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["huh", "-r", "unittests/test1.txt"]
        sortClass = SortCommand(args, out, extra_dict)
        with self.assertRaises(ErrorExectuingApplication) as context:
            sortClass.execute()
        self.assertEqual(f"{context.exception}", "Error executing sort application: Invalid sort arguments")


class TestUnsafeApplication(unittest.TestCase):
    @classmethod
    def setFileUp(cls, cmdline):
        args = [
            "/bin/bash",
            "-c",
            cmdline,
        ]
        p = subprocess.run(args, capture_output=True)
        return p.stdout.decode()

    def setUp(self):
        p = subprocess.run(["mkdir", "unittests"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create unittest directory")
            exit(1)
        self.text1 = ("HELLO\nhello\nhello\nhello\nhello\nHello\nHEllo\nHeLlo\nHeLLo\nhello\nhEllO\nhElLo")
        file_setup = ";".join(
            [
                "cd unittests",
                f"echo '{self.text1}' > hello.txt",
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("unittests")

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(
            ["rm", "-r", "unittests"], stdout=subprocess.DEVNULL
            )
        if p.returncode != 0:
            print("error: failed to remove unittests directory")
            exit(1)

    def test_unsafe_pwd(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _pwdClass = UnsafePwdCommand(["nonexist"], out, extra_dict)
        _pwdClass.execute()
        self.assertEqual(out.popleft(), "Error: Invalid pwd arguments\n")

    def test_unsafe_cd(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _cdClass = UnsafeCdCommand([], out, extra_dict)
        _cdClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing cd application: Invalid cd arguments\n")

    def test_unsafe_ls(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _LsClass = UnsafeLsCommand(["nonexist"], out, extra_dict)
        _LsClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing ls application: [Errno 2] No such file or directory: 'nonexist'\n")

    def test_unsafe_echo(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _echoClass = UnsafeEchoCommand(["echo"], out, extra_dict)
        _echoClass.execute()
        self.assertEqual(out.popleft(), "echo\n")

    def test_unsafe_head(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-Num", "Five", "File"]
        _headClass = UnsafeHeadCommand(args, out, extra_dict)
        _headClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '-Num'\n")

    def test_unsafe_tail(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-Num", "Five", "File"]
        _tailClass = UnsafeTailCommand(args, out, extra_dict)
        _tailClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing head/tail application: Error reading file: [Errno 2] No such file or directory: '-Num'\n")

    def test_unsafe_sort(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _sortClass = UnsafeSortCommand(["File.java"], out, extra_dict)
        _sortClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing sort application: Error reading file: [Errno 2] No such file or directory: 'File.java'\n")

    def test_unsafe_uniq(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _uniqClass = UnsafeUniqCommand(["test.txt", "-i"], out, extra_dict)
        _uniqClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing uniq application: Error reading file: [Errno 2] No such file or directory: '-i'\n")

    def test_unsafe_grep(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        args = ["-Num", "Five", "File"]
        _grepClass = UnsafeGrepCommand(args, out, extra_dict)
        _grepClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing grep application: Error reading file: [Errno 2] No such file or directory: 'Five'\n")

    def test_unsafe_cat(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _catClass = UnsafeCatCommand(["-Num", "Five", "File"], out, extra_dict)
        _catClass.execute()
        self.assertEqual(out.popleft(), "Error: Error executing cat application: Error reading file: [Errno 2] No such file or directory: '-Num'\n")

    def test_unsafe_cut(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _cutClass = UnsafeCutCommand(["-Num", "Five", "File"], out, extra_dict)
        _cutClass.execute()
        self.assertEqual(out.popleft(), "Error: Invalid cut arguments\n")

    def test_unsafe_find(self):
        out = deque()
        extra_dict = {"inputFile": None, "outputFile": None, "contents": None}
        _findClass = UnsafeFindCommand([], out, extra_dict)
        _findClass.execute()
        self.assertEqual(out.popleft(), "Error: Invalid find arguments\n")


if __name__ == '__main__':
    unittest.main()
