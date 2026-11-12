"""Conjunctival-image research interface. Not a diagnostic device."""
import streamlit as st
from inference import classify, load_model, read_image

st.set_page_config(page_title="Conjunctiva Lab | Solomon Odum", layout="wide")


@st.cache_resource
def get_model():
    return load_model()


st.caption("SOLOMON ODUM / ACCESSIBLE HEALTHCARE AI")
st.title("Conjunctiva Lab")
st.write("An image-based anaemia screening research prototype. Inspect model outputs with the limitations in view.")
st.warning("Research only—not a diagnosis. Requires external validation and clinical evaluation. Model scores are not calibrated probabilities of anaemia. Confirm suspected anaemia through appropriate clinical assessment and laboratory testing.")

st.sidebar.title("Research workspace")
st.sidebar.caption("MODEL / YOLOv8 classification")
st.sidebar.write("Single-image and batch inference")
st.sidebar.write("Outputs use the trained model's class labels, not an assumed class order.")
st.sidebar.info("Use consented, de-identified research images only. Do not upload identifiable patient images to a public demo.")

try:
    model = get_model()
except Exception as error:
    st.error(f"Model unavailable: {error}")
    st.stop()

a, b, c = st.columns(3)
a.metric("Model status", "Loaded")
b.metric("Classification labels", str(len(model.names)))
c.metric("Intended use", "Research")
st.caption("Loaded checkpoint: runs/classify/train8/weights/best.pt (or ANEMIA_MODEL_PATH override).")

left, right = st.columns([2, 1], gap="large")
with left:
    st.subheader("Image workspace")
    st.write("Upload a clear conjunctival image to inspect the classifier output. JPG, JPEG or PNG; up to 10 MB and 20 megapixels per image.")
    consent = st.checkbox("I am using consented, de-identified research images.")
    files = st.file_uploader("Research images", type=["jpg", "png", "jpeg"], accept_multiple_files=True, disabled=not consent)
    if files:
        for file in files:
            try:
                image = read_image(file)
                label, score = classify(model, image)
                st.image(image, caption=file.name, use_container_width=True)
                st.metric("Model class · not a diagnosis", label.replace("_", " "))
                st.progress(score, text=f"Model class score: {score:.1%} · not calibrated clinical confidence")
            except Exception as error:
                st.error(f"Could not process {file.name}: {error}")
with right:
    st.subheader("How the prototype works")
    st.write("01 / Image preparation\n\nValidate dimensions, correct orientation and convert to RGB.")
    st.write("02 / Model inference\n\nRun the repository's trained YOLOv8 classification checkpoint locally.")
    st.write("03 / Human interpretation\n\nDisplay the model label and score without asserting a clinical diagnosis.")
    st.divider()
    st.caption("No sensitivity, specificity or clinical accuracy claim is implied by this demo. A general classifier does not verify that an input is a conjunctiva image.")
