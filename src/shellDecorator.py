# Registry for command classes
commandRegistry = {}


# Class decorators to register command classes
def commandRegister(commandName):
    def decorator(cls):
        commandRegistry[commandName] = cls
        return cls
    return decorator


def unsafe_command_decorator(cls):
    class UnsafeCommand(cls):
        def execute(self):
            try:
                super().execute()
            except Exception as e:
                self.out.append(f"Error: {str(e)}\n")
    return UnsafeCommand
