# Framework Reference

Code patterns and project structures for each supported project type.
Load this reference when generating project code.

---

## Python Projects — Common Patterns

### src/ layout (all Python types)
```
my-project/
├── src/my_project/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── CLAUDE.md
├── LICENSE
└─��� .gitignore
```

### pyproject.toml (all Python types)
- Build system: hatchling
- Dependencies: `[project] dependencies`
- Dev deps: `[dependency-groups] dev` (newer spec)
- Ruff config inline: `[tool.ruff]` + `[tool.ruff.lint]`
- Pyright config inline: `[tool.pyright]`
- Pytest config inline: `[tool.pytest.ini_options]`

### Common dev workflow
```bash
uv sync              # install all deps (including dev)
uv run ruff check .  # lint
uv run ruff format . # format
uv run pyright       # type check
uv run pytest        # test
```

---

## FastAPI Structure
```
my-api/
├── src/my_api/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, health endpoint
│   ├── core/
│   │   ├── __init__.py
��   │   └── config.py    # Pydantic Settings
│   ├── api/
│   │   └── __init__.py  # Route modules
│   ├── models/
│   │   └── __init__.py  # SQLAlchemy models (if DB)
│   └── schemas/
│       └── __init__.py  # Pydantic schemas
���── tests/
│   ├── __init__.py
│   └── test_health.py
├── pyproject.toml
├── .env.example
├── CLAUDE.md
└── LICENSE
```

Key patterns:
- `pydantic-settings` for env-based config
- `TestClient` from `fastapi.testclient` for tests
- SQLAlchemy 2.0 async if database selected
- Alembic for migrations if database selected

---

## Flask Structure
```
my-app/
├── src/my_app/
│   ├─��� __init__.py      # Application factory (create_app)
│   ├── api/
│   │   ├── __init__.py
│   │   └─�� routes.py    # Blueprint with routes
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── tests/
���   ├── __init__.py
│   └── test_health.py
��─��� pyproject.toml
├── .env.example
��── CLAUDE.md
└── LICENSE
```

Key patterns:
- Application factory pattern (`create_app()`)
- Blueprints for route organization
- `app.config.from_prefixed_env()` for config
- `flask-sqlalchemy` + `flask-migrate` if database selected

---

## Python CLI Structure
```
my-tool/
├── src/my_tool/
│   ├── __init__.py      # __version__
��   ├── __main__.py      # Entry point
│   ├── cli.py           # Typer app + commands
│   └── commands/
│       └���─ __init__.py  # Subcommand modules
├── tests/
│   ├── __init__.py
│   └── test_cli.py      # CliRunner tests
├── pyproject.toml       # [project.scripts] entry point
├── CLAUDE.md
└── LICENSE
```

Key patterns:
- Typer for CLI framework, Rich for output
- `[project.scripts]` maps command name to `package.cli:app`
- `typer.testing.CliRunner` for tests
- `__main__.py` enables `python -m package`

---

## Python Data Analysis Structure
```
my-analysis/
├─�� src/my_analysis/
│   ├── __init__.py
│   └── load.py          # Data loading utilities
├── notebooks/           # Jupyter notebooks
├── data/
���   ├── raw/            # Input data (gitignored content, kept structure)
│   └── processed/      # Output data (parquet)
├── tests/
│   ├── __init__.py
│   └── test_load.py
├── pyproject.toml       # Polars, plotly, pyarrow + notebook dep group
├── CLAUDE.md
└── LICENSE
```

Key patterns:
- Polars over pandas (lazy execution, memory efficient)
- Parquet as default data format (via pyarrow)
- Plotly for visualization (interactive, works in notebooks and web)
- Separate `[dependency-groups] notebook` for Jupyter deps
- `data/raw/` → process → `data/processed/` pipeline pattern

---

## Go API Structure (Gin or Chi)
```
my-api/
├── cmd/server/
│   └── main.go          # Entry point, router setup
├── internal/
│   ├── handler/
│   │   └─�� health.go    # HTTP handlers (Gin only)
���   ├── model/
│   └── service/
├── pkg/                  # Shared/exported packages
├── go.mod
├── Makefile
├── .env.example
├── CLAUDE.md
└── LICENSE
```

Key patterns:
- `cmd/` for entry points, `internal/` for private, `pkg/` for public
- Gin: `gin.Default()` + handler registration
- Chi: `chi.NewRouter()` + `middleware.Logger` + `middleware.Recoverer`
- Makefile: build, test (with -race), lint (golangci-lint), run, clean

---

## Go CLI Structure (Cobra)
```
my-tool/
├── cmd/
│   └── root.go          # Root command + subcommands
├─��� internal/             # Business logic
├── main.go              # Entry point calling cmd.Execute()
���── go.mod
├─�� Makefile
├── CLAUDE.md
└��─ LICENSE
```

Key patterns:
- `cobra.Command` for root + subcommands
- `init()` for registering subcommands
- `cmd.Execute()` in main.go
- Version subcommand included by default

---

## Go Module Structure
```
my-module/
├── mymodule.go          # Package code
├── mymodule_test.go     # Tests
├── go.mod
├── Makefile
└── LICENSE
```

Key patterns:
- Flat layout — single package at root
- Table-driven tests
- `go test -race -coverprofile=coverage.txt`

---

## Web Projects (CLI-delegated)

### React + Vite
Created by: `npm create vite@latest {name} -- --template react-ts`
Adds: CLAUDE.md, LICENSE, .gitignore

### Astro
Created by: `npm create astro@latest {name} -- --template basics --no-install --no-git -y`
Adds: CLAUDE.md, LICENSE, .gitignore

### Hono
Created by: `npm create hono@latest {name}`
Adds: CLAUDE.md, LICENSE, .gitignore

### T3 Stack
Created by: `npx create-t3-app@latest {name} --noGit -y`
Full-stack: Next.js + tRPC + Prisma + Tailwind + NextAuth
Adds: CLAUDE.md, LICENSE, .gitignore
