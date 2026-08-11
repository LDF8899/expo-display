# Docker Compose Online Mode

This compose stack is for online-mode rehearsal:

```text
Nginx -> Python app -> MySQL
```

It does not start the onsite scanner hardware agent. The scanner agent remains part of the Windows onsite mode unless it is split into a separate onsite service later.

## Files

```text
Dockerfile
docker-compose.online.yml
deploy/nginx/expo-display.compose.conf
deploy/compose.env.example
```

## Start

```bash
cp deploy/compose.env.example .env
```

Edit `.env` and replace these values with real random secrets:

```text
MYSQL_ROOT_PASSWORD
MYSQL_PASSWORD
ADMIN_PASSWORD
CSRF_SECRET
```

Example generators:

```bash
openssl rand -base64 24
openssl rand -hex 32
```

Do not keep the `REPLACE_WITH_...` placeholder values. The app rejects placeholder admin passwords and CSRF secrets in online mode.

Then start the stack:

```bash
python scripts/deploy_preflight.py --env-file .env
docker compose -f docker-compose.online.yml --env-file .env up -d --build
```

## Open

```text
http://localhost:18080/display
http://localhost:18080/admin
```

## Check

```bash
docker compose -f docker-compose.online.yml --env-file .env ps
curl http://localhost:18080/api/ready
```

## Stop

```bash
docker compose -f docker-compose.online.yml --env-file .env down
```

To also delete the MySQL and upload volumes:

```bash
docker compose -f docker-compose.online.yml --env-file .env down -v
```
