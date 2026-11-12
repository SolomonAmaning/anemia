# Anaemia research demo

The app now loads its checkpoint relative to the repository rather than an absolute Mac path. Run `git lfs pull` to retrieve `runs/classify/train8/weights/best.pt`, or set `ANEMIA_MODEL_PATH` to a trusted local checkpoint. Never load weights from an untrusted source.

Use Python 3.12, install `requirements.txt`, and run `streamlit run anemia_prediction.py`. Install pytest and run `python -m pytest test_inference.py -q` for the six checks covering missing weights, LFS pointers, label order, upload validation, real checkpoint execution and UI loading. The verified environment used Torch 2.5.1, Torchvision 0.20.1, Ultralytics 8.3.162 and Streamlit 1.40.0. Earlier installed Ultralytics 8.0.200 could load this checkpoint but failed at prediction because of incompatible transforms.

The synthetic blank-image test establishes code execution only. It does not establish clinical performance. Uploaded images require a research-consent acknowledgement; the server limits uploads to 10 MB and the decoder to 20 megapixels. Outputs use checkpoint class names rather than assuming their order. Scores are not calibrated clinical confidence.

The portfolio screenshot shows the actual loaded model and workspace with no patient image. No breast-thermography implementation is included here. Before any clinical use, the project needs clinical governance, authorised datasets, external validation and an assessment of inappropriate-image rejection.
