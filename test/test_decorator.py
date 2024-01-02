import unittest
import sys
sys.path.append('./src')
from shellDecorator import commandRegister, unsafe_command_decorator, commandRegistry


class TestDecorators(unittest.TestCase):

    def test_commandRegister_decorator(self):
        @commandRegister("test_command")
        class TestCommand:
            pass

        self.assertIn("test_command", commandRegistry)
        self.assertIs(commandRegistry["test_command"], TestCommand)

    def test_unsafe_command_decorator(self):
        @unsafe_command_decorator
        class SafeTestCommand:
            def __init__(self):
                self.out = []

            def execute(self):
                raise Exception("Test Error")

        unsafe_command = SafeTestCommand()
        unsafe_command.execute()

        self.assertEqual(unsafe_command.out, ["Error: Test Error\n"])

    def test_unsafe_command_decorator_with_no_exception(self):
        @unsafe_command_decorator
        class SafeTestCommand:
            def __init__(self):
                self.out = []

            def execute(self):
                self.out.append("Executed successfully")

        unsafe_command = SafeTestCommand()
        unsafe_command.execute()

        self.assertEqual(unsafe_command.out, ["Executed successfully"])


if __name__ == '__main__':
    unittest.main()
