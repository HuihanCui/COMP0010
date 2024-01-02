import unittest
import sys
sys.path.append('./src')
from autoCompletion import ShellCompleter, COMMANDS
from prompt_toolkit.document import Document


class TestShellCompleter(unittest.TestCase):
    def setUp(self):
        self.completer = ShellCompleter(COMMANDS)

    def test_command_completion(self):
        # Test for command completion
        document = Document(text='ec', cursor_position=2)
        completions = list(self.completer.get_completions(document, None))
        self.assertTrue(any(c.text == 'echo' for c in completions))

    def test_no_completion_for_non_matching_command(self):
        # Test when there's no matching command
        document = Document(text='xyz', cursor_position=3)
        completions = list(self.completer.get_completions(document, None))
        self.assertEqual(len(completions), 0)

    def test_file_directory_completion(self):
        document = Document(text='./', cursor_position=2)
        completions = list(self.completer.get_completions(document, None))
        self.assertTrue(len(completions) > 0)

    def test_partial_command_completion(self):
        document = Document(text='gr', cursor_position=2)
        completions = list(self.completer.get_completions(document, None))
        self.assertTrue(any(c.text == 'grep' for c in completions))


# Run the tests
if __name__ == '__main__':
    unittest.main()
