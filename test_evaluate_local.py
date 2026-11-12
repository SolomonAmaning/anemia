from pathlib import Path
from PIL import Image
import pytest

from evaluate_local import audit_dataset, binary_metrics, provisional_split


def directories(tmp_path):
    result = {label: tmp_path / label for label in ("anemic", "non-anemic")}
    for path in result.values():
        path.mkdir()
    return result


def test_pixel_duplicates_detected_across_file_formats(tmp_path):
    paths = directories(tmp_path)
    Image.new("RGB", (20, 20), "red").save(paths["anemic"] / "first.png")
    Image.new("RGB", (20, 20), "red").save(paths["anemic"] / "duplicate.bmp")
    Image.new("RGB", (20, 20), "blue").save(paths["non-anemic"] / "other.png")
    audit, records = audit_dataset(paths)
    assert audit["duplicate_extra_image_count"] == 1
    assert len(records) == 2
    assert audit["cross_label_conflict_group_count"] == 0


def test_conflicting_duplicate_labels_are_flagged(tmp_path):
    paths = directories(tmp_path)
    for path in paths.values():
        Image.new("RGB", (20, 20), "red").save(path / "image.png")
    audit, _ = audit_dataset(paths)
    assert audit["cross_label_conflict_group_count"] == 1


def test_corrupt_image_report_does_not_export_filename(tmp_path):
    paths = directories(tmp_path)
    (paths["anemic"] / "private-patient-name.png").write_bytes(b"not an image")
    Image.new("RGB", (20, 20), "blue").save(paths["non-anemic"] / "valid.png")
    audit, _ = audit_dataset(paths)
    assert audit["unreadable_image_count"] == 1
    assert "private-patient-name" not in str(audit)


def test_metrics_use_anemic_as_positive_and_scores_for_auc():
    result = binary_metrics([1, 1, 0, 0], [0.9, 0.4, 0.6, 0.1])
    assert result["sensitivity"] == 0.5
    assert result["specificity"] == 0.5
    assert result["roc_auc_from_model_scores"] == 0.75
    assert result["confusion_matrix"] == {"true_positive": 1, "false_negative": 1, "true_negative": 1, "false_positive": 1}


def test_absent_class_metrics_not_fabricated():
    result = binary_metrics([0, 0], [0.1, 0.2])
    assert result["sensitivity"] is None
    assert result["roc_auc_from_model_scores"] is None


@pytest.mark.parametrize("labels,scores", [([], []), ([1], [float("nan")]), ([1], [2]), ([2], [0.5])])
def test_invalid_metrics_input(labels, scores):
    with pytest.raises(ValueError):
        binary_metrics(labels, scores)


def test_provisional_split_is_reproducible_and_stratified():
    records = [
        {"label": label, "image_id": f"{label}-{index}", "fingerprint": f"{label}-{index:03d}"}
        for label in ("anemic", "non-anemic") for index in range(10)
    ]
    split = provisional_split(records)
    assert split == provisional_split(list(reversed(records)))
    for label in ("anemic", "non-anemic"):
        assert sum(r["split"] == "provisional_test" and r["folder_label"] == label for r in split) == 2
    assert len({r["pixel_sha256"] for r in split}) == len(split)
    assert "path" not in str(split)


def test_provisional_split_needs_each_class():
    with pytest.raises(ValueError, match="two unique"):
        provisional_split([])
