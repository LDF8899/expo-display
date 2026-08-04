# Online Mode Test Commands

Run these before changing deployment, authentication, permissions, review, upload, or database code.

## Core Checks

```bash
python scripts/deploy_preflight.py
python scripts/online_smoke_test.py
python scripts/online_workflow_test.py
python scripts/teacher_login_redirect_test.py
python scripts/role_isolation_test.py
python scripts/asset_management_test.py
python scripts/review_diff_test.py
python scripts/version_history_test.py
python scripts/deploy_precheck_test.py
python scripts/operations_dashboard_test.py
python scripts/operations_config_audit_test.py
python scripts/acceptance_report_test.py
```

If Docker is running, validate the real Compose online stack:

```bash
python scripts/compose_online_test.py
```

`online_workflow_test.py` covers the main online workflow:

```text
admin creates teacher
admin assigns project
teacher logs in
teacher submits page
admin approves review
admin deploys page
public display API returns the page
```

## Security Checks

```bash
python scripts/csrf_smoke_test.py
python scripts/xss_smoke_test.py
python scripts/auth_rate_limit_test.py
python scripts/password_policy_test.py
python scripts/runtime_config_test.py
```

## Upload Check

```bash
python scripts/upload_smoke_test.py
```

## Backup Script Checks

```bash
python scripts/backup_mysql.py --help
python scripts/restore_mysql.py --help
python scripts/backup_uploads.py --help
python scripts/deploy_preflight.py --help
```

## Full Local Regression

```bash
python -m py_compile server.py db_backend.py storage_backend.py html_sanitizer.py scripts/*.py
python scripts/deploy_preflight.py
python scripts/online_smoke_test.py
python scripts/online_workflow_test.py
python scripts/teacher_login_redirect_test.py
python scripts/compose_online_test.py
python scripts/role_isolation_test.py
python scripts/asset_management_test.py
python scripts/review_diff_test.py
python scripts/version_history_test.py
python scripts/deploy_precheck_test.py
python scripts/operations_dashboard_test.py
python scripts/operations_config_audit_test.py
python scripts/acceptance_report_test.py
python scripts/csrf_smoke_test.py
python scripts/upload_smoke_test.py
python scripts/xss_smoke_test.py
python scripts/auth_rate_limit_test.py
python scripts/password_policy_test.py
python scripts/runtime_config_test.py
```
