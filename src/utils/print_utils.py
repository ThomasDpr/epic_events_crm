from rich.console import Console


class PrintUtils:
    def __init__(self):
        self.console = Console()

    def print_success(self, message):
        self.console.print(f"\n{message}", style="bold green")


    def print_error(self, message):
        self.console.print(f"\n{message}", style="bold red")

    def print_warning(self, message):
        self.console.print(f"\n{message}", style="bold yellow")

