import argparse
from pathlib import Path

from backup_common import ROOT, compose_command, load_env_file, mysql_env, run_streaming


def main():
    parser = argparse.ArgumentParser(description="Restore a MySQL logical backup.")
    parser.add_argument("backup", help="backup .sql file to restore")
    parser.add_argument("--env-file", default="", help="optional .env file to load")
    parser.add_argument("--compose", action="store_true", help="run mysql inside docker compose db service")
    parser.add_argument("--compose-file", default=str(ROOT / "docker-compose.online.yml"), help="compose file path")
    parser.add_argument("--service", default="db", help="compose database service name")
    parser.add_argument("--yes", action="store_true", help="confirm restore")
    args = parser.parse_args()

    if not args.yes:
        raise SystemExit("restore is destructive; rerun with --yes after verifying the target database")

    backup_path = Path(args.backup)
    if not backup_path.exists():
        raise SystemExit(f"backup file not found: {backup_path}")

    load_env_file(args.env_file)
    cfg = mysql_env()

    if args.compose:
        cmd = compose_command(
            args.compose_file,
            args.env_file,
            args.service,
            [
                "mysql",
                "--default-character-set=utf8mb4",
                "-u",
                cfg["user"],
                f"-p{cfg['password']}",
                cfg["database"],
            ],
        )
    else:
        cmd = [
            "mysql",
            "--default-character-set=utf8mb4",
            "-h",
            cfg["host"],
            "-P",
            str(cfg["port"]),
            "-u",
            cfg["user"],
            f"-p{cfg['password']}",
            cfg["database"],
        ]

    with backup_path.open("rb") as handle:
        run_streaming(cmd, stdin=handle)
    print(f"restored {backup_path} into {cfg['database']}")


if __name__ == "__main__":
    main()
