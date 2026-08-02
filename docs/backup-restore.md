# Backup And Restore

Back up two things:

```text
MySQL data: users, projects, pages, review records, scans, logs, asset metadata
Uploaded assets: image files under uploads/ or the configured object-storage bucket
```

If assets are stored in S3/COS/OSS, use the cloud provider's bucket versioning, lifecycle rules, and cross-region backup instead of `backup_uploads.py`.

## MySQL Backup

Local MySQL:

```bash
python scripts/backup_mysql.py --env-file .env
```

Docker Compose MySQL:

```bash
python scripts/backup_mysql.py --env-file .env --compose
```

By default backups are written to:

```text
backups/mysql/
```

## MySQL Restore

Restore is destructive. Verify the target database first.

Local MySQL:

```bash
python scripts/restore_mysql.py backups/mysql/expo_display-YYYYMMDDTHHMMSSZ.sql --env-file .env --yes
```

Docker Compose MySQL:

```bash
python scripts/restore_mysql.py backups/mysql/expo_display-YYYYMMDDTHHMMSSZ.sql --env-file .env --compose --yes
```

## Local Upload Backup

For local asset storage:

```bash
python scripts/backup_uploads.py --env-file .env
```

By default backups are written to:

```text
backups/uploads/
```

For Docker Compose local assets, copy from the named volume first or run a one-off container, for example:

```bash
docker run --rm -v expo-display_uploaded-assets:/assets -v "%cd%/backups/uploads:/backup" alpine sh -c "cd /assets && tar czf /backup/uploads-$(date -u +%Y%m%dT%H%M%SZ).tar.gz ."
```

On Linux/macOS replace `%cd%` with `$(pwd)`.

## Suggested Schedule

```text
MySQL: daily, keep at least 14 copies
Uploaded assets: daily if local, or enable bucket versioning if object storage is used
Restore drill: monthly, into a separate test database
```
