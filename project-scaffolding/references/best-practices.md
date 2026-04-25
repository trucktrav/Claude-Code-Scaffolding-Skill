# Best Practices

Architecture and organizational patterns applied by this scaffolding skill.

---

## Directory Structure

### Python: always use `src/` layout
```
src/package_name/    # forces install before testing
tests/               # at project root, not inside src
```

Why: prevents accidentally importing from the source directory instead of the installed package. Catches packaging bugs before deployment.

### Go: standard layout
```
cmd/          # entry points (one per binary)
internal/     # private application code
pkg/          # code safe to import from other projects
```

Why: Go community convention. `internal/` has compiler-enforced visibility.

### Data projects: separate raw from processed
```
data/raw/         # immutable input data
data/processed/   # computed output (parquet)
notebooks/        # exploratory work
```

Why: reproducibility. Raw data is never modified; processed data can always be regenerated.

---

## Naming Conventions

### Python
- Package names: lowercase, underscores (`ssh_login_alerter`, not `ssh-login-alerter`)
- Module names: lowercase, short (`load.py`, `config.py`)
- Test files: `test_` prefix (`test_health.py`)

### Go
- Package names: lowercase, no underscores (`handler`, not `http_handler`)
- File names: lowercase, underscores OK (`health_handler.go`)
- Test files: `_test.go` suffix

---

## Configuration Management

### Python: Pydantic Settings for apps
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "my-app"
    debug: bool = False
    database_url: str = ""

    class Config:
        env_file = ".env"
```

Why: typed, validated, env-file support, IDE autocomplete.

### Python: pyproject.toml for everything
All tool config lives in `pyproject.toml` — no separate `ruff.toml`, `pyright.json`, `setup.cfg`. Single source of truth.

### Go: env vars with defaults
```go
port := os.Getenv("PORT")
if port == "" {
    port = "8080"
}
```

Simple and effective. Add a `.env.example` for documentation.

---

## Testing Patterns

### Python: pytest with src layout
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

Tests import the installed package, not the source:
```python
from my_package.main import hello
```

### Go: table-driven tests
```go
func TestHello(t *testing.T) {
    tests := []struct{
        name string
        input string
        want string
    }{
        {"basic", "World", "Hello, World!"},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Hello(tt.input)
            if got != tt.want {
                t.Errorf("got %q, want %q", got, tt.want)
            }
        })
    }
}
```

Always use `-race` flag: `go test -race ./...`

---

## Dependency Management

### Python: uv with dependency groups
```toml
[project]
dependencies = ["fastapi>=0.115.0"]  # runtime

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.4.0"]  # development only
notebook = ["jupyter>=1.1"]            # optional groups
```

`dependency-groups` is the newer PEP spec — preferred over `[project.optional-dependencies]` for non-publishable groups.

### Go: go.mod
```
module my-project

go 1.24
```

Run `go mod tidy` after adding imports. No lock file needed — Go uses the module cache.

---

## Code Quality

### Ruff rule selection rationale

The skill selects these rules for all Python projects:

| Rule | Category | Why |
|------|----------|-----|
| E4,E7,E9 | pycodestyle | Basic syntax and style errors |
| F | pyflakes | Unused imports, undefined names |
| B | bugbear | Common bug patterns |
| I | isort | Import ordering |
| UP | pyupgrade | Modernize syntax for target Python |
| N | pep8-naming | Consistent naming |
| S | bandit/security | Hardcoded passwords, SQL injection, eval() |
| SIM | simplify | Unnecessary complexity |
| RET | return | Implicit returns, unreachable code |
| PTH | pathlib | os.path → pathlib migration |

Not selected (and why):
- `ALL` — too noisy, fights with each other
- `D` (docstrings) — useful for libraries, overkill for apps
- `ANN` (annotations) — Pyright handles this better
- `C90` (complexity) — subjective, handled in code review

### Per-file ignores
```toml
"tests/**" = ["S101", "INP001"]
```
- `S101`: allow `assert` in tests (bandit flags it)
- `INP001`: allow test dirs without `__init__.py` in namespace packages

---

## Docker (when enabled)

### Python API: compose.yml
Always use `compose.yml`, never bare `docker run`.

Pattern:
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
  db:
    image: postgres:17
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

---

## CLAUDE.md

Every scaffolded project includes a `CLAUDE.md` with:
1. Project name and description
2. Dev workflow commands (uv/go/pnpm)
3. Reference to zero-check gauntlet

This enables Claude Code to understand the project structure and run validation on any changes.
