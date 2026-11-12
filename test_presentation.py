from presentation import class_label, favicon, illustration


def test_illustration_is_generated_not_a_dataset_asset():
    image = illustration()
    assert image.size == (1000, 520)
    assert image.mode == "RGB"


def test_class_labels_are_not_diagnosis_wording():
    assert class_label("anemic") == "Anaemic class"
    assert class_label("non-anemic") == "Non-anaemic class"
    assert class_label("non_anemic") == "Non-anaemic class"
    assert class_label("unknown-model-label") == "unknown-model-label"


def test_favicon_is_a_small_generated_asset():
    assert favicon().size == (64, 64)
