from typing import List
from rich.table import Table
from rich import box

from src.cli.context import CliContext
from src.models import Person
from src.cli.styles import console
from src.models.DTOs.filters.sql_db.content_filter import ContentFilter
from src.models.DTOs.filters.sql_db.highlight_filter import HighlightFilter
from src.models.DTOs.filters.sql_db.person_filter import PersonFilter
from src.models.DTOs.filters.sql_db.post_filter import PostFilter
from src.models.DTOs.filters.sql_db.story_filter import StoryFilter


def render_profiles_table(ctx: CliContext):
    """
    Renders a rich table showing all profiles in the database.
    """
    profiles: List[Person] = ctx.person_repository.find(
        PersonFilter(
            sort_by="id",
            sort_order="asc"
        )
    )

    if not profiles:
        console.print("[warning]No profiles found in database.[/warning]")
        return

    table = Table(
        title="Database Profiles",
        box=box.ROUNDED,
        header_style="bold cyan",
        border_style="dim blue"
    )

    # Define columns
    table.add_column("ID", style="dim", width=4, justify="right")
    table.add_column("Ext. ID", style="dim white")
    table.add_column("Username", style="bold white")
    table.add_column("Full name", style="bold white")
    table.add_column("Followers", justify="right")
    table.add_column("Following", justify="right")
    table.add_column("Posts", justify="right")

    table.add_column("Downloaded Stories", justify="right", style="green")
    table.add_column("Downloaded Posts", justify="right", style="green")
    table.add_column("Downloaded Highlights", justify="right", style="green")
    table.add_column("Downloaded media", justify="right", style="green")

    table.add_column("Status", justify="right", style="green")

    for person in profiles:
        is_fully_processed = ctx.content_processor_service.is_fully_processed(person.id)
        status_icon = "[green]✔ COMPLETED[/green]" if is_fully_processed else "[yellow]⏳ PENDING[/yellow]"

        # Format numbers
        n_followers = f"{person.n_followers:,}" if person.n_followers else "-"
        n_following = f"{person.n_following:,}" if person.n_following else "-"
        n_posts = f"{person.n_posts:,}" if person.n_posts else "-"

        downloaded_stories = ctx.story_repository.count(
            StoryFilter(
                owner_is=person
            )
        )
        downloaded_posts = ctx.post_repository.count(
            PostFilter(
                owner_is=person
            )
        )
        downloaded_highlights = ctx.highlight_repository.count(
            HighlightFilter(
                owner_is=person
            )
        )
        downloaded_content = ctx.content_repository.count(
            ContentFilter(
                owner_is=person
            )
        )

        table.add_row(
            str(person.id),
            str(person.external_id),
            person.username,
            person.full_name,
            n_followers,
            n_following,
            n_posts,
            str(downloaded_stories),
            str(downloaded_posts),
            str(downloaded_highlights),
            str(downloaded_content),
            status_icon
        )

    console.print(
        table
    )