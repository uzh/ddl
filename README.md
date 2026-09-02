# Data Donation Lab (ddl)
This is the source code for the Data Donation Lab website: https://datadonation.uzh.ch

## Repository Structure

**App components:**
- `config`: Contains the main Django configuration; wires everything together.
- `ddl`: Integrates Wagtail into the webapp and defines website components.
  Additionally, integrates a custom API endpoint that allows directly uploading
  a ZIP file containing one or several JSON files, bypassing the DDM frontend
  (see `ddl.apis.ZipPostAPI`).
- `reports`: Legacy app that was used at the Data Donation Days to display reports
  based on received data donations. Deprecated and will be deleted in the future.

**Other directories:**
- `.github`: Contains the GitHub Action workflows.
- `requirements`: Contains the requirements for this application, divided into
  `base`, `dev`, and `production`.

## Development Setup

### Prerequisites

- Python 3.12
- SQLite - used as dev database; MariaDB is used in production

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/uzh/ddl
cd ddl

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements/dev.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Install pre-commit hooks
pre-commit install
pre-commit install --hook-type pre-push   # enables pip-audit on push

# 6. Apply database migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Start dev server
python manage.py runserver
```

---

## Repository Management

### Branches

We work with three central branches:

- `dev`: Shared code, pre-deployment;
- `stage`: Deployed to stage for testing and QA before production.
- `main`: Deployed to production.

---

## Day-to-day Development

### Running tests

```bash
python manage.py test
python -m coverage run manage.py test
python -m coverage report          # fails if coverage drops below 80 %
```

### Linting and formatting

Usually, auto-run when committing, but good to know:

```bash
ruff check .                        # lint
ruff check . --fix                  # lint and auto-fix
ruff format .                       # format
djlint ddcs/ --check                # check templates
djlint ddcs/ --reformat             # reformat templates
```

### Skipping pre-commit hooks

To skip a specific hook (e.g. when a vulnerability has no fix yet):

```bash
SKIP=pip-audit git push
```

To skip all hooks — use sparingly:

```bash
git push --no-verify
```

`SKIP` accepts a comma-separated list of hook IDs: `SKIP=pip-audit,check-translations git push`.
