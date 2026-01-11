import os
import platform
import subprocess

import questionary
from questionary import Choice

from src.cli.context import CliContext
from src.cli.styles import q_style, print_success, print_error, print_info, console
from src.cli.components.headers import print_header


def show_analysis_menu(ctx: CliContext):
    """
    Displays the user-specific menu (Chat, Import, Report).
    Requires ctx.current_username to be set.
    """
    if not ctx.current_username:
        print_error("No username selected in context.")
        return

    while True:
        # 1. Refresh User State from DB
        # We need to reload every iteration because the user may have just been imported or deleted
        person = ctx.person_repository.get_by_username(ctx.current_username)
        user_exists = person is not None

        # Dynamic header
        subtitle = f"Target: [bold cyan]@{ctx.current_username}[/bold cyan]"
        if user_exists:
            subtitle += f" (ID: {person.id})"
        else:
            subtitle += " [yellow](Not imported yet)[/yellow]"

        print_header(subtitle)

        # 2. Build Dynamic Menu Choices
        # Use 'disabled' to show options but make them unselectable
        choices = [
            Choice(
                "Chat with Profile",
                value="chat",
                disabled=False if user_exists else "Profile not found in DB"
            ),
            Choice(
                "Generate Report",
                value="report",
                disabled=False if user_exists else "Profile not found in DB"
            ),
            questionary.Separator(),
            Choice(
                "Import Data" if not user_exists else "Update/Re-import Data",
                value="import"
            ),
            Choice(
                "Remove Profile Data",
                value="remove",
                disabled=False if user_exists else "Profile not found in DB"
            ),
            questionary.Separator(),
            Choice("Back to Search", value="back")
        ]

        choice = questionary.select(
            "Select action:",
            choices=choices,
            style=q_style
        ).ask()

        # 3. Handle Actions
        if choice == "back":
            # Reset context when exiting
            ctx.current_username = None
            ctx.current_person_id = None
            break

        elif choice == "import":
            _handle_import(ctx)

        elif choice == "chat":
            _handle_chat(ctx)

        elif choice == "report":
            _handle_report(ctx)

        elif choice == "remove":
            _handle_remove_profile(ctx)


def _handle_import(ctx: CliContext):
    """
    Handles the import flow (Scraping + Processing).
    """

    limit_stories: int = 20
    limit_posts: int = 20
    limit_content_per_highlight: int = 10

    # 1. Import and process profile metadata
    with console.status("[info]Importing profile metadata...", spinner="dots"):
        ctx.import_service.import_profile_metadata(ctx.current_username)
        person = ctx.person_repository.get_by_username(ctx.current_username)
    with console.status("[info]Processing profile info...", spinner="dots"):
        ctx.content_processor_service.process_profile_info(person.id)
    print_success("Profile metadata completed\n")

    # 2. Import and process stories
    with console.status(f"[info]Importing stories (limit: {limit_stories})...", spinner="dots"):
        ctx.import_service.import_stories(ctx.current_username, limit=limit_stories)
    with console.status("[info]Processing stories...", spinner="dots"):
        ctx.content_processor_service.process_stories(person.id)
    print_success("Stories completed\n")

    # 3. Import and process posts
    with console.status(f"[info]Importing posts (limit: {limit_posts})...", spinner="dots"):
        ctx.import_service.import_posts(ctx.current_username, limit=limit_posts)
    with console.status("[info]Processing posts...", spinner="dots"):
        ctx.content_processor_service.process_posts(person.id)
    print_success("Posts completed\n")

    # 4. Import and process highlights
    with console.status(f"[info]Importing highlights (limit: {limit_content_per_highlight})...", spinner="dots"):
        ctx.import_service.import_highlights(ctx.current_username, limit=limit_content_per_highlight)
    with console.status("[info]Processing highlights...", spinner="dots"):
        ctx.content_processor_service.process_highlights(person.id)
    print_success("Highlights completed\n")

    print_success("Import completed successfully!")
    questionary.press_any_key_to_continue().ask()


def _handle_remove_profile(ctx: CliContext):
    confirm = questionary.confirm(
        f"Are you sure you want to delete all data for @{ctx.current_username}?",
        style=q_style
    ).ask()

    if confirm and ctx.current_person_id:
        try:
            with console.status("Deleting..."):
                ctx.removal_service.remove_person(ctx.current_username)

            print_success(f"Profile @{ctx.current_username} removed.")
            questionary.press_any_key_to_continue().ask()

        except Exception as e:
            print_error(f"Deletion failed: {e}")


def _handle_chat(ctx: CliContext):
    """
    Starts the RAG Chat Loop.
    """
    print_header(f"CHAT ABOUT @{ctx.current_username}")
    print_info("Type 'exit' or 'quit' to go back.")

    while True:
        question = questionary.text("You:", style=q_style).ask()

        if not question or question.lower() in ["exit", "quit", "back"]:
            break

        try:
            with console.status("Thinking..."):
                # Call the previously created RAG service
                answer = ctx.profile_query_service.ask_question_about_profile(
                    username=ctx.current_username,
                    question=question,
                    k=20
                )

            console.print(f"[bold cyan]AI:[/bold cyan] {answer}")
            console.print("")

        except Exception as e:
            print_error(f"Error: {e}")


def _handle_report(ctx: CliContext):
    """
    Generates the PDF report.
    """
    print_info(f"Generating comprehensive report for @{ctx.current_username}...")
    print_info("This involves deep analysis and may take a minute.\n")

    try:
        with console.status("[bold cyan]Analyzing Personality, Style, and Habits...[/bold cyan]", spinner="earth"):

            report_path = ctx.report_service.generate_report(ctx.current_username)

        print_success(f"Report generated successfully!")
        console.print(f"Saved at: [underline]{report_path}[/underline]")

        if questionary.confirm("Open report now?").ask():
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', report_path))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(report_path)
            else:                                   # linux
                subprocess.call(('xdg-open', report_path))

        questionary.press_any_key_to_continue().ask()

    except Exception as e:
        print_error(f"Report generation failed: {e}")