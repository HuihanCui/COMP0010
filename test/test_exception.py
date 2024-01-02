import unittest
import sys
sys.path.append('./src')
from shellExceptions import InvalidCommandlineArgument, ErrorExectuingApplication


class TestCustomExceptions(unittest.TestCase):

    def test_invalid_commandline_argument_exception(self):
        application = "test_app"
        exception_message = "Invalid test_app arguments"

        try:
            raise InvalidCommandlineArgument(application)
        except InvalidCommandlineArgument as e:
            self.assertEqual(str(e), exception_message)
            self.assertEqual(e.message, exception_message)

    def test_error_executing_application_exception(self):
        application = "test_app"
        error_message = "Sample Error"
        exception = "Error executing test_app application: Sample Error"

        try:
            raise ErrorExectuingApplication(application, error_message)
        except ErrorExectuingApplication as e:
            self.assertEqual(str(e), exception)
            self.assertEqual(e.message, exception)


if __name__ == '__main__':
    unittest.main()
