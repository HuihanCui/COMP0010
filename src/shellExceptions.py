# Different error handling
class InvalidCommandlineArgument(Exception):
    def __init__(self, application):
        self.message = f"Invalid {application} arguments"
        super().__init__(self.message)


class ErrorExectuingApplication(Exception):
    def __init__(self, application, e):
        self.message = f"Error executing {application} application: {e}"
        super().__init__(self.message)
