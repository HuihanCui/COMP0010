import unittest
import os
from io import StringIO
from unittest.mock import patch
import sys
import subprocess
sys.path.append('./src')
from shellFileProcessing import FileProcessingCommand


class TestFileProcessingCommand(unittest.TestCase):

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
        p = subprocess.run(["mkdir", "test_dir"], stdout=subprocess.DEVNULL)
        if p.returncode != 0:
            print("error: failed to create test_dir directory")
            exit(1)
        file_setup = ";".join(
            [
                "cd test_dir",
                "echo 'Line 1\nLine 2\nLine 3' > test_file.txt",
                "echo '\n \n \n\tABC' > test_file2.txt",
                "echo "" > empty_file.txt",
                "echo 'Spécial\nCharactérs\n123\n' > special_chars.txt",
                "mkdir nested_dir",
                "echo 'Nested line 1\nNested line 2' > nested_dir/nested_file.txt"
            ]
        )
        self.setFileUp(file_setup)
        os.chdir("test_dir")
        self.test_dir = "test_dir"
        self.command = FileProcessingCommand([], [], {"inputFile": None, "contents": None})

    def tearDown(self):
        os.chdir("/")
        os.chdir("comp0010")
        p = subprocess.run(["rm", "-r", "test_dir"], stdout=subprocess.DEVNULL)

        if p.returncode != 0:
            print("error: failed to remove test_dir directory")
            exit(1)

    def test_get_contents_from_file(self):
        filename = 'test_file.txt'
        expected = ['Line 1\n', 'Line 2\n', 'Line 3\n']
        self.assertEqual(self.command.get_contents(filename), expected)

    def test_handle_exceptions(self):
        with self.assertRaises(ValueError):
            self.command.handle_exceptions(lambda: 1 / 0)

    def test_contents_with_newline(self):
        contents = ['Line 1', 'Line 2']
        expected = ['Line 1', 'Line 2\n']
        self.assertEqual(self.command.contents_with_newline(contents), expected)

    def test_expand_globbing(self):
        args = ['*.txt']
        expected = sorted([f for f in os.listdir('.') if f.endswith('.txt')])
        self.assertEqual(sorted(self.command.expand_globbing(args)), expected)

    def test_read_file(self):
        filename = os.path.dirname(os.path.realpath("test_file.txt")) + "/test_file.txt"
        expected = ['Line 1\n', 'Line 2\n', 'Line 3\n']
        self.assertEqual(self.command.read_file([filename]), expected)

    def test_read_file_newlines(self):
        filename = os.path.dirname(os.path.realpath("test_file2.txt")) + "/test_file2.txt"
        expected = ['\n', ' \n', ' \n', '\tABC\n']
        self.assertEqual(self.command.read_file([filename]), expected)

    def test_read_file_with_error(self):
        with self.assertRaises(ValueError) as context:
            self.command.read_file(['nonexistent_file.txt'])
        self.assertIn('Error reading file', str(context.exception))

    def test_read_file_nonexistent(self):
        with self.assertRaises(ValueError):
            self.command.read_file(['nonexistent_file.txt'])

    def test_read_file_empty(self):
        expected = ['\n']
        self.assertEqual(self.command.read_file(['empty_file.txt']), expected)

    def test_read_file_special_chars(self):
        filename = os.path.dirname(os.path.realpath("special_chars.txt")) + "/special_chars.txt"
        expected = ['Spécial\n', 'Charactérs\n', '123\n', '\n']
        self.assertEqual(self.command.read_file([filename]), expected)

    def test_read_multiple_files_contents(self):
        filenames = ['test_file.txt', 'empty_file.txt']
        expected = [['test_file.txt', 'Line 1\n', 'Line 2\n', 'Line 3\n'], ['empty_file.txt', '\n']]
        self.assertEqual(self.command.read_multiple_files(filenames, True), expected)

    def test_read_multiple_files_empty(self):
        filenames = []
        expected = None
        self.assertEqual(self.command.read_multiple_files(filenames, True), expected)

    def test_read_multiple_files_nonexistent(self):
        with self.assertRaises(ValueError):
            self.command.read_multiple_files(['nonexistent_file.txt'], True)

    def test_read_multiple_files_nested_directory(self):
        filenames = ['nested_dir/nested_file.txt']
        expected = [['nested_dir/nested_file.txt', 'Nested line 1\n', 'Nested line 2\n']]
        self.assertEqual(self.command.read_multiple_files(filenames, True), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_from_stdin(self, mock_stdin):
        mock_stdin.write("Input line\n")
        mock_stdin.seek(0)
        expected = ['Input line\n']
        self.assertEqual(self.command.read_from_stdin(), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_from_stdin_empty(self, mock_stdin):
        mock_stdin.write("")
        mock_stdin.seek(0)
        self.assertEqual(self.command.read_from_stdin(), [])

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_from_stdin_multiple_lines(self, mock_stdin):
        mock_stdin.write("Line 1\nLine 2\n")
        mock_stdin.seek(0)
        expected = ['Line 1\n', 'Line 2\n']
        self.assertEqual(self.command.read_from_stdin(), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_from_stdin_no_newline(self, mock_stdin):
        mock_stdin.write("Single line")
        mock_stdin.seek(0)
        expected = ['Single line\n']
        self.assertEqual(self.command.read_from_stdin(), expected)

    def test_read_stdin_with_contents(self):
        self.command.contents = ["Contents\n"]
        expected = ["Contents\n"]
        self.assertEqual(self.command.read_stdin(), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_stdin_with_input_redirection(self, mock_stdin):
        mock_stdin.write('Line 1\n')
        mock_stdin.write('Line 2\n')
        mock_stdin.write('Line 3\n')
        mock_stdin.seek(0)
        self.command.inputFile = ("test_file.txt", True)
        expected = ['Line 1\n', 'Line 2\n', 'Line 3\n']
        self.assertEqual(self.command.read_stdin(), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_stdin_no_input_file(self, mock_stdin):
        mock_stdin.write("Input\n")
        mock_stdin.seek(0)
        self.command.inputFile = None
        expected = ['Input\n']
        self.assertEqual(self.command.read_stdin(), expected)

    def test_read_stdin_input_file(self):
        self.command.inputFile = ("test_file.txt", False)
        expected = ['Line 1\n', 'Line 2\n', 'Line 3\n']
        self.assertEqual(self.command.read_stdin(), expected)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_stdin_with_empty_contents(self, mock_stdin):
        self.command.contents = []
        self.assertEqual(self.command.read_stdin(), [])


if __name__ == '__main__':
    unittest.main()
