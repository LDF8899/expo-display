import argparse
import os
import zipfile
from pathlib import Path

from backup_common import ROOT, load_env_file, timestamp


def main():
    parser = argparse.ArgumentParser(description="Create a zip backup of local uploaded assets.")
    parser.add_argument("--env-file", default="", help="optional .env file to load")
    parser.add_argument("--upload-dir", default="", help="upload directory, defaults to UPLOAD_DIR or ./uploads")
    parser.add_argument("--out-dir", default=str(ROOT / "backups" / "uploads"), help="backup output directory")
    parser.add_argument("--output", default="", help="exact output .zip path")
    args = parser.parse_args()

    load_env_file(args.env_file)
    upload_dir = Path(args.upload_dir or os.environ.get("UPLOAD_DIR", ROOT / "uploads"))
    if not upload_dir.exists():
        raise SystemExit(f"upload directory not found: {upload_dir}")

    output = Path(args.output) if args.output else Path(args.out_dir) / f"uploads-{timestamp()}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    output_resolved = output.resolve()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in upload_dir.rglob("*"):
            if path.is_file():
                if path.resolve() == output_resolved:
                    continue
                archive.write(path, path.relative_to(upload_dir))
    print(output)


if __name__ == "__main__":
    main()
