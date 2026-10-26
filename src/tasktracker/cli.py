from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from tasktracker.db import (
    VALID_PRIORITIES,
    HasSubtasksError,
    Task,
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
    parent: Optional[int] = typer.Option(None, "--parent", help="Parent task id (creates a subtask)"),
):
    """Add a new task."""
    if priority not in VALID_PRIORITIES:
        typer.secho(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        task_id = add_task(description, priority, tag_list, parent_id=parent)
    except ValueError as e:
        typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)
    suffix = f" tags={tag_list}" if tag_list else ""
    if parent is not None:
        suffix += f" parent=#{parent}"
    typer.secho(f"Added task #{task_id}: {description} [{priority}]{suffix}", fg=typer.colors.GREEN)


def _print_tree(tasks: list[Task]) -> None:
    children_by_parent: dict[Optional[int], list[Task]] = {}
    for task in tasks:
        children_by_parent.setdefault(task.parent_id, []).append(task)

    def render(parent_id: Optional[int], depth: int) -> None:
        for task in children_by_parent.get(parent_id, []):
            status = "done" if task.done else "pending"
            color = PRIORITY_COLORS[task.priority]
            tag_suffix = f" [{', '.join(task.tags)}]" if task.tags else ""
            indent = "  " * depth
            console.print(
                f"{indent}#{task.id} [{color}]{task.priority}[/{color}] "
                f"({status}) {task.description}{tag_suffix}"
            )
            render(task.id, depth + 1)

    render(None, 0)


@app.command(name="list")
def list_cmd(
    all: bool = typer.Option(False, "--all", "-a", help="Include completed tasks"),
    tag: str = typer.Option(None, "--tag", help="Filter by tag"),
    tree: bool = typer.Option(False, "--tree", help="Show nested hierarchy (ignores --all/--tag)"),
):
    """List tasks."""
    if tree:
        tasks = list_tasks(include_done=True)
        if not tasks:
            typer.echo("No tasks found.")
            return
        _print_tree(tasks)
        return

    tasks = list_tasks(include_done=all, tag_filter=tag)
    if not tasks:
        typer.echo("No tasks found.")
        return

    table = Table()
    table.add_column("ID", justify="right")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Tags")
    table.add_column("Parent")
    table.add_column("Description")

    for task in tasks:
        status = "done" if task.done else "pending"
        color = PRIORITY_COLORS[task.priority]
        table.add_row(
            str(task.id),
            f"[{color}]{task.priority}[/{color}]",
            status,
            ", ".join(task.tags),
            str(task.parent_id) if task.parent_id is not None else "-",
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
def rm(
    task_id: int,
    cascade: bool = typer.Option(False, "--cascade", help="Delete this task and all its subtasks"),
):
    """Delete a task."""
    try:
        deleted = delete_task(task_id, cascade=cascade)
    except HasSubtasksError as e:
        typer.secho(
            f"Task #{task_id} has {e.count} subtask(s); use --cascade to delete them too.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if deleted:
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
