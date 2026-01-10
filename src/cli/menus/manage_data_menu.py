import questionary
from questionary import Choice

from src.cli.components.headers import print_header
from src.cli.components.tables import render_profiles_table
from src.cli.context import CliContext
from src.cli.styles import q_style, print_success, print_error, print_info, console


def show_manage_data_menu(ctx: CliContext):
    """
    Displays the 'Manage Data' menu.
    """
    while True:
        print_header("MANAGE DATA")

        # Menu Options
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                Choice("Show All Profiles", value="show"),
                Choice("Remove All Data", value="reset"),
                questionary.Separator(),
                Choice("Back to Main Menu", value="back")
            ],
            style=q_style
        ).ask()

        if choice == "back":
            break

        elif choice == "show":
            _handle_show_all(ctx)
            questionary.press_any_key_to_continue().ask()

        elif choice == "reset":
            _handle_reset_db(ctx)
            questionary.press_any_key_to_continue().ask()


def _handle_show_all(ctx: CliContext):
    """
    Fetches all people and renders the table.
    """
    try:
        render_profiles_table(ctx)

    except Exception as e:
        print_error(f"Failed to fetch profiles: {e}")


def _handle_reset_db(ctx: CliContext):
    """
    Dangerous operation: Deletes EVERYTHING (SQL + Vector).
    """
    print_header("⚠ DANGER ZONE ⚠")
    console.print(
        "[bold red]This will permanently delete ALL profiles, posts, stories, and vector embeddings.[/bold red]")

    confirm = questionary.confirm(
        "Are you absolutely sure you want to proceed?",
        default=False,
        style=q_style
    ).ask()

    if not confirm:
        print_info("Operation cancelled.")
        return

    try:
        with console.status("[bold red]Wiping everything...[/bold red]"):
            ctx.removal_service.remove_all_data()

        print_success("Everything has been reset successfully.")

    except Exception as e:
        ctx.session.rollback()
        print_error(f"Reset failed: {e}")
