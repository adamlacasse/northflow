from invoke.tasks import task


@task
def lint(ctx):
    """Lint Python, SQL, and HTML files"""
    ctx.run("ruff check --fix . && ruff format .")
    ctx.run("sqlfluff fix --dialect mysql app/database/")
    ctx.run("djlint --reformat --lint app/templates/")


@task
def lint_python(ctx):
    """Lint Python files only"""
    ctx.run("ruff check --fix . && ruff format .")


@task
def lint_sql(ctx):
    """Lint SQL files only"""
    ctx.run("sqlfluff fix --dialect mysql app/database/")


@task
def lint_html(ctx):
    """Lint HTML/Jinja2 templates only"""
    ctx.run("djlint --reformat --lint app/templates/")
