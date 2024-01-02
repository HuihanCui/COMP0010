import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('./src')
from shellCommandFactory import CommandFactory, commandRegistry


class TestCommandFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up any class-level fixtures (e.g., global configurations)
        pass

    def setUp(self):
        # Create a CommandFactory instance before each test
        self.cmdline = "echo Test"
        self.out = []
        self.extra_dict = {
            "inputFile": None, "outputFile": None, "content": None
        }
        self.factory = CommandFactory(self.cmdline, self.out, self.extra_dict)

    def tearDown(self):
        # Clean up after each test method
        pass

    @classmethod
    def tearDownClass(cls):
        # Clean up any class-level fixtures
        pass

    def test_output_redirection(self):
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            self.factory.extra_dict["outputFile"] = ("test_output.txt", False)
            self.factory.output_redirection()
            mock_file.assert_called_with("test_output.txt", "w")
            self.assertEqual(self.factory.out, [])

    def test_parse_command_valid(self):
        commandname, args = self.factory.parse_command()
        self.assertEqual(commandname, "echo")
        self.assertEqual(args, ["Test"])

    def test_parse_command_invalid(self):
        self.factory.cmdline = ""
        with self.assertRaises(ValueError) as context:
            self.factory.parse_command()
        self.assertIn("No application provided", str(context.exception))

    def test_execute_command_known_command(self):
        with patch.dict(commandRegistry, {'echo': MagicMock()}):
            self.factory.execute_command('echo', ['Test'])

    def test_execute_command_unknown_command(self):
        with self.assertRaises(ValueError) as context:
            self.factory.execute_command('unknown_cmd', ['Test'])
        self.assertIn("Unknown application", str(context.exception))

    def test_execute_command_unsafe_version_command(self):
        with patch.dict(commandRegistry, {'_echo': MagicMock()}):
            self.factory.execute_command('_echo', ['Test'])

    def test_other_execute_command(self):
        with patch.dict(commandRegistry, {'ls': MagicMock()}):
            self.factory.execute_command('ls', [])

    def test_other_execute_command_with_arguments(self):
        with patch.dict(commandRegistry, {'cd': MagicMock()}):
            self.factory.execute_command('cd', ['-b', '1-3'])

    def test_execute(self):
        with patch.object(self.factory, 'parse_command', return_value=('echo', ['Test'])) as mock_parse:
            with patch.object(self.factory, 'execute_command') as mock_execute:
                self.factory.execute()
                mock_parse.assert_called_once()
                mock_execute.assert_called_once_with('echo', ['Test'])

    def test_invalid_arguments(self):
        with patch.object(CommandFactory, 'execute'):
            factory = CommandFactory('head invalid name', [], {})
            with self.assertRaises(ValueError):
                factory.execute_command('head', ['invalid', 'name'])

    def test_invalid_command_name(self):
        with patch.object(CommandFactory, 'execute') as mock_execute:
            factory = CommandFactory('invalid name', [], {})
            factory.parse_command()
            self.assertEqual(mock_execute.call_count, 0)


if __name__ == '__main__':
    unittest.main()
