import unittest
from unittest.mock import patch
import sys
sys.path.append('./src')
from shell import Comp0010Shell


class TestComp0010Shell(unittest.TestCase):

    def setUp(self):
        self.shell = Comp0010Shell()

        with patch('shell.CommandParser') as MockCommandParser:
            self.shell.eval("echo test")
            MockCommandParser.assert_called_with("echo test", self.shell.out)
            MockCommandParser.return_value.parse.assert_called_once()

    def test_run_command_line(self):
        with patch('shell.print') as mock_print:
            self.shell.run_command_line("echo test")
            mock_print.assert_called_with("test\n", end="")

    def test_run_shell_with_args(self):
        test_args = ["shell.py", "-c", "echo test"]
        with patch.object(sys, 'argv', test_args):
            with patch('shell.Comp0010Shell.run_command_line') as mock_run_command_line:
                self.shell.run_shell()
                mock_run_command_line.assert_called_with("echo test")

    def test_run_shell_with_incorrect_args(self):
        test_args = ["shell.py", "-c"]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(ValueError) as context:
                self.shell.run_shell()
            self.assertEqual(str(context.exception), "Wrong number of program arguments")

    def test_run_shell_with_unexpected_arg(self):
        test_args = ["shell.py", "-x", "echo test"]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(ValueError) as context:
                self.shell.run_shell()
            self.assertEqual(str(context.exception), "Unexpected program argument -x")


if __name__ == '__main__':
    unittest.main()
