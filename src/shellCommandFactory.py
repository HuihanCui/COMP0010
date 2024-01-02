from shellCommands import commandRegistry


# The class for command factory design
class CommandFactory:
    def __init__(self, cmdline, out, extra_dict):
        self.cmdline = cmdline
        self.out = out
        self.extra_dict = extra_dict

    # Handle the potential output direction
    def output_redirection(self):
        output_file = self.extra_dict.get("outputFile")
        if output_file is not None:
            with open(output_file[0], "a" if output_file[1] else "w") as f:
                f.writelines(self.out)
                self.out.clear()

    # Parrse command into command name and arguments
    def parse_command(self):
        tokens = self.cmdline.split()
        if not tokens:
            raise ValueError("No application provided")
        commandname = tokens[0]
        if commandname in ["echo", "_echo"]:
            args = [self.cmdline[len(commandname) + 1:]]
        else:
            args = tokens[1:]
        return commandname, args

    # Create corresponding classes for commands and execute
    def execute_command(self, commandname, args):
        cmd_class = commandRegistry.get(commandname)
        if cmd_class:
            try:
                command_instance = cmd_class(args, self.out, self.extra_dict)
                command_instance.execute()
            except Exception as e:
                raise ValueError(f"Failed '{commandname}' initialize: {e}")
        else:
            raise ValueError(f"Unknown application: {commandname}")

    # Main function for command factory
    def execute(self):
        try:
            commandname, args = self.parse_command()
            self.execute_command(commandname, args)
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}\n")
        finally:
            self.output_redirection()
