from invoke.tasks import task


@task
def lint(ctx):
    """Lint Python and SQL files"""
    ctx.run("ruff check --fix . && ruff format .")
    ctx.run("sqlfluff fix --dialect mysql src/database/")


@task
def lint_python(ctx):
    """Lint Python files only"""
    ctx.run("ruff check --fix . && ruff format .")


@task
def lint_sql(ctx):
    """Lint SQL files only"""
    ctx.run("sqlfluff fix --dialect mysql src/database/")
