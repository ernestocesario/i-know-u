import os
from rich.panel import Panel
from rich.align import Align
from src.cli.styles import console
from src.config.app_properties import AppProperties


def clear_screen():
    # Clears the terminal screen (Windows or Unix-based)
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(subtitle: str = "A powerful AI profile analyzer"):
    """
    Clears the screen and prints the standard application header.
    """
    clear_screen()

    title_text = f"[bold cyan]IKU[/bold cyan] [dim]- {AppProperties.APP_NAME}[/dim]"

    if subtitle:
        content = f"{title_text}\n[bold white]{subtitle}[/bold white]"
    else:
        content = title_text

    console.print(
        Panel(
            Align.center(content),
            border_style="blue",
            padding=(0, 2)
        )
    )
    console.print("")  # Empty line for spacing
