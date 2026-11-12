"""Prepare an app-only Railway upload; never include training images or secrets."""
import argparse
from pathlib import Path
import shutil

APP_ROOT = Path(__file__).resolve().parent
FILES = (
    "Dockerfile", "requirements.txt", "anemia_prediction.py", "inference.py",
    "model_assets.py", "serve.py", "presentation.py", ".dockerignore", ".streamlit/config.toml",
)


def prepare_payload(destination, source=APP_ROOT):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination == source or destination in source.parents:
        raise ValueError("Destination must be a separate deployment-payload directory.")
    if destination.exists():
        if any(path.is_symlink() for path in destination.rglob("*")):
            raise ValueError("Symbolic links are not allowed in a deployment payload.")
        unexpected = {
            str(path.relative_to(destination))
            for path in destination.rglob("*") if path.is_file()
        } - set(FILES)
        if unexpected:
            raise ValueError("Destination contains unexpected files; refusing to upload or remove them.")
    for name in FILES:
        original = source / name
        target = destination / name
        if original.is_symlink() or original.parent.is_symlink() or target.is_symlink():
            raise ValueError("Symbolic links are not allowed in a deployment payload.")
        if not original.is_file():
            raise ValueError(f"Missing application file: {name}")
    destination.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    actual = {str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file()}
    if actual != set(FILES):
        raise ValueError("Deployment payload verification failed.")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", default=str(APP_ROOT / ".local-deploy/payload"))
    args = parser.parse_args()
    result = prepare_payload(args.destination)
    print(f"Application-only payload prepared at {result}; {len(FILES)} files, no dataset or secrets.")
