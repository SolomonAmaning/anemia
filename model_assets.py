"""Retrieve only the existing public checkpoint, verified by size and SHA-256."""
import hashlib
from pathlib import Path
import tempfile
from urllib.request import urlopen

MODEL_URL = "https://media.githubusercontent.com/media/SolomonAmaning/anemia/main/runs/classify/train8/weights/best.pt"
MODEL_SHA256 = "881fd4ddc44392b415b891a3a8b3d221d79263509c905dc9c668aec596609ddc"
MODEL_SIZE = 10260737
DEPLOY_MODEL = Path(__file__).resolve().parent / ".models" / "anemia-classifier.pt"


def verified_checkpoint(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size != MODEL_SIZE:
        return False
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == MODEL_SHA256


def provision_checkpoint(destination=DEPLOY_MODEL):
    destination = Path(destination)
    if verified_checkpoint(destination):
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as file:
            temporary = Path(file.name)
            total = 0
            with urlopen(MODEL_URL, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > MODEL_SIZE:
                        raise ValueError("Downloaded checkpoint exceeds its expected size.")
                    file.write(chunk)
        if not verified_checkpoint(temporary):
            raise ValueError("Checkpoint size or SHA-256 verification failed; model will not be loaded.")
        temporary.replace(destination)
        return destination
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
