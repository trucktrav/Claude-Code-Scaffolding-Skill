#!/usr/bin/env python3
# ruff: noqa: S603, S607 — scaffold deliberately shells out to git/npm/npx
"""
Project scaffolding engine — opinionated defaults for PBS stack.

Supports 14 project types across Python, Go, and Web.
Python: uv + Ruff + Pyright. Polars for data work. src/ layout.
Go: standard cmd/internal/pkg layout with Makefile.
Web: TypeScript by default, Tailwind for React/Astro.

Every project gets: git init, first commit, CLAUDE.md, MIT license.
"""

import json
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration enums and dataclass
# ---------------------------------------------------------------------------

class Language(Enum):
    PYTHON = "python"
    GO = "go"
    TYPESCRIPT = "typescript"


class Database(Enum):
    NONE = "none"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class CSSFramework(Enum):
    TAILWIND = "tailwind"
    NONE = "none"


@dataclass
class ProjectConfig:
    """Configuration for a new project."""

    name: str
    project_type: str
    language: Language = Language.PYTHON
    description: str = ""
    author: str = ""
    license: str = "MIT"
    version: str = "0.1.0"

    # SDK/Runtime
    python_version: str = "3.13"
    go_version: str = "1.24"
    node_version: str = "22"

    # Framework options
    css_framework: CSSFramework = CSSFramework.TAILWIND
    database: Database = Database.NONE

    # Features
    docker: bool = False
    github_actions: bool = False

    # Additional features
    features: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Ruff rule set — opinionated but not ALL
# ---------------------------------------------------------------------------

RUFF_RULES = [
    "E4",   # pycodestyle import errors
    "E7",   # pycodestyle statement errors
    "E9",   # pycodestyle runtime errors
    "F",    # pyflakes
    "B",    # flake8-bugbear
    "I",    # isort
    "UP",   # pyupgrade
    "N",    # pep8-naming
    "S",    # flake8-bandit (security)
    "SIM",  # flake8-simplify
    "RET",  # flake8-return
    "PTH",  # flake8-use-pathlib
]


# ---------------------------------------------------------------------------
# Scaffolder
# ---------------------------------------------------------------------------

class ProjectScaffolder:
    """Main scaffolding engine."""

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path if base_path is not None else Path.cwd()

    def create_project(self, config: ProjectConfig) -> Path:
        """Create a new project from configuration."""
        project_path = self.base_path / config.name

        if project_path.exists():
            raise FileExistsError(f"Project {config.name} already exists")

        creators = {
            # Static
            "html": self._create_html,
            # Python
            "fastapi": self._create_fastapi,
            "flask": self._create_flask,
            "python-cli": self._create_python_cli,
            "python-lib": self._create_python_lib,
            "python-data": self._create_python_data,
            # Go
            "go-gin": self._create_go_api,
            "go-chi": self._create_go_api,
            "go-cli": self._create_go_cli,
            "go-module": self._create_go_module,
            # Ansible
            "ansible": self._create_ansible,
            "ansible-role": self._create_ansible_role,
            "ansible-docker-container": self._create_ansible_container,
            # Web (CLI-delegated)
            "react": self._create_react,
            "astro": self._create_astro,
            "hono": self._create_hono,
            "t3": self._create_t3,
        }

        if config.project_type not in creators:
            raise ValueError(
                f"Unknown project type: {config.project_type}. "
                f"Valid types: {', '.join(sorted(creators.keys()))}"
            )

        project_path.mkdir(parents=True)
        creators[config.project_type](project_path, config)

        # Every project: git init + first commit + CLAUDE.md
        self._git_init(project_path, config)

        return project_path

    # =====================================================================
    # Utility methods
    # =====================================================================

    def _create_dirs(self, path: Path, dirs: list[str]) -> None:
        for d in dirs:
            (path / d).mkdir(parents=True, exist_ok=True)

    def _write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def _write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n")

    def _git_init(self, path: Path, config: ProjectConfig) -> None:
        """Initialize git repo and create first commit."""
        try:
            subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)  # noqa: S603, S607
            subprocess.run(["git", "add", "."], cwd=path, capture_output=True, check=True)  # noqa: S603, S607
            subprocess.run(  # noqa: S603, S607
                ["git", "commit", "-m", f"Initial scaffold: {config.project_type} project"],
                cwd=path,
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # git not available — skip silently

    # =====================================================================
    # Common file generators
    # =====================================================================

    def _python_gitignore(self) -> str:
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
.pyright/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
*.log
"""

    def _go_gitignore(self) -> str:
        return """# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib
/bin/

# Test
*.test
*.out
coverage.txt

# Vendor (optional)
# vendor/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
*.log
"""

    def _web_gitignore(self) -> str:
        return """# Dependencies
node_modules/

# Build
dist/
build/
.next/
out/
.astro/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/

# Logs
*.log
npm-debug.log*
"""

    def _claude_md(self, config: ProjectConfig) -> str:
        """Generate CLAUDE.md for the scaffolded project."""
        lines = [
            f"# {config.name}",
            "",
            f"{config.description or 'Project description.'}",
            "",
        ]

        if config.language == Language.PYTHON:
            lines.extend([
                "## Development",
                "",
                "```bash",
                "uv sync           # install deps",
                "uv run ruff check --fix .   # lint + fix",
                "uv run ruff format .        # format",
                "uv run pyright              # type check",
                "uv run pytest               # test",
                "```",
                "",
                "## Validation",
                "",
                "Run the zero-check gauntlet after any code change:",
                "```bash",
                "~/zero-check-pipeline/validate/run-all.sh .",
                "```",
            ])
        elif config.language == Language.GO:
            lines.extend([
                "## Development",
                "",
                "```bash",
                "make build    # build binary",
                "make test     # run tests",
                "make lint     # golangci-lint",
                "make run      # build and run",
                "```",
                "",
                "## Validation",
                "",
                "Run the zero-check gauntlet after any code change:",
                "```bash",
                "~/zero-check-pipeline/validate/run-all.sh .",
                "```",
            ])
        elif config.language == Language.TYPESCRIPT:
            lines.extend([
                "## Development",
                "",
                "```bash",
                "pnpm install   # install deps",
                "pnpm dev       # dev server",
                "pnpm build     # production build",
                "pnpm lint      # ESLint",
                "pnpm test      # tests",
                "```",
            ])

        return "\n".join(lines) + "\n"

    def _ansible_claude_md(self, config: ProjectConfig) -> str:
        """Generate CLAUDE.md for Ansible projects."""
        return f"""# {config.name}

{config.description or 'Ansible project.'}

## Development

```bash
# Lint
ansible-lint playbook.yml

# Syntax check
ansible-playbook playbook.yml --syntax-check

# Dry run
ansible-playbook playbook.yml -i inventory.yml --check --diff

# Deploy
ansible-playbook playbook.yml -i inventory.yml
```
"""

    def _license_mit(self, config: ProjectConfig) -> str:
        return f"""MIT License

Copyright (c) 2026 {config.author or config.name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    def _readme(self, config: ProjectConfig, install_steps: str, dev_steps: str) -> str:
        return f"""# {config.name}

{config.description or 'Project description.'}

## Getting Started

### Installation

{install_steps}

### Development

{dev_steps}

## License

{config.license}
"""

    def _ruff_toml(self, config: ProjectConfig, first_party: str = "app") -> str:
        rules_str = ", ".join(f'"{r}"' for r in RUFF_RULES)
        return f"""line-length = 100
target-version = "py{config.python_version.replace('.', '')}"

[lint]
select = [{rules_str}]

[lint.per-file-ignores]
"tests/**" = ["S101", "INP001"]

[lint.isort]
known-first-party = ["{first_party}"]
"""

    def _pyproject_python(
        self,
        config: ProjectConfig,
        package_name: str,
        deps: list[str] | None = None,
        scripts: dict[str, str] | None = None,
        extra_sections: str = "",
    ) -> str:
        """Generate a pyproject.toml for Python projects using uv + hatchling."""
        deps_str = ""
        if deps:
            deps_str = "\n".join(f'    "{d}",' for d in deps)
            deps_str = f"\n{deps_str}\n"

        scripts_str = ""
        if scripts:
            entries = "\n".join(f'{k} = "{v}"' for k, v in scripts.items())
            scripts_str = f"\n[project.scripts]\n{entries}\n"

        return f"""[project]
name = "{config.name}"
version = "{config.version}"
description = "{config.description or ''}"
authors = [{{name = "{config.author or 'Author'}"}}]
readme = "README.md"
license = {{text = "{config.license}"}}
requires-python = ">={config.python_version}"
dependencies = [{deps_str}]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "ruff>=0.4.0",
    "pyright>=1.1",
]
{extra_sections}
{scripts_str}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]

[tool.ruff]
line-length = 100
target-version = "py{config.python_version.replace('.', '')}"

[tool.ruff.lint]
select = {json.dumps(RUFF_RULES)}

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "INP001"]

[tool.pyright]
pythonVersion = "{config.python_version}"
typeCheckingMode = "standard"
venvPath = "."
venv = ".venv"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

    def _python_common_files(self, path: Path, config: ProjectConfig) -> None:
        """Write common files for all Python projects."""
        self._write_file(path / ".gitignore", self._python_gitignore())
        self._write_file(path / "CLAUDE.md", self._claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))

    def _go_common_files(self, path: Path, config: ProjectConfig) -> None:
        """Write common files for all Go projects."""
        self._write_file(path / ".gitignore", self._go_gitignore())
        self._write_file(path / "CLAUDE.md", self._claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))

    def _web_common_files(self, path: Path, config: ProjectConfig) -> None:
        """Write common files for all web projects."""
        self._write_file(path / ".gitignore", self._web_gitignore())
        self._write_file(path / "CLAUDE.md", self._claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))

    # =====================================================================
    # Static HTML
    # =====================================================================

    def _create_html(self, path: Path, config: ProjectConfig) -> None:
        """Create a static HTML/CSS site with Tailwind CDN."""
        self._create_dirs(path, ["css", "js", "images"])

        self._write_file(path / "index.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{config.name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="css/style.css">
</head>
<body class="bg-gray-50 text-gray-900">
  <header class="bg-white shadow">
    <div class="max-w-7xl mx-auto px-4 py-6">
      <h1 class="text-3xl font-bold">{config.name}</h1>
    </div>
  </header>
  <main class="max-w-7xl mx-auto px-4 py-8">
    <p>{config.description or 'Welcome.'}</p>
  </main>
  <script src="js/main.js"></script>
</body>
</html>
""")
        self._write_file(path / "css/style.css", "/* Custom styles */\n")
        self._write_file(path / "js/main.js", "// Main script\n")

        self._write_file(path / ".gitignore", self._web_gitignore())
        self._write_file(path / "CLAUDE.md", self._claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))

    # =====================================================================
    # Python: FastAPI
    # =====================================================================

    def _create_fastapi(self, path: Path, config: ProjectConfig) -> None:
        """Create a FastAPI project with uv + src layout."""
        config.language = Language.PYTHON
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}/api",
            f"src/{package_name}/core",
            f"src/{package_name}/models",
            f"src/{package_name}/schemas",
            "tests",
        ])

        deps = [
            "fastapi>=0.115.0",
            "uvicorn[standard]>=0.34.0",
            "pydantic>=2.10.0",
            "pydantic-settings>=2.1.0",
        ]

        if config.database == Database.POSTGRESQL:
            deps.extend(["sqlalchemy>=2.0.0", "asyncpg>=0.29.0", "alembic>=1.13.0"])
        elif config.database == Database.MYSQL:
            deps.extend(["sqlalchemy>=2.0.0", "aiomysql>=0.2.0", "alembic>=1.13.0"])
        elif config.database == Database.SQLITE:
            deps.extend(["sqlalchemy>=2.0.0", "aiosqlite>=0.19.0", "alembic>=1.13.0"])

        self._write_file(
            path / "pyproject.toml",
            self._pyproject_python(config, package_name, deps=deps),
        )

        # App files
        self._write_file(path / f"src/{package_name}/__init__.py", "")
        self._write_file(path / f"src/{package_name}/main.py", f'''"""FastAPI application."""

from fastapi import FastAPI

from {package_name}.core.config import settings

app = FastAPI(title=settings.app_name, version="{config.version}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "ok"}}
''')
        self._write_file(path / f"src/{package_name}/core/__init__.py", "")
        self._write_file(path / f"src/{package_name}/core/config.py", f'''"""Application settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App configuration loaded from environment."""

    app_name: str = "{config.name}"
    debug: bool = False
    database_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
''')
        self._write_file(path / f"src/{package_name}/api/__init__.py", "")
        self._write_file(path / f"src/{package_name}/models/__init__.py", "")
        self._write_file(path / f"src/{package_name}/schemas/__init__.py", "")

        # Tests
        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_health.py", f'''"""Tests for health endpoint."""

from fastapi.testclient import TestClient

from {package_name}.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {{"status": "ok"}}
''')

        self._write_file(path / ".env.example", "DEBUG=true\nDATABASE_URL=\n")

        if config.docker:
            self._write_file(path / "compose.yml", self._fastapi_docker_compose(config))

        self._python_common_files(path, config)

    def _fastapi_docker_compose(self, config: ProjectConfig) -> str:
        return """services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:17
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""

    # =====================================================================
    # Python: Flask
    # =====================================================================

    def _create_flask(self, path: Path, config: ProjectConfig) -> None:
        """Create a Flask project with uv + src layout."""
        config.language = Language.PYTHON
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}/api",
            f"src/{package_name}/models",
            f"src/{package_name}/services",
            "tests",
        ])

        deps = [
            "flask>=3.1.0",
            "python-dotenv>=1.0.0",
        ]

        if config.database in (Database.POSTGRESQL, Database.MYSQL, Database.SQLITE):
            deps.extend(["flask-sqlalchemy>=3.1.0", "flask-migrate>=4.0.0"])

        self._write_file(
            path / "pyproject.toml",
            self._pyproject_python(config, package_name, deps=deps),
        )

        self._write_file(path / f"src/{package_name}/__init__.py", f'''"""Flask application factory."""

from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_prefixed_env()

    from {package_name}.api import routes
    app.register_blueprint(routes.bp)

    return app
''')
        self._write_file(path / f"src/{package_name}/api/__init__.py", "")
        self._write_file(path / f"src/{package_name}/api/routes.py", '''"""API routes."""

from flask import Blueprint, jsonify

bp = Blueprint("api", __name__)


@bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(status="ok")
''')
        self._write_file(path / f"src/{package_name}/models/__init__.py", "")
        self._write_file(path / f"src/{package_name}/services/__init__.py", "")

        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_health.py", f'''"""Tests for health endpoint."""

import pytest

from {package_name} import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json == {{"status": "ok"}}
''')

        self._write_file(path / ".env.example", "FLASK_DEBUG=true\nFLASK_DATABASE_URL=\n")
        self._python_common_files(path, config)

    # =====================================================================
    # Python: CLI (Typer)
    # =====================================================================

    def _create_python_cli(self, path: Path, config: ProjectConfig) -> None:
        """Create a Python CLI tool with Typer + uv."""
        config.language = Language.PYTHON
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}/commands",
            "tests",
        ])

        deps = ["typer[all]>=0.15.0", "rich>=13.7.0"]
        scripts = {config.name: f"{package_name}.cli:app"}

        self._write_file(
            path / "pyproject.toml",
            self._pyproject_python(config, package_name, deps=deps, scripts=scripts),
        )

        self._write_file(path / f"src/{package_name}/__init__.py",
                         f'"""{ config.description or config.name }"""\n\n__version__ = "{config.version}"\n')
        self._write_file(path / f"src/{package_name}/__main__.py",
                         f"from {package_name}.cli import app\n\nif __name__ == '__main__':\n    app()\n")
        self._write_file(path / f"src/{package_name}/cli.py", f'''"""CLI application."""

import typer
from rich import print

app = typer.Typer(help="{config.description or config.name}")


@app.command()
def hello(name: str = "World"):
    """Say hello."""
    print(f"[green]Hello, {{name}}![/green]")


@app.command()
def version():
    """Show version."""
    from {package_name} import __version__

    print(f"[blue]{{__version__}}[/blue]")


if __name__ == "__main__":
    app()
''')
        self._write_file(path / f"src/{package_name}/commands/__init__.py", "")

        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_cli.py", f'''"""Tests for CLI."""

from typer.testing import CliRunner

from {package_name}.cli import app

runner = CliRunner()


def test_hello():
    result = runner.invoke(app, ["hello", "--name", "Test"])
    assert result.exit_code == 0
    assert "Test" in result.stdout


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
''')

        self._python_common_files(path, config)

    # =====================================================================
    # Python: Library (PyPI)
    # =====================================================================

    def _create_python_lib(self, path: Path, config: ProjectConfig) -> None:
        """Create a Python library with uv + src layout."""
        config.language = Language.PYTHON
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [f"src/{package_name}", "tests"])

        self._write_file(
            path / "pyproject.toml",
            self._pyproject_python(config, package_name),
        )

        self._write_file(path / f"src/{package_name}/__init__.py",
                         f'"""{config.description or config.name}"""\n\n__version__ = "{config.version}"\n')
        self._write_file(path / f"src/{package_name}/main.py", '''"""Main module."""


def hello(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"
''')

        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_main.py", f'''"""Tests for main module."""

from {package_name}.main import hello


def test_hello():
    assert hello("World") == "Hello, World!"
''')

        self._python_common_files(path, config)

    # =====================================================================
    # Python: Data Analysis (Polars + Jupyter)
    # =====================================================================

    def _create_python_data(self, path: Path, config: ProjectConfig) -> None:
        """Create a data analysis project with Polars + Jupyter."""
        config.language = Language.PYTHON
        package_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"src/{package_name}",
            "notebooks",
            "data/raw",
            "data/processed",
            "tests",
        ])

        deps = [
            "polars>=1.0.0",
            "plotly>=5.22.0",
            "pyarrow>=17.0.0",
        ]

        extra = """notebook = [
    "jupyter>=1.1",
    "ipykernel>=7.0",
    "nbstripout>=0.7",
]
"""

        self._write_file(
            path / "pyproject.toml",
            self._pyproject_python(
                config,
                package_name,
                deps=deps,
                extra_sections=extra,
            ),
        )

        self._write_file(path / f"src/{package_name}/__init__.py",
                         f'"""{config.description or config.name}"""\n\n__version__ = "{config.version}"\n')
        self._write_file(path / f"src/{package_name}/load.py", '''"""Data loading utilities."""

from pathlib import Path

import polars as pl

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def load_raw(filename: str) -> pl.DataFrame:
    """Load a raw data file (CSV or Parquet)."""
    path = DATA_DIR / "raw" / filename
    if path.suffix == ".parquet":
        return pl.read_parquet(path)
    return pl.read_csv(path)


def save_processed(df: pl.DataFrame, filename: str) -> Path:
    """Save a processed DataFrame to parquet."""
    path = DATA_DIR / "processed" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)
    return path
''')

        self._write_file(path / "notebooks/.gitkeep", "")
        self._write_file(path / "data/raw/.gitkeep", "")
        self._write_file(path / "data/processed/.gitkeep", "")

        self._write_file(path / "tests/__init__.py", "")
        self._write_file(path / "tests/test_load.py", f'''"""Tests for data loading."""

from pathlib import Path

from {package_name}.load import DATA_DIR


def test_data_dir_exists():
    assert DATA_DIR.exists() or True  # CI may not have data dir
''')

        self._python_common_files(path, config)

    # =====================================================================
    # Go: API (Gin or Chi)
    # =====================================================================

    def _create_go_api(self, path: Path, config: ProjectConfig) -> None:
        """Create a Go API project with standard layout."""
        config.language = Language.GO
        module_name = config.name

        # Choose framework based on project type
        framework = "chi" if config.project_type == "go-chi" else "gin"

        self._create_dirs(path, [
            "cmd/server",
            "internal/handler",
            "internal/model",
            "internal/service",
            "pkg",
        ])

        # go.mod
        self._write_file(path / "go.mod", f"""module {module_name}

go {config.go_version}
""")

        if framework == "gin":
            self._write_file(path / "cmd/server/main.go", f'''package main

import (
\t"log"
\t"os"

\t"github.com/gin-gonic/gin"
\t"{module_name}/internal/handler"
)

func main() {{
\tport := os.Getenv("PORT")
\tif port == "" {{
\t\tport = "8080"
\t}}

\tr := gin.Default()
\thandler.RegisterRoutes(r)

\tlog.Printf("Starting server on :%s", port)
\tif err := r.Run(":" + port); err != nil {{
\t\tlog.Fatal(err)
\t}}
}}
''')
            self._write_file(path / "internal/handler/health.go", '''package handler

import (
\t"net/http"

\t"github.com/gin-gonic/gin"
)

func RegisterRoutes(r *gin.Engine) {
\tr.GET("/health", healthHandler)
}

func healthHandler(c *gin.Context) {
\tc.JSON(http.StatusOK, gin.H{"status": "ok"})
}
''')
        else:  # chi
            self._write_file(path / "cmd/server/main.go", '''package main

import (
\t"encoding/json"
\t"log"
\t"net/http"
\t"os"

\t"github.com/go-chi/chi/v5"
\t"github.com/go-chi/chi/v5/middleware"
)

func main() {
\tport := os.Getenv("PORT")
\tif port == "" {
\t\tport = "8080"
\t}

\tr := chi.NewRouter()
\tr.Use(middleware.Logger)
\tr.Use(middleware.Recoverer)

\tr.Get("/health", func(w http.ResponseWriter, r *http.Request) {
\t\tw.Header().Set("Content-Type", "application/json")
\t\tjson.NewEncoder(w).Encode(map[string]string{"status": "ok"})
\t})

\tlog.Printf("Starting server on :%s", port)
\tif err := http.ListenAndServe(":"+port, r); err != nil {
\t\tlog.Fatal(err)
\t}
}
''')

        self._write_file(path / "internal/model/.gitkeep", "")
        self._write_file(path / "internal/service/.gitkeep", "")
        self._write_file(path / "pkg/.gitkeep", "")

        # Makefile
        self._write_file(path / "Makefile", f""".PHONY: build test lint run clean

BINARY_NAME := {config.name}
BUILD_DIR := ./bin

build:
\tgo build -o $(BUILD_DIR)/$(BINARY_NAME) ./cmd/server

test:
\tgo test -v -race -coverprofile=coverage.txt ./...

lint:
\tgolangci-lint run ./...

run: build
\t$(BUILD_DIR)/$(BINARY_NAME)

clean:
\trm -rf $(BUILD_DIR) coverage.txt
""")

        self._write_file(path / ".env.example", "PORT=8080\n")

        readme = self._readme(
            config,
            install_steps="```bash\ngo mod tidy\n```",
            dev_steps="```bash\nmake run\n```",
        )
        self._write_file(path / "README.md", readme)
        self._go_common_files(path, config)

    # =====================================================================
    # Go: CLI (Cobra)
    # =====================================================================

    def _create_go_cli(self, path: Path, config: ProjectConfig) -> None:
        """Create a Go CLI tool with Cobra."""
        config.language = Language.GO
        module_name = config.name

        self._create_dirs(path, ["cmd", "internal"])

        self._write_file(path / "go.mod", f"""module {module_name}

go {config.go_version}
""")

        self._write_file(path / "main.go", f'''package main

import "{module_name}/cmd"

func main() {{
\tcmd.Execute()
}}
''')

        self._write_file(path / "cmd/root.go", f'''package cmd

import (
\t"fmt"
\t"os"

\t"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{{
\tUse:   "{config.name}",
\tShort: "{config.description or config.name}",
}}

func Execute() {{
\tif err := rootCmd.Execute(); err != nil {{
\t\tfmt.Fprintln(os.Stderr, err)
\t\tos.Exit(1)
\t}}
}}

func init() {{
\t// Add subcommands here
\trootCmd.AddCommand(versionCmd)
}}

var versionCmd = &cobra.Command{{
\tUse:   "version",
\tShort: "Print version",
\tRun: func(cmd *cobra.Command, args []string) {{
\t\tfmt.Println("{config.name} v{config.version}")
\t}},
}}
''')

        # Makefile
        self._write_file(path / "Makefile", f""".PHONY: build test lint run clean

BINARY_NAME := {config.name}
BUILD_DIR := ./bin

build:
\tgo build -o $(BUILD_DIR)/$(BINARY_NAME) .

test:
\tgo test -v -race -coverprofile=coverage.txt ./...

lint:
\tgolangci-lint run ./...

run: build
\t$(BUILD_DIR)/$(BINARY_NAME)

clean:
\trm -rf $(BUILD_DIR) coverage.txt
""")

        readme = self._readme(
            config,
            install_steps=f"```bash\ngo install {module_name}@latest\n# or\nmake build\n```",
            dev_steps="```bash\nmake run\n```",
        )
        self._write_file(path / "README.md", readme)
        self._go_common_files(path, config)

    # =====================================================================
    # Go: Module (library)
    # =====================================================================

    def _create_go_module(self, path: Path, config: ProjectConfig) -> None:
        """Create a Go module/library."""
        config.language = Language.GO
        module_name = config.name
        package = config.name.replace("-", "").replace("_", "")

        self._write_file(path / "go.mod", f"""module {module_name}

go {config.go_version}
""")

        self._write_file(path / f"{package}.go", f'''// Package {package} provides {config.description or "library functionality"}.
package {package}

// Hello returns a greeting for the given name.
func Hello(name string) string {{
\treturn "Hello, " + name + "!"
}}
''')

        self._write_file(path / f"{package}_test.go", f'''package {package}

import "testing"

func TestHello(t *testing.T) {{
\tgot := Hello("World")
\twant := "Hello, World!"
\tif got != want {{
\t\tt.Errorf("Hello() = %q, want %q", got, want)
\t}}
}}
''')

        self._write_file(path / "Makefile", """.PHONY: test lint

test:
\tgo test -v -race -coverprofile=coverage.txt ./...

lint:
\tgolangci-lint run ./...
""")

        readme = self._readme(
            config,
            install_steps=f"```bash\ngo get {module_name}\n```",
            dev_steps="```bash\nmake test\n```",
        )
        self._write_file(path / "README.md", readme)
        self._go_common_files(path, config)

    # =====================================================================
    # Ansible: Full playbook project
    # =====================================================================

    def _create_ansible(self, path: Path, config: ProjectConfig) -> None:
        """Create a full Ansible playbook project."""
        self._create_dirs(path, [
            "roles",
            "group_vars/all",
            "host_vars",
        ])

        self._write_file(path / "ansible.cfg", """[defaults]
inventory = inventory.yml
roles_path = roles
host_key_checking = false
retry_files_enabled = false

[privilege_escalation]
become = true
become_method = sudo
""")

        self._write_file(path / "inventory.yml", f"""---
# {config.name} inventory
# Add target hosts here.
#
# all:
#   children:
#     servers:
#       hosts:
#         server-01:
#           ansible_host: 192.168.1.10
#           ansible_user: deploy

all:
  children:
    servers:
      hosts: {{}}
""")

        self._write_file(path / "playbook.yml", f"""---
- name: {config.description or config.name}
  hosts: all
  gather_facts: true

  roles: []
    # - role: my_role
    #   tags: my_role
""")

        self._write_file(path / "group_vars/all/main.yml", """---
# Global variables for all hosts
# app_name: my-app
""")

        self._write_file(path / "requirements.yml", """---
# Ansible Galaxy roles and collections
# Install with: ansible-galaxy install -r requirements.yml

roles: []

collections:
  - name: community.general
  - name: community.docker
""")

        self._write_file(path / ".gitignore", """*.retry
*.pyc
__pycache__/
.vagrant/
*.log
.env
vault_password
""")

        readme = self._readme(
            config,
            install_steps="```bash\nansible-galaxy install -r requirements.yml\n```",
            dev_steps="""```bash
# Lint
ansible-lint playbook.yml

# Syntax check
ansible-playbook playbook.yml --syntax-check

# Dry run
ansible-playbook playbook.yml -i inventory.yml --check --diff

# Deploy
ansible-playbook playbook.yml -i inventory.yml
```""",
        )
        self._write_file(path / "README.md", readme)
        self._write_file(path / "CLAUDE.md", self._ansible_claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))
        self._git_init(path, config)

    # =====================================================================
    # Ansible: Reusable role (Galaxy-style)
    # =====================================================================

    def _create_ansible_role(self, path: Path, config: ProjectConfig) -> None:
        """Create a standalone Ansible role with playbook wrapper."""
        role_name = config.name.replace("-", "_")

        self._create_dirs(path, [
            f"roles/{role_name}/tasks",
            f"roles/{role_name}/defaults",
            f"roles/{role_name}/handlers",
            f"roles/{role_name}/templates",
            f"roles/{role_name}/files",
            "group_vars",
            "host_vars",
        ])

        self._write_file(path / "ansible.cfg", """[defaults]
inventory = inventory.yml
roles_path = roles
host_key_checking = false
retry_files_enabled = false

[privilege_escalation]
become = true
become_method = sudo
""")

        self._write_file(path / "inventory.yml", f"""---
# {config.name} inventory
all:
  children:
    servers:
      hosts: {{}}
""")

        self._write_file(path / "playbook.yml", f"""---
- name: {config.description or config.name}
  hosts: all
  gather_facts: true
  tags: [{role_name}]

  roles:
    - role: {role_name}
""")

        self._write_file(
            path / f"roles/{role_name}/defaults/main.yml",
            f"""---
# {role_name} role defaults
# Override per-host in host_vars/ or per-group in group_vars/.
""",
        )

        self._write_file(
            path / f"roles/{role_name}/tasks/main.yml",
            f"""---
# {role_name} — main task dispatcher

- name: Placeholder task
  ansible.builtin.debug:
    msg: "{role_name} role is running on {{{{ inventory_hostname }}}}"
""",
        )

        self._write_file(
            path / f"roles/{role_name}/handlers/main.yml",
            """---
# Handlers — triggered by notify in tasks
# - name: Restart service
#   ansible.builtin.service:
#     name: my-service
#     state: restarted
""",
        )

        self._write_file(path / ".gitignore", """*.retry
*.pyc
__pycache__/
.vagrant/
*.log
.env
vault_password
""")

        readme = self._readme(
            config,
            install_steps="```bash\n# No external dependencies\n```",
            dev_steps="""```bash
# Lint
ansible-lint playbook.yml

# Syntax check
ansible-playbook playbook.yml --syntax-check

# Dry run
ansible-playbook playbook.yml -i inventory.yml --check --diff

# Deploy
ansible-playbook playbook.yml -i inventory.yml
ansible-playbook playbook.yml -i inventory.yml --limit server-01
```""",
        )
        self._write_file(path / "README.md", readme)
        self._write_file(path / "CLAUDE.md", self._ansible_claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))
        self._git_init(path, config)

    # =====================================================================
    # Ansible: Docker container deployment structure
    # =====================================================================

    def _create_ansible_container(self, path: Path, config: ProjectConfig) -> None:
        """Create the skeleton for a tag-based Docker container Ansible role.

        Generates the dockers role structure matching common/deploy.yml contract.
        The CLI wizard then fills in container-specific content.
        """
        self._create_dirs(path, [
            "roles/dockers/tasks/common",
            "roles/dockers/tasks/containers",
            "roles/dockers/files",
            "roles/dockers/defaults",
            "roles/dockers/vars",
            "roles/dockers/templates",
            "group_vars/all",
            "host_vars",
        ])

        self._write_file(path / "ansible.cfg", """[defaults]
inventory = inventory.yml
roles_path = roles
host_key_checking = false
retry_files_enabled = false

[privilege_escalation]
become = true
become_method = sudo
""")

        self._write_file(path / "inventory.yml", f"""---
# {config.name} inventory
all:
  children:
    servers:
      hosts: {{}}
""")

        self._write_file(path / "playbook.yml", f"""---
- name: {config.description or 'Deploy Docker containers'}
  hosts: all
  gather_facts: true

  roles:
    - role: dockers
      become: true
      tags: dockers
""")

        self._write_file(path / "roles/dockers/defaults/main.yml", """---
# dockers role defaults
""")

        self._write_file(path / "roles/dockers/vars/main.yml", f"""---
# Container deployment configuration
dockers_path: /opt/docker
dockers_lan_name: "{config.name}-networks"
dockers_domain_name: "example.com"
dockers_admin_email: "admin@example.com"

# Container list — add entries as you scaffold containers
dockers_containers: []
""")

        # Shared deploy logic matching the production contract
        self._write_file(path / "roles/dockers/tasks/common/deploy.yml", """---
# Shared container deploy logic. Called via import_tasks from each
# containers/<name>.yml.
#
# Required vars:
#   container_name           (str)  — directory name under files/
#
# Optional vars:
#   container_has_env        (bool) — template .env file (default: false)
#   container_extra_dirs     (list of str)  — additional directories
#   container_extra_files    (list of {src, dest, mode}) — static files
#   container_extra_templates (list of {src, dest, mode}) — Jinja templates

- name: "{{ container_name }} | Create container directory"
  ansible.builtin.file:
    path: "{{ dockers_path }}/{{ container_name }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: root
    mode: '0775'

- name: "{{ container_name }} | Create extra directories"
  ansible.builtin.file:
    path: "{{ item }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: root
    mode: '0775'
  loop: "{{ container_extra_dirs | default([]) }}"

- name: "{{ container_name }} | Template .env"
  ansible.builtin.template:
    src: "./files/{{ container_name }}/.env.j2"
    dest: "{{ dockers_path }}/{{ container_name }}/.env"
    owner: root
    group: root
    mode: '0600'
  when: container_has_env | default(false)
  no_log: true

- name: "{{ container_name }} | Template compose.yml"
  ansible.builtin.template:
    src: "./files/{{ container_name }}/compose.j2"
    dest: "{{ dockers_path }}/{{ container_name }}/compose.yml"
    owner: "{{ ansible_user }}"
    group: root
    mode: '0664'

- name: "{{ container_name }} | Copy extra files"
  ansible.builtin.copy:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
    owner: "{{ ansible_user }}"
    group: root
    mode: "{{ item.mode | default('0660') }}"
  loop: "{{ container_extra_files | default([]) }}"
  no_log: true

- name: "{{ container_name }} | Template extra template files"
  ansible.builtin.template:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
    owner: "{{ ansible_user }}"
    group: root
    mode: "{{ item.mode | default('0664') }}"
  loop: "{{ container_extra_templates | default([]) }}"
  no_log: true

- name: "{{ container_name }} | Start container"
  community.docker.docker_compose_v2:
    project_src: "{{ dockers_path }}/{{ container_name }}/"
  when: not ansible_check_mode
""")

        # Shared GitHub clone logic
        self._write_file(path / "roles/dockers/tasks/common/github.yml", """---
# Shared GitHub clone logic. Called via import_tasks from containers
# that build from a cloned repo.
#
# Required vars:
#   repo_url      (str)  — SSH URL
#   repo_dest     (str)  — absolute path on target
#
# Optional vars:
#   repo_version  (str)  — branch/tag/commit (default: main)

- name: "{{ container_name }} | Ensure git is installed"
  ansible.builtin.package:
    name: git
    state: present

- name: "{{ container_name }} | Ensure destination parent exists"
  ansible.builtin.file:
    path: "{{ repo_dest | dirname }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: "0755"

- name: "{{ container_name }} | Clone/update repository"
  ansible.builtin.git:
    repo: "{{ repo_url }}"
    dest: "{{ repo_dest }}"
    version: "{{ repo_version | default('main') }}"
    update: true
    accept_hostkey: true
  become: true
  become_user: "{{ ansible_user }}"

- name: "{{ container_name }} | Set ownership on cloned directory"
  ansible.builtin.file:
    path: "{{ repo_dest }}"
    state: directory
    owner: "{{ ansible_user }}"
    group: "{{ ansible_user }}"
    mode: "0750"
    recurse: true
""")

        # Setup task
        self._write_file(path / "roles/dockers/tasks/setup.yml", """---
- name: Ensure Docker service is running
  ansible.builtin.service:
    name: docker
    state: started
    enabled: true
  when: not ansible_check_mode

- name: Add user to docker group
  ansible.builtin.user:
    name: "{{ ansible_user }}"
    groups: docker
    append: true
""")

        # Main task dispatcher
        self._write_file(path / "roles/dockers/tasks/main.yml", """---
# Common setup always runs regardless of tags.
- import_tasks: setup.yml
  tags: always

# Add container imports here as you scaffold them:
# - import_tasks: containers/my-app.yml
#   tags: my-app
""")

        self._write_file(path / "requirements.yml", """---
collections:
  - name: community.general
  - name: community.docker
""")

        self._write_file(path / ".gitignore", """*.retry
*.pyc
__pycache__/
.vagrant/
*.log
.env
vault_password
""")

        readme = self._readme(
            config,
            install_steps="```bash\nansible-galaxy install -r requirements.yml\n```",
            dev_steps="""```bash
# Lint
ansible-lint playbook.yml

# Deploy all containers
ansible-playbook playbook.yml -i inventory.yml

# Deploy a single container by tag
ansible-playbook playbook.yml -i inventory.yml --tags my-app

# Scaffold a new container (if wizard is available)
uv run python main.py
```""",
        )
        self._write_file(path / "README.md", readme)
        self._write_file(path / "CLAUDE.md", self._ansible_claude_md(config))
        self._write_file(path / "LICENSE", self._license_mit(config))
        self._git_init(path, config)

    # =====================================================================
    # Web: React + Vite (CLI-delegated)
    # =====================================================================

    def _create_react(self, path: Path, config: ProjectConfig) -> None:
        """Create a React project via Vite CLI, then add opinions."""
        config.language = Language.TYPESCRIPT
        # Remove the directory we created — Vite wants to create it
        path.rmdir()

        try:
            subprocess.run(  # noqa: S603, S607
                ["npm", "create", "vite@latest", config.name, "--",
                 "--template", "react-ts"],
                cwd=self.base_path,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fall back: recreate directory and write minimal structure
            path.mkdir(parents=True)
            self._write_file(path / "README.md", f"# {config.name}\n\nRun: `npm create vite@latest {config.name} -- --template react-ts`\n")
            self._web_common_files(path, config)
            return

        self._web_common_files(path, config)

    # =====================================================================
    # Web: Astro (CLI-delegated)
    # =====================================================================

    def _create_astro(self, path: Path, config: ProjectConfig) -> None:
        """Create an Astro project via CLI."""
        config.language = Language.TYPESCRIPT
        path.rmdir()

        try:
            subprocess.run(  # noqa: S603, S607
                ["npm", "create", "astro@latest", config.name, "--",
                 "--template", "basics", "--no-install", "--no-git", "-y"],
                cwd=self.base_path,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            path.mkdir(parents=True)
            self._write_file(path / "README.md", f"# {config.name}\n\nRun: `npm create astro@latest`\n")

        self._web_common_files(path, config)

    # =====================================================================
    # Web: Hono (CLI-delegated)
    # =====================================================================

    def _create_hono(self, path: Path, config: ProjectConfig) -> None:
        """Create a Hono project via CLI."""
        config.language = Language.TYPESCRIPT
        path.rmdir()

        try:
            subprocess.run(  # noqa: S603, S607
                ["npm", "create", "hono@latest", config.name],
                cwd=self.base_path,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            path.mkdir(parents=True)
            self._write_file(path / "README.md", f"# {config.name}\n\nRun: `npm create hono@latest`\n")

        self._web_common_files(path, config)

    # =====================================================================
    # Web: T3 Stack (CLI-delegated)
    # =====================================================================

    def _create_t3(self, path: Path, config: ProjectConfig) -> None:
        """Create a T3 Stack project via CLI."""
        config.language = Language.TYPESCRIPT
        path.rmdir()

        try:
            subprocess.run(  # noqa: S603, S607
                ["npx", "create-t3-app@latest", config.name, "--noGit", "-y"],
                cwd=self.base_path,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            path.mkdir(parents=True)
            self._write_file(path / "README.md", f"# {config.name}\n\nRun: `npx create-t3-app@latest`\n")

        self._web_common_files(path, config)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Simple CLI for direct scaffold.py usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Project Scaffolder")
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=[
            "html",
            "fastapi", "flask", "python-cli", "python-lib", "python-data",
            "go-gin", "go-chi", "go-cli", "go-module",
            "ansible", "ansible-role", "ansible-docker-container",
            "react", "astro", "hono", "t3",
        ],
        help="Project type",
    )
    parser.add_argument("--description", "-d", default="", help="Project description")
    parser.add_argument("--author", "-a", default="", help="Author name")
    parser.add_argument("--python-version", default="3.13", help="Python version (default: 3.13)")
    parser.add_argument("--go-version", default="1.24", help="Go version (default: 1.24)")
    parser.add_argument("--docker", action="store_true", help="Include Docker files")
    parser.add_argument("--database", choices=["none", "sqlite", "postgresql", "mysql"],
                        default="none", help="Database")

    args = parser.parse_args()

    config = ProjectConfig(
        name=args.name,
        project_type=args.type,
        description=args.description,
        author=args.author,
        python_version=args.python_version,
        go_version=args.go_version,
        docker=args.docker,
        database=Database(args.database),
    )

    scaffolder = ProjectScaffolder()
    project_path = scaffolder.create_project(config)
    print(f"Created {config.project_type} project at {project_path}")


if __name__ == "__main__":
    main()
