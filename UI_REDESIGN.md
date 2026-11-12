# Conjunctiva research interface

The interface is redesigned around a clear image-to-review workflow instead of developer counters and automatic inference on every rerun. It uses a light clinical-research workspace, dark navigation, concise notices and distinct input/review panels.

## Behaviour

- The access form disappears after successful login. “Lock demo” returns to the gate; the password is still supplied through Railway variables, never hardcoded in UI source.
- A generated eye illustration lets visitors explore the interface without patient data. It is explicitly labelled and never submitted to the classifier. The walkthrough does not fabricate diagnoses, scores or clinical accuracy.
- Research uploads require acknowledgement of authorised, de-identified use. Images are previewed before the user selects “Run research analysis.” Single-image and up-to-five-image batch modes are supported.
- Results show the checkpoint's selected class and an uncalibrated class-support score, not clinical confidence. Results remain tied to an input fingerprint, so changed inputs do not display a previous image's result.
- A research-output JSON can be downloaded. The app does not write uploaded images to disk or send them to an external AI API.
- “Start again” clears the result and uploader. Implementation, privacy and validation limitations are in a separate tab rather than dominating the main workspace.

The model, trained weights and clinical-validation status are unchanged. Independent testing and clinical evaluation remain necessary; the UI is not a diagnostic device or privacy-compliance guarantee.

## Deployment and verification

`presentation.py` contains styles and generated assets and is included in the app-only Docker/upload allowlists. No dataset image is included. Use `python prepare_railway_payload.py` and deploy the resulting minimal payload, not the entire repository.

Run `python -m pytest test_inference.py test_deployment.py test_evaluate_local.py test_presentation.py -q`. Browser checks cover the login form disappearing, the illustration-only flow, synthetic PNG upload/inference, JSON output, reset and mobile layout. Screenshots use only the generated illustration or synthetic execution-test image and remain in ignored `.local-deploy/` until deliberately chosen for portfolio publication.

The working Railway address remains `https://anemia-research-demo-production.up.railway.app`. The requested custom domain `anemia.solomonodum.com` is registered on Railway, but its DNS ownership records must be added by an authorised DNS editor before changing public links. The Vercel CLI DNS request was refused and is not bypassed by this UI update.
