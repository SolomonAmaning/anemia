# Railway research-demo deployment

Railway can host this Streamlit application as a CPU service. No database, GPU or persistent patient-image storage is needed. This deployment is a research demo, not a validated diagnostic service.

## What is prepared

- Python 3.12 Dockerfile with CPU-only Torch wheels and a non-root runtime.
- An explicit application-file allowlist in both Docker COPY statements and `.dockerignore`. No medical dataset, training images, local environment or training logs enter the build context.
- `serve.py` honours Railway's `PORT` and binds to `0.0.0.0`.
- The existing public model is downloaded at startup and verified against its exact size and SHA-256 before loading. A synthetic-image inference check must pass before Streamlit starts.
- Upload limits, disabled telemetry and optional password-gated staging through `ANEMIA_DEMO_PASSWORD`.

## Railway setup

1. Use a dedicated service in the explicitly authorised Railway project. Prepare a minimal upload with `python prepare_railway_payload.py`. Deploy **that payload directory only** using Railway CLI with `--path-as-root`, explicit project/service/environment flags and `--ci`. Do not upload this entire repository: it contains historical training images, and `.dockerignore` alone does not establish what the CLI archive sends to Railway. Confirm account charges before creating/deploying a service.
2. Let Railway detect the root Dockerfile. Do not override its start command; it uses `python serve.py`.
3. Set healthcheck path to `/_stcore/health` and timeout to 300 seconds. The preflight catches broken model provisioning before the server can report healthy. Railway healthchecks are deployment checks, not continuous monitoring.
4. Set `ANEMIA_DEMO_PASSWORD` securely for private staging. Docker defaults to `ANEMIA_REQUIRE_PASSWORD=true` and refuses to start without a configured password. Never commit the password. Leave `ANEMIA_MODEL_PATH` unset to use the checksum-verified public checkpoint. Disabling the staging requirement is a separate public-release decision.
5. Generate a Railway public domain after reviewing the build and startup logs. Test the UI and an authorised synthetic image through the deployed domain. Do not use clinical patient images for a public deployment test.

Railway's November 2026 documentation deprecates new `railway.toml` / `railway.json` Config as Code services. Use dashboard settings or Railway's current Infrastructure as Code rather than adding deprecated configuration.

## Local checks

Install `requirements.txt` and pytest, then run `python -m pytest test_inference.py test_deployment.py -q`. Set `ANEMIA_MODEL_PATH` to the verified repository model to test `PORT=8506 python serve.py` without a download. To test Docker once Docker Desktop is running: `docker build -t anemia-research .`, then `docker run --rm -e PORT=8080 -p 8080:8080 anemia-research`.

## Current limits

The original OneDrive training paths remain blocked by macOS permissions. The user subsequently supplied accessible `Downloads/anemic` and `Downloads/non-anemic` folders and confirmed authorised, de-identified research use. These images are inspected and evaluated locally only; none is uploaded, retrained on or published. Previous inclusion in training is unknown. No patient-group mapping or verified haemoglobin labels were supplied, so these cannot be called an independent or clinical test set.

The user authorised the existing `positive-luck` project. A separate `anemia-research-demo` service was created in its production-named environment; this is still a private **research staging demo**, not a production clinical service. `PORT=8080`, a generated password and the required-password flag are configured through Railway variables. The generated domain is `https://anemia-research-demo-production.up.railway.app`. Creation of a domain alone does not establish a successful deployment; check hosted health and password-gated synthetic inference before declaring it live.

Deployment `b2ddb050-24b2-404d-be19-9a162f69f1a4` succeeded on November 12, 2026 using the runtime code from commit `4628623`. The Linux CPU Docker image built successfully; startup verified the checkpoint and synthetic inference before serving. The hosted health endpoint returned `ok`. Browser checks verified wrong-password denial, password-gated model loading, consent acknowledgement, and synthetic PNG upload/inference. Only an artificial pink image named `synthetic-execution-test.png` was uploaded. No dataset image was sent. Container inspection confirmed application files plus the downloaded model only; the main Python process used approximately 389 MB RSS after this smoke test, not a measured production capacity bound.

The access password is available in the service's Railway Variables as `ANEMIA_DEMO_PASSWORD`. A local owner-readable copy is kept in ignored `.local-deploy/access-password`; do not commit or publish it. The private screenshot is in `.local-deploy/live-demo-synthetic.png`. The service was deployed via a minimal CLI upload and is not automatically connected to GitHub; future deploys must use the prepared application-only payload. The source changes remain in a draft PR, with no main-branch merge.

Railway's public API returned HTTP 403 for the attempted health-check configuration update. That update was not applied or retried through another route. Configure `/_stcore/health` in the service dashboard if required; the application's model-verification preflight still runs before Streamlit starts. Dependency vulnerability review, upload abuse protection and any public launch remain separate release gates. The password is a staging gate, not enterprise authentication or a claim of privacy compliance. No patient-image storage, database or GPU is provisioned.

## Local dataset consistency check

Run `python evaluate_local.py --anemic-dir /path/to/anemic --non-anemic-dir /path/to/non-anemic`. Reports are written to ignored `.local-evaluation/` and contain hashed image identifiers rather than filenames. Keep reports private. The script checks image decoding, pixel-identical duplicate copies and cross-label conflicts, deduplicates before scoring, and uses the checkpoint's own class mapping with anaemic as the positive class.

The November 12 local audit found 338 images (116 anaemic, 222 non-anaemic), 281 unique pixel images (90/191), 57 duplicate copies, no undecodable files and no pixel-identical cross-label conflicts. The existing checkpoint missed 21 of the 90 anaemic-labelled unique images at the default 0.5 threshold. This is a consistency check with unknown training overlap, not clinical validation; do not use these figures as proven performance in the public UI or résumé.

A fixed-seed, stratified image-level subset is reserved in `provisional-split.json` for future comparisons. This does not retroactively remove these images from the existing model's training. Related images from the same person may still span development and test subsets without a patient-group mapping. No threshold tuning or retraining is performed.
