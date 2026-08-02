import argparse
import os
from pathlib import Path

from backup_common import ROOT, compose_command, load_env_file, mysql_env, run_streaming, timestamp


def main():
    parser = argparse.ArgumentParser(description="Create a MySQL logical backup.")
    parser.add_argument("--env-file", default="", help="optional .env file to load")
    parser.add_argument("--out-dir", default=str(ROOT / "backups" / "mysql"), help="backup output directory")
    parser.add_argument("--output", default="", help="exact output .sql path")
    parser.add_argument("--compose", action="store_true", help="run mysqldump inside docker compose db service")
    parser.add_argument("--compose-file", default=str(ROOT / "docker-compose.online.yml"), help="compose file path")
    parser.add_argument("--service", default="db", help="compose database service name")
    args = parser.parse_args()

    load_env_file(args.env_file)
    cfg = mysql_env()
    output = Path(args.output) if args.output else Path(args.out_dir) / f"{cfg['database']}-{timestamp()}.sql"
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.compose:
        cmd = compose_command(
            args.compose_file,
            args.env_file,
            args.service,
            [
                "mysqldump",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--default-character-set=utf8mb4",
                "-u",
                cfg["user"],
                f"-p{cfg['password']}",
                cfg["database"],
            ],
        )
    else:
        cmd = [
            "mysqldump",
            "--single-transaction",
            "--routines",
            "--triggers",
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

    with output.open("wb") as handle:
        run_streaming(cmd, stdout=handle)
    print(output)


if __name__ == "__main__":
    main()
