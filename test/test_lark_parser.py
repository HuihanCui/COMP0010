import unittest
import sys
sys.path.append('./src')
from shellLarkParser import larkParser, LARK_GRAMMAR
from lark import Tree, Token


class TestShellCommandTransformer(unittest.TestCase):

    @staticmethod
    def parse_and_transform(cmdline):
        parsed = larkParser(LARK_GRAMMAR, cmdline)
        return parsed

    def test_normal_command(self):
        result = self.parse_and_transform("echo test")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo test')]}]}
        self.assertEqual(result, expected)

    def test_sequence_command(self):
        result = self.parse_and_transform("echo first; echo second")
        expected = {'seq': [{'command': [{'call': [{'normal': [Token('__ANON_0', 'echo first')]}]}]}, {'command': [{'call': [{'normal': [Token('__ANON_0', 'echo second')]}]}]}]}
        self.assertEqual(result, expected)

    def test_pipe_command(self):
        result = self.parse_and_transform("cat file | grep text")
        expected = {'pipe': [{'call': [{'normal': [Token('__ANON_0', 'cat file ')]}]}, {'call': [{'normal': [Token('__ANON_0', 'grep text')]}]}]}
        self.assertEqual(result, expected)

    def test_quoted_command(self):
        result = self.parse_and_transform("echo 'hello world'")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'single_quoted': [{'inner': [Token('__ANON_1', 'hello world')]}]}]}]}
        self.assertEqual(result, expected)

    def test_single_in_double(self):
        result = self.parse_and_transform("echo \"'abc'\"")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'double_quoted': [{'single_quoted': [{'inner': [Token('__ANON_1', 'abc')]}]}]}]}]}
        self.assertEqual(result, expected)

    def test_back_in_double(self):
        result = self.parse_and_transform("echo \"`echo abc`\"")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'double_quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo abc')]}]}]}]}]}
        self.assertEqual(result, expected)

    def test_double_in_single(self):
        result = self.parse_and_transform("echo 'This is a \"nested\" quote'")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'single_quoted': [{'inner': [Token('__ANON_1', 'This is a ')]}, {'double_quoted': [{'inner': [Token('__ANON_1', 'nested')]}]}, {'inner': [Token('__ANON_1', ' quote')]}]}]}]}
        self.assertEqual(result, expected)

    def test_back_in_single(self):
        result = self.parse_and_transform("echo '`echo disqualified`'")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'single_quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo disqualified')]}]}]}]}]}
        self.assertEqual(result, expected)

    def test_single_in_back(self):
        result = self.parse_and_transform("echo `echo 'abc'`")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo ')]}, {'single_quoted': [{'inner': [Token('__ANON_1', 'abc')]}]}]}]}]}
        self.assertEqual(result, expected)

    def test_double_in_back(self):
        result = self.parse_and_transform("echo `echo \"abc\"`")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'echo ')]}, {'double_quoted': [{'inner': [Token('__ANON_1', 'abc')]}]}]}]}]}
        self.assertEqual(result, expected)

    def test_backquoted_command(self):
        result = self.parse_and_transform("echo `date`")
        expected = {'call': [{'normal': [Token('__ANON_0', 'echo ')]}, {'quoted': [{'backquoted': [{'inner': [Token('__ANON_1', 'date')]}]}]}]}
        self.assertEqual(result, expected)

    def test_io_redirection(self):
        result = self.parse_and_transform("grep text < file.txt")
        expected = {'call': [{'normal': [Token('__ANON_0', 'grep text ')]}, {'io_redirection': [{'input_redirection': [Tree(Token('RULE', 'filename'), [Token('__ANON_4', 'file.txt')])]}]}]}
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
