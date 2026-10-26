import typer
from rich.console import Console
from rich.table import Table

from tasktracker.db import (
    VALID_PRIORITIES,
    add_tag_to_task,
    add_task,
    delete_task,
    init_db,
    list_tasks,
    mark_done,
    remove_tag_from_task,
)

app = typer.Typer(help="Simple task tracker CLI.")
console = Console()

PRIORITY_COLORS = {"alta": "red", "media": "yellow", "baja": "green"}


@app.callback()
def main():
    init_db()


@app.command()
def add(
    description: str,
    priority: str = typer.Option("media", "--priority", "-p", help=f"One of {VALID_PRIORITIES}"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags, e.g. casa,urgente"),
):
    """Add a new task."""
    if priority not in VALID_PRIORITIES:
        typer.secho(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    task_id = add_task(description, priority, tag_list)
    suffix = f" tags={tag_list}" if tag_list else ""
    typer.secho(f"Added task #{task_id}: {description} [{priority}]{suffix}", fg=typer.colors.GREEN)


@app.command(name="list")
def list_cmd(
    all: bool = typer.Option(False, "--all", "-a", help="Include completed tasks"),
    tag: str = typer.Option(None, "--tag", help="Filter by tag"),
):
    """List tasks."""
    tasks = list_tasks(include_done=all, tag_filter=tag)
    if not tasks:
        typer.echo("No tasks found.")
        return

    table = Table()
    table.add_column("ID", justify="right")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Tags")
    table.add_column("Description")

    for task in tasks:
        status = "done" if task.done else "pending"
        color = PRIORITY_COLORS[task.priority]
        table.add_row(
            str(task.id),
            f"[{color}]{task.priority}[/{color}]",
            status,
            ", ".join(task.tags),
            task.description,
        )

    console.print(table)


@app.command()
def done(task_id: int):
    """Mark a task as done."""
    if mark_done(task_id):
        typer.secho(f"Task #{task_id} marked as done.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Task #{task_id} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def rm(task_id: int):
    """Delete a task."""
    if delete_task(task_id):
        typer.secho(f"Task #{task_id} deleted.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Task #{task_id} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def tag(task_id: int, tag_name: str):
    """Add a tag to an existing task."""
    if add_tag_to_task(task_id, tag_name):
        typer.secho(f"Tag '{tag_name}' added to task #{task_id}.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Task #{task_id} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def untag(task_id: int, tag_name: str):
    """Remove a tag from an existing task."""
    if remove_tag_from_task(task_id, tag_name):
        typer.secho(f"Tag '{tag_name}' removed from task #{task_id}.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"Task #{task_id} has no tag '{tag_name}' (or task doesn't exist).", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
