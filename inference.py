"""Model loading and image validation, independent of the Streamlit UI."""
import os
from pathlib import Path

from PIL import Image, ImageOps

DEFAULT_MODEL = Path(__file__).resolve().parent / "runs/classify/train8/weights/best.pt"
MAX_BYTES = 10 * 1024 * 1024


def model_path():
    path = Path(os.getenv("ANEMIA_MODEL_PATH", str(DEFAULT_MODEL))).expanduser()
    if not path.is_file():
        raise ValueError("Model weights are missing. Run git lfs pull or set ANEMIA_MODEL_PATH.")
    with path.open("rb") as file:
        if file.read(80).startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError("Weights are a Git LFS pointer, not a model. Run git lfs pull.")
    return path


def load_model():
    from ultralytics import YOLO
    model = YOLO(str(model_path()))
    if model.task != "classify":
        raise ValueError("A classification model is required.")
    return model


def read_image(file):
    if file.size > MAX_BYTES:
        raise ValueError("Image must be 10 MB or smaller.")
    image = Image.open(file)
    if image.width * image.height > 20_000_000:
        raise ValueError("Image dimensions exceed the 20 megapixel limit.")
    return ImageOps.exif_transpose(image).convert("RGB")


def classify(model, image):
    result = model.predict(image, verbose=False)[0]
    if result.probs is None:
        raise ValueError("The model did not return classification probabilities.")
    return result.names[int(result.probs.top1)], float(result.probs.top1conf)
