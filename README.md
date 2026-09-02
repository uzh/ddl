# Data Donation Lab (ddl)
This is the source code for the Data Donation Lab website: https://datadonation.uzh.ch

## About

The Data Donation Lab at the University of Zurich helps researchers run *data
donation* studies: participants request a copy of their data from a platform
(Instagram, YouTube, …) and donate selected parts of it for research.

`ddl` is the public website (a Wagtail CMS) built around
[`django-ddm`](https://github.com/uzh/ddm) — the reusable Django app that
implements the donation flow and the researcher interface. This repository wires
DDM into the site, themes it, and adds a few site-specific pieces.

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
- SQLite for local development; MariaDB in CI and production
- Signing in to the researcher interface (`/ddm/`) locally also needs SWITCH
  eduID OIDC credentials (`OIDC_RP_CLIENT_ID` / `OIDC_RP_CLIENT_SECRET`); the CMS
  and Django admin work without them

DDM ships its frontend as pre-built bundles, so there is no Node/npm build step.

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
# then edit .env and set DJANGO_SECRET (see the comment in the file)

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

### Authentication

The site has two separate login paths:

| Path                                        | Users                                 | Backend                                                                                       |
|---------------------------------------------|---------------------------------------|-----------------------------------------------------------------------------------------------|
| `/admin/` (Django admin), `/cms/` (Wagtail) | Local accounts from `createsuperuser` | Username / password + TOTP 2FA (enforced in production)                                       |
| `/ddm/` (researcher interface)              | UZH researchers                       | SWITCH eduID (OIDC); a linked affiliation mail ending in `uzh.ch` is required (`ddl/auth.py`) |

Study participants are not authenticated — they reach a donation project through
its public participation URL.

**Two-factor authentication** (`wagtail-2fa`) is required for every admin/CMS
account when `WAGTAIL_2FA_REQUIRED` is set (on in `config.settings.production`,
off in local/CI). On first sign-in a user is sent to enrol an authenticator app;
afterwards each session prompts once for a TOTP code. Manage your own devices via
the Wagtail account menu → *Manage your 2FA devices*; a superuser can reset a
locked-out user from Wagtail → Users → *Manage 2FA*. To exercise it locally, set
`WAGTAIL_2FA_REQUIRED = True` in `config/settings/local.py`.

---

## Environment Variables

All configuration is read from the environment; a local `.env` file is loaded
automatically. [`.env.example`](.env.example) is the complete, annotated list —
the essentials:

| Variable                                       | Scope                       | Notes                                                                                 |
|------------------------------------------------|-----------------------------|---------------------------------------------------------------------------------------|
| `DJANGO_SECRET`                                | all                         | Required. Generate with the command in `.env.example`.                                |
| `DJANGO_SETTINGS_MODULE`                       | all                         | `config.settings.local` (default), `.ci`, or `.production`.                           |
| `ALLOWED_HOSTS`                                | production                  | Comma- or space-separated host list.                                                  |
| `DJANGO_DB_HOST` / `_NAME` / `_USER` / `_PW`   | production                  | MariaDB connection.                                                                   |
| `EMAIL_HOST` / `_HOST_USER` / `_HOST_PASSWORD` | production                  | Authenticated SMTP, required. `EMAIL_PORT` (587) and `EMAIL_USE_TLS` (true) optional. |
| `SERVER_EMAIL` / `DEFAULT_FROM_EMAIL`          | production                  | From-addresses for error reports / ordinary mail.                                     |
| `ADMINS`                                       | production                  | JSON `[["Name", "mail"], …]`; recipients of error reports.                            |
| `OIDC_RP_CLIENT_ID` / `OIDC_RP_CLIENT_SECRET`  | any env using `/ddm/` login | SWITCH eduID client credentials.                                                      |
| `ZIP_BLUEPRINT_NAME`                           | where the ZIP API is used   | `DonationBlueprint` targeted by `ddl.apis.ZipPostAPI`.                                |
| `SEARCH_*`, `DIGITALMEAL_*`                    | `reports` app               | Project PKs / API keys for the legacy report views.                                   |

---

## Repository Management

### Branches

We work with three central branches:

- `dev`: Shared code, pre-deployment;
- `stage`: Deployed to stage for testing and QA before production.
- `main`: Deployed to production.

---

## Deployment

`stage` and `main` are deployed to the stage and production servers
respectively. Each target runs with `DJANGO_SETTINGS_MODULE=config.settings.production`
and, on the server:

```bash
pip install -r requirements/production.txt   # adds gunicorn + mysqlclient
python manage.py migrate
python manage.py collectstatic --noinput
```

- **App server:** gunicorn serving `config.wsgi:application`.
- **Database:** MariaDB (see the `DJANGO_DB_*` variables).
- **Static / media:** served by the reverse proxy from `STATIC_ROOT`
  (`<repo>/../staticfiles/`) and `MEDIA_ROOT` (`<repo>/../media/`).
- **TLS:** terminated at the proxy, which must set `X-Forwarded-Proto` (trusted
  via `SECURE_PROXY_SSL_HEADER`) and forward the real `Host` header.

Infrastructure specifics (web server, process manager) live outside this
repository.

---

## Day-to-day Development

### Running tests

```bash
python manage.py test                      # SQLite (config.settings.local)
python -m coverage run manage.py test
python -m coverage report                  # fails if coverage drops below 80 %
```

CI runs the suite against MariaDB with `config.settings.ci`. To reproduce that
locally, start a MariaDB with the credentials in `config/settings/ci.py`
(`127.0.0.1`, `root` / `password`, database `ddmtestdb`) and run:

```bash
DJANGO_SETTINGS_MODULE=config.settings.ci python manage.py test
```

### Linting and formatting

Usually, auto-run when committing, but good to know:

```bash
ruff check .                        # lint
ruff check . --fix                  # lint and auto-fix
ruff format .                       # format
djlint ddl/ --check                 # check templates (runs via pre-commit)
djlint ddl/ --reformat              # reformat templates
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

---

## Contact

- Website: https://datadonation.uzh.ch
- Issues: https://github.com/uzh/ddl/issues
- DDM documentation: https://uzh.github.io/ddm/ddm/
