import typer
from rich.console import Console
from rich.table import Table

from tasktracker.db import VALID_PRIORITIES, add_task, delete_task, init_db, list_tasks, mark_done

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
):
    """Add a new task."""
    if priority not in VALID_PRIORITIES:
        typer.secho(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    task_id = add_task(description, priority)
    typer.secho(f"Added task #{task_id}: {description} [{priority}]", fg=typer.colors.GREEN)


@app.command(name="list")
def list_cmd(all: bool = typer.Option(False, "--all", "-a", help="Include completed tasks")):
    """List tasks."""
    tasks = list_tasks(include_done=all)
    if not tasks:
        typer.echo("No tasks found.")
        return

    table = Table()
    table.add_column("ID", justify="right")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Description")

    for task in tasks:
        status = "done" if task.done else "pending"
        color = PRIORITY_COLORS[task.priority]
        table.add_row(str(task.id), f"[{color}]{task.priority}[/{color}]", status, task.description)

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


if __name__ == "__main__":
    app()
