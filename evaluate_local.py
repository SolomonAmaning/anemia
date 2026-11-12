"""Local dataset audit and checkpoint consistency check. Never uploads images."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageOps

EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}
LABELS = ("anemic", "non-anemic")
LIMITATION = (
    "Local dataset consistency check, NOT an independent test or clinical validation. "
    "Training overlap and patient-level independence are unknown. Folder labels have "
    "not been verified against haemoglobin measurements. No patient benefit is established."
)


def audit_dataset(class_dirs):
    records = []
    issues = []
    for label in LABELS:
        directory = Path(class_dirs[label])
        if not directory.is_dir():
            raise ValueError(f"Missing directory for {label}.")
        paths = sorted(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in EXTENSIONS)
        if not paths:
            raise ValueError(f"No supported images for {label}.")
        for path in paths:
            # Do not include identifying filenames in exported reports or console output.
            image_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]
            try:
                with Image.open(path) as source:
                    has_exif = bool(source.getexif())
                    if source.width * source.height > 20_000_000:
                        raise ValueError("Image exceeds 20 megapixels")
                    image = ImageOps.exif_transpose(source).convert("RGB")
                    image.load()
                fingerprint = hashlib.sha256(
                    f"RGB:{image.width}:{image.height}:".encode() + image.tobytes()
                ).hexdigest()
                records.append({
                    "path": path, "label": label, "image_id": image_id,
                    "fingerprint": fingerprint, "width": image.width,
                    "height": image.height, "has_exif": has_exif,
                })
            except Exception as error:
                issues.append({"image_id": image_id, "label": label, "error_type": type(error).__name__})

    by_fingerprint = defaultdict(list)
    for record in records:
        by_fingerprint[record["fingerprint"]].append(record)
    conflicts = [group for group in by_fingerprint.values() if len({r["label"] for r in group}) > 1]
    duplicate_groups = [group for group in by_fingerprint.values() if len(group) > 1]
    unique = [group[0] for group in by_fingerprint.values()]
    audit = {
        "raw_class_counts": dict(Counter(r["label"] for r in records)),
        "unique_class_counts": dict(Counter(r["label"] for r in unique)),
        "valid_image_count": len(records), "unique_pixel_image_count": len(unique),
        "unreadable_image_count": len(issues), "unreadable_images": issues,
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_extra_image_count": len(records) - len(unique),
        "cross_label_conflict_group_count": len(conflicts),
        "images_with_exif_metadata": sum(r["has_exif"] for r in records),
        "width_range_px": [min(r["width"] for r in records), max(r["width"] for r in records)] if records else None,
        "height_range_px": [min(r["height"] for r in records), max(r["height"] for r in records)] if records else None,
        "patient_grouping": "Unknown; no patient-level mapping supplied.",
        "training_overlap": "Unknown; original training images are inaccessible or unavailable.",
    }
    return audit, unique


def binary_metrics(labels, probabilities, threshold=0.5):
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    if len(labels) == 0 or labels.shape != probabilities.shape:
        raise ValueError("Labels and probabilities must be non-empty and have the same shape.")
    if not set(labels.tolist()).issubset({0, 1}) or not np.isfinite(probabilities).all():
        raise ValueError("Invalid labels or non-finite probabilities.")
    if ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("Probabilities must be between zero and one.")
    predicted = probabilities >= threshold
    tp = int(np.sum((labels == 1) & predicted))
    fn = int(np.sum((labels == 1) & ~predicted))
    tn = int(np.sum((labels == 0) & ~predicted))
    fp = int(np.sum((labels == 0) & predicted))
    def ratio(numerator, denominator):
        return numerator / denominator if denominator else None
    sensitivity = ratio(tp, tp + fn)
    specificity = ratio(tn, tn + fp)
    precision = ratio(tp, tp + fp)
    positive = probabilities[labels == 1]
    negative = probabilities[labels == 0]
    # Pairwise probability comparison, including half credit for ties.
    auc = float(np.mean((positive[:, None] > negative) + 0.5 * (positive[:, None] == negative))) if len(positive) and len(negative) else None
    return {
        "positive_label": "anemic", "threshold": threshold,
        "image_count": len(labels), "accuracy": (tp + tn) / len(labels),
        "balanced_accuracy": (sensitivity + specificity) / 2 if sensitivity is not None and specificity is not None else None,
        "precision": precision, "sensitivity": sensitivity, "specificity": specificity,
        "f1": ratio(2 * tp, 2 * tp + fp + fn), "roc_auc_from_model_scores": auc,
        "confusion_matrix": {"true_positive": tp, "false_negative": fn, "true_negative": tn, "false_positive": fp},
    }


def provisional_split(records, test_fraction=0.2, seed=42):
    """Reserve deduplicated images now, without claiming prior training exclusion."""
    if not 0 < test_fraction < 1:
        raise ValueError("Test fraction must be between zero and one.")
    generator = np.random.default_rng(seed)
    manifest = []
    for label in LABELS:
        group = sorted((r for r in records if r["label"] == label), key=lambda r: r["fingerprint"])
        if len(group) < 2:
            raise ValueError("At least two unique images per class are needed for a provisional split.")
        count = min(len(group) - 1, max(1, math.ceil(len(group) * test_fraction)))
        reserved = set(generator.choice(len(group), size=count, replace=False).tolist())
        for index, record in enumerate(group):
            manifest.append({
                "image_id": record["image_id"], "pixel_sha256": record["fingerprint"],
                "folder_label": label, "split": "provisional_test" if index in reserved else "development",
            })
    return manifest


def evaluate_checkpoint(records):
    from inference import load_model, model_path
    model = load_model()
    names = model.names
    matching = [int(index) for index, name in names.items() if name == "anemic"]
    if len(matching) != 1 or set(names.values()) != set(LABELS):
        raise ValueError("Checkpoint labels do not match anemic/non-anemic dataset labels.")
    positive_index = matching[0]
    labels, probabilities, predictions = [], [], []
    started = time.perf_counter()
    for index, record in enumerate(records):
        with Image.open(record["path"]) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            result = model.predict(image, verbose=False, device="cpu")[0]
        if result.probs is None:
            raise ValueError("Checkpoint did not return class probabilities.")
        score = float(result.probs.data[positive_index])
        labels.append(int(record["label"] == "anemic"))
        probabilities.append(score)
        predictions.append({"image_id": record["image_id"], "folder_label": record["label"], "anemic_class_score": score})
        if (index + 1) % 50 == 0:
            print(f"Processed {index + 1}/{len(records)} unique images locally.", flush=True)
    return {
        "metrics": binary_metrics(labels, probabilities),
        "checkpoint_sha256": hashlib.sha256(model_path().read_bytes()).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
        "model_labels": names, "predictions": predictions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anemic-dir", required=True)
    parser.add_argument("--non-anemic-dir", required=True)
    parser.add_argument("--output-dir", default=".local-evaluation")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    audit, records = audit_dataset({"anemic": args.anemic_dir, "non-anemic": args.non_anemic_dir})
    report = {"purpose": LIMITATION, "audit": audit}
    if not args.audit_only:
        if audit["cross_label_conflict_group_count"] or audit["unreadable_image_count"]:
            report["evaluation_status"] = "blocked_by_dataset_integrity"
        else:
            split = provisional_split(records, args.test_fraction, args.seed)
            (output / "provisional-split.json").write_text(json.dumps({
                "purpose": LIMITATION,
                "split_note": "Reserved now at image level. Not established as unseen by the existing model; not patient-disjoint.",
                "seed": args.seed, "test_fraction": args.test_fraction, "images": split,
            }, indent=2))
            report["evaluation"] = evaluate_checkpoint(records)
            reserved_ids = {r["image_id"] for r in split if r["split"] == "provisional_test"}
            reserved_predictions = [r for r in report["evaluation"]["predictions"] if r["image_id"] in reserved_ids]
            report["provisional_test_check"] = {
                "purpose": "Image-level subset check only. Previous training overlap unknown; no model retraining or threshold selection performed.",
                "class_counts": dict(Counter(r["folder_label"] for r in reserved_predictions)),
                "metrics": binary_metrics(
                    [int(r["folder_label"] == "anemic") for r in reserved_predictions],
                    [r["anemic_class_score"] for r in reserved_predictions],
                ),
            }
            report["evaluation_status"] = "completed_consistency_check_only"
    (output / "dataset-check.json").write_text(json.dumps(report, indent=2))
    summary = {"purpose": report["purpose"], "audit": audit, "evaluation_status": report.get("evaluation_status")}
    if "evaluation" in report:
        summary["metrics"] = report["evaluation"]["metrics"]
        summary["elapsed_seconds"] = report["evaluation"]["elapsed_seconds"]
        summary["provisional_test_check"] = report["provisional_test_check"]
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
