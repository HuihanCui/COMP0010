import unittest
from unittest.mock import patch
import sys
sys.path.append('./src')
from shellVisitor import ClassifierVisitor, SeqElement, PipeElement, CallElement, SeqCommand, PipeCommand, CallCommand


class TestVisitorClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up any class-level fixtures
        pass

    def setUp(self):
        # Create instance of each element class with mock data
        self.seq_element = SeqElement([{"command": "seq_command"}], [])
        self.pipe_element = PipeElement([{"command": "pipe_command"}], [])
        self.call_element = CallElement([{"command": "call_command"}], [])

    def tearDown(self):
        # Clean up after each test method
        pass

    @classmethod
    def tearDownClass(cls):
        # Clean up any class-level fixtures
        pass

    def test_seq_element_accept(self):
        visitor = ClassifierVisitor()
        with patch.object(visitor, 'visitSeq') as mock_visit:
            self.seq_element.accept(visitor)
            mock_visit.assert_called_once()

    def test_pipe_element_accept(self):
        visitor = ClassifierVisitor()
        with patch.object(visitor, 'visitPipe') as mock_visit:
            self.pipe_element.accept(visitor)
            mock_visit.assert_called_once()

    def test_call_element_accept(self):
        visitor = ClassifierVisitor()
        with patch.object(visitor, 'visitCall') as mock_visit:
            self.call_element.accept(visitor)
            mock_visit.assert_called_once()

    def test_seq_element_entry_exception_handling(self):
        with patch.object(SeqCommand, 'execute', side_effect=Exception("Error")):
            with self.assertRaises(ValueError) as context:
                self.seq_element.entry()
            self.assertIn("Error executing sequence command", str(context.exception))

    def test_pipe_element_entry_exception_handling(self):
        with patch.object(PipeCommand, 'execute', side_effect=Exception("Error")):
            with self.assertRaises(ValueError) as context:
                self.pipe_element.entry()
            self.assertIn("Error executing pipeline command", str(context.exception))

    def test_call_element_entry_exception_handling(self):
        with patch.object(CallCommand, 'execute', side_effect=Exception("Error")):
            with self.assertRaises(ValueError) as context:
                self.call_element.entry()
            self.assertIn("Error executing call command", str(context.exception))

    def test_other_command(self):
        seq_element = SeqElement([], [])
        with patch.object(PipeCommand, 'execute') as mock_execute:
            seq_element.entry()
            mock_execute.assert_not_called()

    def test_invalid_parsed_dict(self):
        seq_element = CallCommand({"command": ""}, [])
        with self.assertRaises(ValueError) as context:
            seq_element.execute()
        self.assertIn("Unexpected error", str(context.exception))

    def test_pipe_element_with_single_command(self):
        pipe_element = PipeElement([{"command": "pipe_command"}], [])
        with patch.object(PipeCommand, 'execute') as mock_execute:
            pipe_element.entry()
            mock_execute.assert_called_once()

    def test_seq_element_with_multiple_commands(self):
        commands = [{'seq': [{'call': {'before_backquote': 'echo foo', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo foo'}}, {'call': {'before_backquote': 'echo bar', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo bar'}}]}]
        seq_element = SeqElement(commands, [])
        with patch.object(CallCommand, 'execute') as mock_execute:
            seq_element.entry()
            self.assertEqual(mock_execute.call_count, 2)

    def test_pipe_element_with_two_commands(self):
        commands = [{'pipe': [{'call': {'before_backquote': 'echo foo', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo foo'}}, {'call': {'before_backquote': 'echo bar', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo bar'}}]}]
        pipe_element = PipeElement(commands, [])
        with patch.object(CallCommand, 'execute') as mock_execute:
            pipe_element.entry()
            self.assertEqual(mock_execute.call_count, 2)

    def test_pipe_element_with_multiple_commands(self):
        commands = [{'pipe': [{'pipe': [{'call': {'before_backquote': 'echo foo', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo foo'}}, {'call': {'before_backquote': 'echo bar', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo bar'}}]}, {'call': {'before_backquote': 'echo abc', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo abc'}}]}]
        pipe_element = PipeElement(commands, [])
        with patch.object(CallCommand, 'execute') as mock_execute:
            pipe_element.entry()
            self.assertEqual(mock_execute.call_count, 3)

    def test_command_substitution(self):
        with patch.object(CallCommand, 'execute') as mock_execute:
            call_command = CallCommand({}, [])
            call_command.process_backquote('echo foo', {})
            self.assertEqual(mock_execute.call_count, 0)

    def test_complex_command_substitution(self):
        with patch.object(CallCommand, 'execute') as mock_execute:
            call_command = CallCommand({}, [])
            call_command.process_backquote([{'seq': [{'call': {'before_backquote': 'echo foo', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo foo'}}, {'call': {'before_backquote': 'echo bar', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo bar'}}]}], {})
            self.assertEqual(mock_execute.call_count, 2)

    def test_call_with_complex_command_substitution(self):
        with patch.object(CallCommand, 'execute') as mock_execute:
            commands = {'before_backquote': 'echo ', 'backquote': 'echo foo', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo `echo foo`'}
            call_element = CallCommand(commands, [])
            call_element.execute()
            self.assertEqual(mock_execute.call_count, 1)

    def test_invalid_pipe(self):
        commands = [{'notaType': [{'call': {'before_backquote': 'echo foo', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo foo'}}, {'call': {'before_backquote': 'echo bar', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo bar'}}]}]
        seq_element = SeqElement(commands, [])
        with patch.object(CallCommand, 'execute'):
            with self.assertRaises(ValueError):
                seq_element.entry()

    def test_call_io(self):
        params = [('input', 'input.txt', False), ('output', 'output.txt', False)]
        call_command = CallCommand({}, [])
        inputs, outputs = call_command.handle_io_redirection(params)
        self.assertEqual(inputs, ('input.txt', False))
        self.assertEqual(outputs, ('output.txt', False))

    def test_call_io_input_exception(self):
        params = [('input', 'input1.txt', False), ('input', 'input2.txt', False)]
        call_command = CallCommand({}, [])
        with self.assertRaises(ValueError):
            call_command.handle_io_redirection(params)

    def test_call_io_output_exception(self):
        params = [('output', 'output1.txt', False), ('output', 'output2.txt', False)]
        call_command = CallCommand({}, [])
        with self.assertRaises(ValueError):
            call_command.handle_io_redirection(params)


if __name__ == '__main__':
    unittest.main()
