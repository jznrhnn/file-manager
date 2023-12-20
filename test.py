from rich.progress import Progress

# Create a progress context
with Progress() as progress:

    # Create a task to track the progress
    task = progress.add_task("[cyan]Working...", total=100)

    # Simulate progress updating
    for i in range(1, 101):
        # Update the task's progress
        progress.update(task, advance=1)
        # Simulate some work being done
        # Replace this with your actual task or computation
