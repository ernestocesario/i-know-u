import os
from typing import Optional

from pyfiglet import Figlet
from rich.align import Align
from rich.panel import Panel
from rich.console import Group

from src.cli.styles import console
from src.config.app_properties import AppProperties


def clear_screen():
    # Clears the terminal screen (Windows or Unix-based)
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(menu_name: Optional[str] = None):
    """
    Clears the screen and prints an application header.
    """
    clear_screen()

    fig = Figlet(font='bloody')
    title_ascii = fig.renderText(AppProperties.APP_NAME)

    title_text = f"[bold red]{title_ascii}[/bold red]"
    tagline = f"[dim bold italic]Nothing stays private forever...[/dim bold italic]"

    content = Group(
        Align.center(title_text),
        Align.center(tagline)
    )

    panel = Panel(
        content,
        border_style="red",
        padding=(1, 2)
    )

    if menu_name:
        menu_text = f"[bold yellow]{menu_name}[/bold yellow]"
        console.print(
            Group(
                panel,
                Align.center(menu_text)
            )
        )
    else:
        console.print(panel)

    console.print("")