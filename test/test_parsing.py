import unittest
import sys
sys.path.append('./src')
from shellParsing import CommandParser
from lark import Tree, Token


class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.cmdline = "echo 'Hello World'"
        self.out = []
        self.parser = CommandParser(self.cmdline, self.out)

    def tearDown(self):
        pass

    def test_initialize(self):
        self.parser.initialize()
        self.assertIsNone(self.parser.disqualified)
        self.assertEqual(self.parser.backquote, "")
        self.assertEqual(self.parser.before_backquote, "")
        self.assertEqual(self.parser.after_backquote, "")
        self.assertEqual(self.parser.io_redirection, [])

    def test_parse_quoted(self):
        quoted = [{"double_quoted": [{"inner": ["Hello "]}, {"single_quoted": [{"inner": [" World "]}]}, {"double_quoted": [{"inner": ["Python"]}]}]}]
        result = self.parser.parse_quoted(quoted)
        self.assertEqual(result, 'Hello \' World \'"Python"')

    def test_parse_io_redirection_input(self):
        io_redirection = [{'input_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'input.txt')])]}]
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [('input', 'input.txt', False)])

    def test_parse_io_redirection_output(self):
        io_redirection = [{'output_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'output.txt')])]}]
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [('output', 'output.txt', False)])
 
    def test_parse_io_redirection_both(self):
        io_redirection = [{'input_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'input.txt')])]},
                          {'output_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'output.txt')])]}]
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [('input', 'input.txt', False), ('output', 'output.txt', False)])

    def test_parse_io_redirection_heredoc(self):
        io_redirection = [{'heredoc_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'input.txt')])]}]
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [('input', 'input.txt', True)])

    def test_parse_io_redirection_append(self):
        io_redirection = [{'append_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'output.txt')])]}]
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [('output', 'output.txt', True)])

    def test_parse_io_redirection_last_in_pipe(self):
        io_redirection = [{'output_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_2', 'o.txt')])]}]
        with self.assertRaises(ValueError) as context:
            self.parser.parse_io_redirection(io_redirection, True, False)
        self.assertIn("Output redirection in the middle of a pipeline", str(context.exception))

    def test_parse_io_redirection_none(self):
        io_redirection = {}
        result = self.parser.parse_io_redirection(io_redirection)
        self.assertEqual(result, [])

    def test_process_command_part_normal(self):
        part = {"normal": [Token('__ANON_0', 'echo Hello')]}
        result = self.parser.process_command_part(part, False, False)
        self.assertEqual(result, "echo Hello")

    def test_process_command_part_quoted(self):
        part = {'quoted': [{'double_quoted': [{'inner': [Token('__ANON_1', 'hello')]}]}]}
        result = self.parser.process_command_part(part, False, False)
        self.assertEqual(result, 'hello')

    def test_process_command_part_io_redirection(self):
        part = {'io_redirection': [{'output_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_4', 'o.txt')])]}]}
        result = self.parser.process_command_part(part, False, False)
        self.assertEqual(result, "")

    def test_parsed_command_list_with_call(self):
        command_structure = {"call": [{"normal": [Token('__ANON_0', 'echo Hello')]}]}
        result = []
        self.parser.parsed_command_list(command_structure, result)
        self.assertEqual(result, [{"call": {"before_backquote": "echo Hello", "backquote": "", "after_backquote": "", "disqualified": None, "io_redirection": [], "command": "echo Hello"}}])

    def test_parsed_command_list_with_call_back_quote(self):
        command_structure = {"call": [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo hello')]}]}]}]}
        result = []
        self.parser.parsed_command_list(command_structure, result)
        self.assertEqual(result, [{'call': {'before_backquote': 'echo ', 'backquote': [{'call': {'before_backquote': 'echo hello', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo hello'}}], 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo `echo hello`'}}])

    def test_parsed_command_list_with_call_seq(self):
        command_structure = {'seq': [{'command': [{'call': [{'normal': [Token('__ANON_0', 'echo hello ')]}]}]}, {'command': [{'call': [{'normal': [Token('__ANON_0', 'echo world')]}]}]}]}
        result = []
        self.parser.parsed_command_list(command_structure, result)
        self.assertEqual(result, [{'seq': [{'call': {'before_backquote': 'echo hello', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo hello'}}, {'call': {'before_backquote': 'echo world', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo world'}}]}])

    def test_parsed_command_list_with_call_back_pipe(self):
        command_structure = {'pipe': [{'call': [{'normal': [Token('__ANON_0', 'echo hello ')]}]}, {'call': [{'normal': [Token('__ANON_0', 'echo world')]}]}]}
        result = []
        self.parser.parsed_command_list(command_structure, result)
        self.assertEqual(result, [{'pipe': [{'call': {'before_backquote': 'echo hello', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo hello'}}, {'call': {'before_backquote': 'echo world', 'backquote': '', 'after_backquote': '', 'disqualified': None, 'io_redirection': [], 'command': 'echo world'}}]}])

    def test_nested_quoting_parsing(self):
        command_structure = [{'double_quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo ')]}, {'single_quoted': [{'inner': [Token('__ANON_1', 'hello')]}]}]}]}]
        parsed = self.parser.parse_quoted(command_structure)
        self.assertEqual(parsed, "`echo 'hello'`")

    def test_nested_back_quoting_parsing(self):
        command_structure = [{'backquoted': [{'inner': [Token('__ANON_1', 'echo ')]}, {'double_quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo abc')]}]}]}]}]
        with self.assertRaises(ValueError):
            self.parser.parse_quoted(command_structure)

    def test_disqualified_back_quoting(self):
        command_structure = [{'single_quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo abc')]}]}]}]
        parsed = self.parser.parse_quoted(command_structure)
        self.assertEqual(parsed, "`echo abc`")

    def test_parse_exception(self):
        with self.assertRaises(ValueError):
            self.parser.cmdline = "echo '"
            self.parser.parse()


if __name__ == '__main__':
    unittest.main()
