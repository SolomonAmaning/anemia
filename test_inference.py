from io import BytesIO
from types import SimpleNamespace
from PIL import Image
import pytest
from streamlit.testing.v1 import AppTest
from inference import classify, load_model, model_path, read_image


def test_lfs_pointer_has_actionable_error(tmp_path, monkeypatch):
    path = tmp_path / "best.pt"
    path.write_text("version https://git-lfs.github.com/spec/v1\n")
    monkeypatch.setenv("ANEMIA_MODEL_PATH", str(path))
    with pytest.raises(ValueError, match="Git LFS pointer"):
        model_path()


def test_missing_weights(tmp_path, monkeypatch):
    monkeypatch.setenv("ANEMIA_MODEL_PATH", str(tmp_path / "absent.pt"))
    with pytest.raises(ValueError, match="missing"):
        model_path()


def test_model_labels_not_assumed_order():
    result = SimpleNamespace(probs=SimpleNamespace(top1=0, top1conf=0.7), names={0: "non_anemic", 1: "anemic"})
    model = SimpleNamespace(predict=lambda *args, **kwargs: [result])
    assert classify(model, Image.new("RGB", (32, 32))) == ("non_anemic", 0.7)


def test_image_validation():
    file = BytesIO()
    Image.new("RGB", (64, 64)).save(file, format="PNG")
    file.size = file.tell()
    file.seek(0)
    assert read_image(file).mode == "RGB"
    file.size = 11 * 1024 * 1024
    with pytest.raises(ValueError, match="10 MB"):
        read_image(file)


def test_actual_checkpoint_smoke():
    # Synthetic blank image tests execution only, never clinical validity.
    model = load_model()
    label, score = classify(model, Image.new("RGB", (224, 224), "pink"))
    assert label in model.names.values()
    assert 0 <= score <= 1


def test_app_loads():
    from pathlib import Path
    app = AppTest.from_file(str(Path(__file__).parent / "anemia_prediction.py")).run(timeout=90)
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "Loaded"


def test_private_demo_gate(monkeypatch):
    from pathlib import Path
    monkeypatch.setenv("ANEMIA_DEMO_PASSWORD", "synthetic-test-password")
    app = AppTest.from_file(str(Path(__file__).parent / "anemia_prediction.py")).run(timeout=90)
    assert not app.exception
    assert len(app.metric) == 0
    app.text_input[0].set_value("incorrect").run(timeout=90)
    assert len(app.metric) == 0
    app.text_input[0].set_value("synthetic-test-password").run(timeout=90)
    assert not app.exception
    assert app.metric[0].value == "Loaded"


def test_actual_image_format_is_checked():
    file = BytesIO()
    Image.new("RGB", (32, 32), "pink").save(file, format="BMP")
    file.size = file.tell()
    file.seek(0)
    with pytest.raises(ValueError, match="contents must be JPEG or PNG"):
        read_image(file)
