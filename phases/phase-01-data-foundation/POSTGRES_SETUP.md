# PostgreSQL Setup (Windows)

Your project expects:

```env
DATABASE_URL=postgresql://spotify:spotify@localhost:5432/spotify_nl
```

## Current check

```powershell
cd "c:\Users\Hp\OneDrive\Desktop\Spotify NL"
.\.venv\Scripts\python scripts\verify_db.py
```

If you see **connection refused**, PostgreSQL is not installed or not running.

---

## Option A — Install PostgreSQL natively (recommended on your machine)

Docker is not installed on your PC, so use a local PostgreSQL install.

### 1. Download and install

1. Open https://www.postgresql.org/download/windows/
2. Run the **EDB installer** (PostgreSQL 15 or 16)
3. During setup:
   - Port: **5432**
   - Superuser password: choose one and **remember it** (for user `postgres`)
   - Locale: default is fine
4. Keep **Stack Builder** unchecked unless you know you need extras
5. Finish install — ensure **pgAdmin** is included (optional but helpful)

### 2. Create project user and database

Open **SQL Shell (psql)** from Start Menu, or pgAdmin → Query Tool.

Login as `postgres`, then run the contents of:

```
scripts/setup_postgres.sql
```

In psql, after creating the database, connect to it first:

```sql
\c spotify_nl
GRANT ALL ON SCHEMA public TO spotify;
```

### 3. Verify

```powershell
.\.venv\Scripts\python scripts\verify_db.py
```

Expected: `OK: PostgreSQL connection successful`

### 4. Initialize app tables

```powershell
cd phases\phase-01-data-foundation
..\..\.venv\Scripts\python cli\scrape.py init-db

cd ..\phase-02-ai-understanding
..\..\.venv\Scripts\python cli\extract.py init-db
```

### 5. Smoke test scrape

```powershell
cd phases\phase-01-data-foundation
..\..\.venv\Scripts\python cli\scrape.py scrape --limit 50
```

---

## Option B — Docker Desktop (if you prefer containers)

1. Install **Docker Desktop** for Windows
2. Restart PC if prompted
3. Run:

```powershell
cd phases\phase-01-data-foundation
docker compose up -d
```

This starts PostgreSQL with user `spotify`, password `spotify`, database `spotify_nl` — no `setup_postgres.sql` needed.

Then:

```powershell
..\..\.venv\Scripts\python scripts\verify_db.py
..\..\.venv\Scripts\python cli\scrape.py init-db
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `connection refused` | Start service: Services → `postgresql-x64-16` → Start |
| `password authentication failed` | Re-run `setup_postgres.sql` or fix password in `.env` |
| Port 5432 in use | Another app uses 5432; change port in install + `.env` |
| `role "spotify" does not exist` | Run `scripts/setup_postgres.sql` |

## What to tell the assistant after setup

Reply with the output of:

```powershell
.\.venv\Scripts\python scripts\verify_db.py
```

If OK, we can run scrape + Phase 2 extraction together.
