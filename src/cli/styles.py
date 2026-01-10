import questionary
from rich.console import Console
from rich.theme import Theme

# 1. Rich Configuration (Output)
# Define color aliases
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "header": "bold white on blue",
    "highlight": "bold magenta",
    "label": "dim white",
    "value": "bold white"
})

console = Console(theme=custom_theme)

# 2. Questionary Configuration (Interactive Input)
# This style controls the selection menus
q_style = questionary.Style([
    ('qmark', 'fg:#00FFFF bold'),       # ? symbol in cyan
    ('question', 'fg:#FFFFFF bold'),    # Question in white
    ('answer', 'fg:#00FFFF bold'),      # Given answer in cyan
    ('pointer', 'fg:#00FFFF bold'),     # Selection cursor (>)
    ('highlighted', 'fg:#00FFFF bold'), # Highlighted entry
    ('selected', 'fg:#00FFFF'),         # Selected checkbox
    ('separator', 'fg:#6C6C6C'),        # Separators
    ('instruction', 'fg:#6C6C6C italic') # Instructions (use arrows...)
])

def print_success(msg: str):
    console.print(f"[success]✔ {msg}[/success]")

def print_error(msg: str):
    console.print(f"[error]✖ {msg}[/error]")

def print_info(msg: str):
    console.print(f"[info]ℹ {msg}[/info]")
