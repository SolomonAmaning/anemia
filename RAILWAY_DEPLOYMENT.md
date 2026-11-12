# Railway research-demo deployment

Railway can host this Streamlit application as a CPU service. No database, GPU or persistent patient-image storage is needed. This deployment is a research demo, not a validated diagnostic service.

## What is prepared

- Python 3.12 Dockerfile with CPU-only Torch wheels and a non-root runtime.
- An explicit application-file allowlist in both Docker COPY statements and `.dockerignore`. No medical dataset, training images, local environment or training logs enter the build context.
- `serve.py` honours Railway's `PORT` and binds to `0.0.0.0`.
- The existing public model is downloaded at startup and verified against its exact size and SHA-256 before loading. A synthetic-image inference check must pass before Streamlit starts.
- Upload limits, disabled telemetry and optional password-gated staging through `ANEMIA_DEMO_PASSWORD`.

## Railway setup

1. Create a dedicated service from the `SolomonAmaning/anemia` GitHub repository and select the reviewed deployment branch. Confirm any account charges before creating/deploying it.
2. Let Railway detect the root Dockerfile. Do not override its start command; it uses `python serve.py`.
3. Set healthcheck path to `/_stcore/health` and timeout to 300 seconds. The preflight catches broken model provisioning before the server can report healthy. Railway healthchecks are deployment checks, not continuous monitoring.
4. Set `ANEMIA_DEMO_PASSWORD` securely for private staging. Docker defaults to `ANEMIA_REQUIRE_PASSWORD=true` and refuses to start without a configured password. Never commit the password. Leave `ANEMIA_MODEL_PATH` unset to use the checksum-verified public checkpoint. Disabling the staging requirement is a separate public-release decision.
5. Generate a Railway public domain after reviewing the build and startup logs. Test the UI and an authorised synthetic image through the deployed domain. Do not use clinical patient images for a public deployment test.

Railway's November 2026 documentation deprecates new `railway.toml` / `railway.json` Config as Code services. Use dashboard settings or Railway's current Infrastructure as Code rather than adding deprecated configuration.

## Local checks

Install `requirements.txt` and pytest, then run `python -m pytest test_inference.py test_deployment.py -q`. Set `ANEMIA_MODEL_PATH` to the verified repository model to test `PORT=8506 python serve.py` without a download. To test Docker once Docker Desktop is running: `docker build -t anemia-research .`, then `docker run --rm -e PORT=8080 -p 8080:8080 anemia-research`.

## Current limits

The original OneDrive training paths remain blocked by macOS permissions. The user subsequently supplied accessible `Downloads/anemic` and `Downloads/non-anemic` folders and confirmed authorised, de-identified research use. These images are inspected and evaluated locally only; none is uploaded, retrained on or published. Previous inclusion in training is unknown. No patient-group mapping or verified haemoglobin labels were supplied, so these cannot be called an independent or clinical test set.

No Railway service has been created by these code changes. The portfolio is configured on Vercel; no Railway project named portfolio was found. A separate Railway service/project must be explicitly selected and authorised. Docker image execution and Linux memory usage still need verification because Docker Desktop is not running. Dependency vulnerability review, upload abuse protection and any public launch remain separate release gates. The optional password is a staging gate, not enterprise authentication or a claim of privacy compliance.

## Local dataset consistency check

Run `python evaluate_local.py --anemic-dir /path/to/anemic --non-anemic-dir /path/to/non-anemic`. Reports are written to ignored `.local-evaluation/` and contain hashed image identifiers rather than filenames. Keep reports private. The script checks image decoding, pixel-identical duplicate copies and cross-label conflicts, deduplicates before scoring, and uses the checkpoint's own class mapping with anaemic as the positive class.

The November 12 local audit found 338 images (116 anaemic, 222 non-anaemic), 281 unique pixel images (90/191), 57 duplicate copies, no undecodable files and no pixel-identical cross-label conflicts. The existing checkpoint missed 21 of the 90 anaemic-labelled unique images at the default 0.5 threshold. This is a consistency check with unknown training overlap, not clinical validation; do not use these figures as proven performance in the public UI or résumé.

A fixed-seed, stratified image-level subset is reserved in `provisional-split.json` for future comparisons. This does not retroactively remove these images from the existing model's training. Related images from the same person may still span development and test subsets without a patient-group mapping. No threshold tuning or retraining is performed.
