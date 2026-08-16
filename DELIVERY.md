# Expo Display Delivery

This is a clean deliverable copy created from branch `2.2` on 2026-08-12.

## Included

- Application source: `server.py`, `db_backend.py`, `storage_backend.py`, `html_sanitizer.py`, `start_expo.py`
- Frontend assets required by the running pages: `static/`
- Current lightweight uploaded image assets: `uploads/`
- Current SQLite database snapshot: `database/expo-latest.db`
- SQLite SQL export: `database/expo_display_sqlite_snapshot_20260812.sql`
- MySQL schema and older 2.1 SQL reference: `database/mysql_schema.sql`, `database/expo_display_2_1.sql`
- Deployment docs/scripts: `deploy/`, `docs/`, `scripts/`, `scanner-agent/`

## Excluded

- Git metadata and local tool caches: `.git/`, `.playwright-cli/`, `__pycache__/`
- Runtime logs, old backup databases, previous output folders
- Real local `.env` files containing passwords
- Unity WebGL package: `uploads/unityceshi111/`
- Homestay desktop model package: `uploads/minsu/` (`uploads/民宿/` in the source tree)
- Original page material folder and generated preview outputs: `sucai/page-materials/` (`sucai/页面/` in the source tree), `sucai/output/`

## Run Locally

Copy `.env.example` to `.env`, replace `ADMIN_PASSWORD` and `CSRF_SECRET`, then run:

```powershell
python .\server.py
```

Open:

```text
http://127.0.0.1:8000/display
http://127.0.0.1:8000/admin
```

The deliverable is configured for SQLite by default:

```text
DATABASE_BACKEND=sqlite
DB_PATH=database/expo-latest.db
```

Use the SQL export only when a text snapshot is needed; the app can run directly from `database/expo-latest.db`.
