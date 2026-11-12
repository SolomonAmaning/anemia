"""Railway entry point: validate model execution before starting Streamlit."""
import os
from pathlib import Path
import sys


def streamlit_command(port):
    port = int(port)
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be an integer between 1 and 65535.")
    return [
        sys.executable, "-m", "streamlit", "run",
        str(Path(__file__).resolve().parent / "anemia_prediction.py"),
        "--server.address=0.0.0.0", f"--server.port={port}",
        "--server.headless=true", "--browser.gatherUsageStats=false",
    ]


def preflight():
    from PIL import Image
    from inference import classify, load_model
    from model_assets import provision_checkpoint

    if not os.getenv("ANEMIA_MODEL_PATH"):
        os.environ["ANEMIA_MODEL_PATH"] = str(provision_checkpoint())
    model = load_model()
    # Checks execution only; this image provides no clinical evaluation evidence.
    classify(model, Image.new("RGB", (224, 224), "pink"))


def require_staging_password():
    if os.getenv("ANEMIA_REQUIRE_PASSWORD", "").lower() == "true" and not os.getenv("ANEMIA_DEMO_PASSWORD"):
        raise ValueError("Private staging requires ANEMIA_DEMO_PASSWORD in Railway service variables.")


if __name__ == "__main__":
    command = streamlit_command(os.getenv("PORT", "8501"))
    require_staging_password()
    preflight()
    print("Checkpoint loaded and synthetic execution check passed. Starting research demo.", flush=True)
    os.execv(sys.executable, command)
