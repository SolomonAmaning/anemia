import hashlib
from io import BytesIO
from pathlib import Path

import pytest

import model_assets
from serve import preflight, require_staging_password, streamlit_command
from prepare_railway_payload import FILES, prepare_payload


@pytest.fixture
def tiny_checkpoint(monkeypatch):
    content = b"test checkpoint bytes"
    monkeypatch.setattr(model_assets, "MODEL_SIZE", len(content))
    monkeypatch.setattr(model_assets, "MODEL_SHA256", hashlib.sha256(content).hexdigest())
    return content


def test_verified_download_is_atomic(tmp_path, monkeypatch, tiny_checkpoint):
    monkeypatch.setattr(model_assets, "urlopen", lambda *args, **kwargs: BytesIO(tiny_checkpoint))
    destination = tmp_path / "model.pt"
    assert model_assets.provision_checkpoint(destination) == destination
    assert model_assets.verified_checkpoint(destination)
    assert list(tmp_path.iterdir()) == [destination]


def test_bad_hash_never_replaces_existing_file(tmp_path, monkeypatch, tiny_checkpoint):
    monkeypatch.setattr(model_assets, "urlopen", lambda *args, **kwargs: BytesIO(b"x" * len(tiny_checkpoint)))
    destination = tmp_path / "model.pt"
    destination.write_bytes(b"existing pointer")
    with pytest.raises(ValueError, match="verification failed"):
        model_assets.provision_checkpoint(destination)
    assert destination.read_bytes() == b"existing pointer"
    assert list(tmp_path.iterdir()) == [destination]


def test_oversized_download_is_rejected(tmp_path, monkeypatch, tiny_checkpoint):
    monkeypatch.setattr(model_assets, "urlopen", lambda *args, **kwargs: BytesIO(tiny_checkpoint + b"extra"))
    with pytest.raises(ValueError, match="expected size"):
        model_assets.provision_checkpoint(tmp_path / "model.pt")
    assert list(tmp_path.iterdir()) == []


def test_verified_file_is_reused_without_network(tmp_path, monkeypatch, tiny_checkpoint):
    destination = tmp_path / "model.pt"
    destination.write_bytes(tiny_checkpoint)
    monkeypatch.setattr(model_assets, "urlopen", lambda *args, **kwargs: pytest.fail("Unexpected network request"))
    assert model_assets.provision_checkpoint(destination) == destination


def test_railway_port_is_honoured():
    command = streamlit_command("8080")
    assert "--server.port=8080" in command
    assert "--server.address=0.0.0.0" in command
    assert "--browser.gatherUsageStats=false" in command


@pytest.mark.parametrize("port", ["not-a-port", "0", "65536"])
def test_invalid_port(port):
    with pytest.raises(ValueError):
        streamlit_command(port)


def test_docker_copies_only_app_files():
    dockerfile = (Path(__file__).parent / "Dockerfile").read_text()
    assert "COPY . ." not in dockerfile
    assert "USER appuser" in dockerfile
    assert "download.pytorch.org/whl/cpu" in dockerfile


def test_real_model_preflight(monkeypatch):
    from inference import model_path
    monkeypatch.setenv("ANEMIA_MODEL_PATH", str(model_path()))
    preflight()


def test_private_staging_requires_configured_password(monkeypatch):
    monkeypatch.setenv("ANEMIA_REQUIRE_PASSWORD", "true")
    monkeypatch.delenv("ANEMIA_DEMO_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="Private staging requires"):
        require_staging_password()


def test_private_staging_accepts_configured_password(monkeypatch):
    monkeypatch.setenv("ANEMIA_REQUIRE_PASSWORD", "true")
    monkeypatch.setenv("ANEMIA_DEMO_PASSWORD", "synthetic-test-password")
    require_staging_password()


def test_upload_payload_excludes_images_and_secrets(tmp_path):
    source = tmp_path / "source"
    for name in FILES:
        file = source / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("application file")
    (source / "patient-image.png").write_bytes(b"not for upload")
    (source / ".env").write_text("PRIVATE=do-not-upload")
    destination = prepare_payload(tmp_path / "payload", source)
    assert {str(p.relative_to(destination)) for p in destination.rglob("*") if p.is_file()} == set(FILES)


def test_upload_payload_refuses_unexpected_destination_files(tmp_path):
    destination = tmp_path / "payload"
    destination.mkdir()
    private_file = destination / "patient-image.png"
    private_file.write_bytes(b"must not be deleted or uploaded")
    with pytest.raises(ValueError, match="unexpected files"):
        prepare_payload(destination)
    assert private_file.exists()


def test_upload_payload_cannot_overwrite_source():
    with pytest.raises(ValueError, match="separate deployment"):
        prepare_payload(Path(__file__).parent)
