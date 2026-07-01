-- Run once as PostgreSQL superuser (usually "postgres") after installing PostgreSQL.
-- Matches config/.env.example:
--   DATABASE_URL=postgresql://spotify:spotify@localhost:5432/spotify_nl

CREATE USER spotify WITH PASSWORD 'spotify';

CREATE DATABASE spotify_nl OWNER spotify;

GRANT ALL PRIVILEGES ON DATABASE spotify_nl TO spotify;

-- Connect to spotify_nl before running the line below:
-- \c spotify_nl
GRANT ALL ON SCHEMA public TO spotify;
