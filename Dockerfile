FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    YOLO_CONFIG_DIR=/tmp/ultralytics \
    ANEMIA_REQUIRE_PASSWORD=true

WORKDIR /app

# Ultralytics depends on OpenCV; these are its minimal Linux runtime libraries.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# CPU wheels avoid installing several gigabytes of unused CUDA dependencies.
RUN python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 torchvision==0.20.1 \
    && python -m pip install -r requirements.txt

# Explicitly copy app code only. No dataset, training images, logs or local secrets.
COPY anemia_prediction.py inference.py model_assets.py serve.py ./
COPY .streamlit/config.toml .streamlit/config.toml

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["python", "serve.py"]
