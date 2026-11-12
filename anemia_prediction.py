"""A clear, human-reviewed research interface. Not a diagnostic device."""
import hashlib
import hmac
import json
import os

import streamlit as st

from inference import classify, load_model, read_image
from presentation import BRAND, STYLES, WORKFLOW, class_label, favicon, illustration

st.set_page_config(page_title="Conjunctiva · Anaemia screening research", page_icon=favicon(), layout="wide")
st.markdown(STYLES, unsafe_allow_html=True)


@st.cache_resource
def get_model():
    return load_model()


@st.cache_data
def example_image():
    return illustration()


def clear_workspace():
    st.session_state.pop("analysis", None)
    st.session_state.pop("walkthrough", None)
    st.session_state.pop("research_consent", None)
    st.session_state["upload_version"] = st.session_state.get("upload_version", 0) + 1


def lock_demo():
    clear_workspace()
    st.session_state["demo_authenticated"] = False
    st.session_state.pop("login_failed", None)


def access_screen(password):
    def submit_access():
        entered = st.session_state.get("demo_access_input", "")
        allowed = hmac.compare_digest(entered.encode(), password.encode())
        st.session_state["demo_authenticated"] = allowed
        st.session_state["login_failed"] = not allowed
        if allowed:
            st.session_state.pop("demo_access_input", None)

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown('<div class="login-brand">CONJUNCTIVA / CLINICAL AI RESEARCH</div>', unsafe_allow_html=True)
        st.title("A research workspace for anaemia screening.")
        st.markdown('<p class="lead">Explore an anaemia research prototype—from a conjunctival image to a model output that stays open to human review.</p>', unsafe_allow_html=True)
        st.image(example_image(), use_container_width=True)
        st.caption("Schematic illustration only. No patient image or clinical finding is shown.")
    with right:
        with st.container(border=True, key="access_card"):
            st.caption("RESEARCH DEMO ACCESS")
            st.subheader("Open the workspace")
            st.write("Use the demo password provided by Solomon. This is an educational research prototype, not a clinical service.")
            with st.form("demo_access"):
                st.text_input("Demo access password", type="password", key="demo_access_input")
                st.form_submit_button("Open research demo", type="primary", use_container_width=True, on_click=submit_access)
            if st.session_state.get("login_failed"):
                st.error("That password did not match. Please try again.")
            st.caption("Do not upload protected health information. A shared demo password is not a medical-data privacy control.")
            st.link_button("About this project", "https://solomonodum.com/projects/low-cost-vision-screening", use_container_width=True)


password = os.getenv("ANEMIA_DEMO_PASSWORD")
if password and not st.session_state.get("demo_authenticated", False):
    access_screen(password)
    st.stop()

with st.sidebar:
    st.markdown(BRAND, unsafe_allow_html=True)
    st.markdown('<div class="side-section">THE WORKFLOW</div>', unsafe_allow_html=True)
    st.write("Choose a research image. Run the model. Review the output with its limits in view.")
    st.markdown('<div class="side-line"></div><div class="side-section">DESIGNED FOR REVIEW</div>', unsafe_allow_html=True)
    st.write("Assistive research, not automated diagnosis.")
    st.caption("Use authorised, de-identified images only. Uploads are processed in server memory; the app does not write them to disk or send them to an AI API.")
    st.markdown('<div class="side-line"></div>', unsafe_allow_html=True)
    if password:
        st.button("Lock demo", on_click=lock_demo, use_container_width=True)
    st.markdown('<div class="side-section">BUILT BY SOLOMON ODUM</div>', unsafe_allow_html=True)
    st.link_button("View portfolio", "https://solomonodum.com/projects/low-cost-vision-screening", use_container_width=True)

eyebrow, actions = st.columns([5, 1])
with eyebrow:
    st.markdown('<div class="eyebrow">ACCESSIBLE HEALTHCARE AI / RESEARCH PROTOTYPE</div>', unsafe_allow_html=True)
with actions:
    st.button("Start again", on_click=clear_workspace, use_container_width=True)
st.title("Explore image-based anaemia screening.")
st.markdown('<p class="lead">A clear path from image input to a reviewable model output—with clinical judgement and research limitations kept visible.</p>', unsafe_allow_html=True)
st.markdown('<div class="research-note"><strong>Research only—not a diagnosis.</strong> This prototype is not clinically validated. Model scores are not probabilities that a person has anaemia.</div>', unsafe_allow_html=True)

workspace, notes = st.tabs(["Research workspace", "Methods & limitations"])

with workspace:
    st.markdown(WORKFLOW, unsafe_allow_html=True)
    input_column, result_column = st.columns([1.15, 0.85], gap="large")
    source = None
    files = []
    signature = None
    selected = None
    preview = None
    valid_batch = True
    with input_column:
        with st.container(border=True, key="input_panel"):
            st.markdown('<div class="panel-kicker">01 / IMAGE INPUT</div>', unsafe_allow_html=True)
            st.subheader("Image workspace")
            source = st.radio("Input source", ["Illustrated example", "Upload research image"], horizontal=True)
            if source == "Illustrated example":
                st.image(example_image(), use_container_width=True)
                st.caption("Drawn illustration—not a patient image. It is not submitted to the classifier.")
                st.button("Explore example workflow", type="primary", use_container_width=True, on_click=lambda: st.session_state.update(walkthrough=True))
            else:
                st.write("Choose a clear, cropped conjunctival image. Avoid blur, harsh shadows and colour filters. Image preparation alone does not establish clinical suitability.")
                consent = st.checkbox("I confirm these are authorised, de-identified research images.", key="research_consent")
                batch = st.checkbox("Batch mode · up to five images", key="batch_mode")
                uploaded = st.file_uploader("Research image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=batch, disabled=not consent, key=f"image_upload_{st.session_state.get('upload_version', 0)}")
                files = (uploaded or []) if batch else ([uploaded] if uploaded else [])
                if len(files) > 5:
                    st.error("Choose at most five images per batch.")
                    valid_batch = False
                if files and valid_batch:
                    digest = hashlib.sha256()
                    for file in files:
                        digest.update(file.name.encode())
                        digest.update(file.getvalue())
                    signature = digest.hexdigest()
                    selected = st.selectbox("Preview image", range(len(files)), format_func=lambda index: files[index].name) if batch else 0
                    try:
                        preview = read_image(files[selected])
                        st.image(preview, caption=files[selected].name, use_container_width=True)
                        st.caption(f"Image decoded · {preview.width} × {preview.height} pixels · RGB")
                    except Exception:
                        st.error("This file could not be opened as a supported image. Use a JPEG or PNG, up to 10 MB and 20 megapixels.")
                run = st.button("Run research analysis", type="primary", use_container_width=True, disabled=not (consent and files and valid_batch and preview is not None))
                if run:
                    rows = []
                    with st.spinner("Preparing images and running the research model…"):
                        try:
                            model = get_model()
                        except Exception:
                            st.error("The research engine is temporarily unavailable. Try again later.")
                            model = None
                        if model is not None:
                            for file in files:
                                try:
                                    image = read_image(file)
                                    label, score = classify(model, image)
                                    rows.append({"file": file.name, "model_class": label, "model_score_uncalibrated": score, "width_px": image.width, "height_px": image.height, "status": "complete"})
                                except Exception:
                                    rows.append({"file": file.name, "status": "unable_to_process"})
                            st.session_state["analysis"] = {"signature": signature, "rows": rows}
                st.caption("JPEG or PNG · 10 MB per file · 20 megapixels maximum. No identifying patient information.")

    with result_column:
        with st.container(border=True, key="review_panel"):
            st.markdown('<div class="panel-kicker">02 / RESULT REVIEW</div>', unsafe_allow_html=True)
            st.subheader("Review workspace")
            analysis = st.session_state.get("analysis")
            if source == "Illustrated example":
                if st.session_state.get("walkthrough"):
                    st.markdown('<span class="status-label">ILLUSTRATIVE WALKTHROUGH</span><div class="review-title">The workflow, without patient data.</div><p class="review-copy">The example shows how the workspace is organised. No clinical classification was performed.</p><div class="check-row"><strong>Image preview</strong><span>A schematic illustration, clearly marked as synthetic.</span></div><div class="check-row"><strong>Model output</strong><span>Available only after an authorised research image is analysed.</span></div><div class="check-row"><strong>Human review</strong><span>Interpret outputs alongside validation evidence and clinical judgement.</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="review-title">From image to careful review.</div><p class="review-copy">Start with the illustrated example to understand the workflow, or upload an authorised research image to run real model inference.</p><div class="check-row"><strong>Illustration preview only</strong><span>No classification is performed on the drawing.</span></div><div class="check-row"><strong>Ready for a research image</strong><span>After analysis, this panel shows the model label, class-support score and review notes.</span></div>', unsafe_allow_html=True)
            elif analysis and analysis["signature"] == signature:
                row = analysis["rows"][selected or 0]
                if row["status"] == "complete":
                    st.markdown('<span class="status-label">MODEL OUTPUT AVAILABLE</span>', unsafe_allow_html=True)
                    st.caption(row["file"])
                    st.metric("Research-model class", class_label(row["model_class"]))
                    score = row["model_score_uncalibrated"]
                    st.progress(score, text=f"Class-support score · {score:.1%}")
                    st.caption("An uncalibrated model score—not clinical confidence or a person's probability of anaemia.")
                    st.info("Human review required. This output must not be used to diagnose or rule out anaemia. Appropriate clinical assessment and laboratory testing remain necessary.")
                    st.markdown('<div class="check-row"><strong>What was checked</strong><span>File decoding, format, dimensions and model execution.</span></div><div class="check-row"><strong>What was not established</strong><span>Image suitability, independent clinical accuracy or patient benefit.</span></div>', unsafe_allow_html=True)
                else:
                    st.warning("This image could not be processed. Check its format and size, then try an appropriate research image.")
                report = {"purpose": "Research output only; not a diagnosis or independent clinical validation.", "notes": "Model scores are uncalibrated. The classifier does not verify that an input is a conjunctiva image.", "results": analysis["rows"]}
                st.download_button("Download research output · JSON", json.dumps(report, indent=2), "conjunctiva-research-output.json", "application/json", use_container_width=True)
                if len(analysis["rows"]) > 1:
                    st.caption(f"Batch summary · {sum(row['status'] == 'complete' for row in analysis['rows'])} of {len(analysis['rows'])} images processed. Select an image on the left to review it.")
            else:
                st.markdown('<div class="review-title">Your review starts here.</div><p class="review-copy">Choose a supported research image, then select “Run research analysis.” The output stays linked to that image—changing inputs clears the displayed result.</p><div class="check-row"><strong>Model label</strong><span>The classifier’s selected class, not a clinical diagnosis.</span></div><div class="check-row"><strong>Class-support score</strong><span>A model score displayed with calibration limits.</span></div><div class="check-row"><strong>Review context</strong><span>Clear limits and a downloadable research record.</span></div>', unsafe_allow_html=True)
        st.markdown('<p class="fine-print">Designed for transparent research review. No automatic care decisions, diagnostic claims or treatment recommendations.</p>', unsafe_allow_html=True)

with notes:
    st.subheader("Understand the research before interpreting an output.")
    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True, key="method_implementation"):
            st.caption("IMPLEMENTATION")
            st.write("The existing YOLOv8 classification checkpoint is run on CPU. Image decoding checks JPEG/PNG format and dimensions, corrects orientation, and converts input to RGB.")
            st.write("The model's own class names are used; the interface does not assume their order.")
        with st.container(border=True, key="method_privacy"):
            st.caption("IMAGE HANDLING")
            st.write("Uploaded files are processed in server memory. The application does not save uploaded images to disk or send them to an external AI provider. Hosting infrastructure still receives uploads, so protected health information must not be entered.")
            st.write("A shared demo password is only a casual access gate, not privacy-compliance protection.")
    with right:
        with st.container(border=True, key="method_limits"):
            st.caption("VALIDATION LIMITS")
            st.write("This is not a clinically validated diagnostic tool. Independent patient-level testing, verified labels, external validation and clinical evaluation remain necessary.")
            st.write("Training overlap and patient-level independence of the supplied local images are unknown. Splitting those images now does not prove the existing model never saw them.")
            st.write("Class scores are not calibrated clinical probabilities. A general image classifier does not verify that an image shows conjunctiva or reject every unsuitable input.")
        st.link_button("Read the project case study", "https://solomonodum.com/projects/low-cost-vision-screening", use_container_width=True)

st.caption("Conjunctiva · Built by Solomon Amaning Odum · Research prototype only")
