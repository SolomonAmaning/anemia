# Anemia Detection App

## Overview
Welcome to the **Anemia Detection App**, an AI-powered tool designed to assist in the detection of anemia from conjunctiva images. This project leverages a **YOLOv8 model** trained on conjunctiva images to classify whether an individual is **anemic** or **non-anemic**. 

This app was developed using **Streamlit** for an interactive user experience and is powered by a custom deep learning model.

---

## Features
- **Upload single or multiple images** for prediction.
- **Batch processing** of multiple conjunctiva images.
- Display of **predicted class** (`anemic` or `non_anemic`) with confidence scores.
- User-friendly interface with clear instructions and feedback.

---

## How It Works
1. **Model**: A custom YOLOv8 model trained on conjunctiva images.
2. **Inference**: The uploaded image(s) are analyzed by the model to determine if the conjunctiva indicates anemia.
3. **Results**: The app displays:
   - The uploaded image.
   - The predicted class (`anemic` or `non_anemic`).
   - Confidence score for the prediction.

---

## Instructions
1. **Upload Images**:
   - Use the "Upload Image(s) of the Conjunctiva" uploader.
   - Upload images in JPG, PNG, or JPEG formats.
   - For batch processing, you can upload multiple images simultaneously.
2. **View Results**:
   - Each uploaded image will be displayed alongside its predicted classification and confidence score.
   - Errors will be displayed if the uploaded file is invalid or cannot be processed.
3. **Feedback**:
   - The app provides user-friendly error messages for invalid inputs.

---

## Prerequisites
### Tools and Libraries
Ensure you have the following installed:
- **Python 3.8+**
- **Streamlit**
- **YOLOv8**
- **OpenCV**
- **Pillow**
- **NumPy**

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/anemia-detection-app.git
   cd anemia-detection-app
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place the trained YOLOv8 model in the appropriate directory:
   ```bash
   /path/to/your/model/best.pt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

---

## File Structure
```
anemia/
├── amemia_prediction.py                   
├── requirements.txt         
├── README.md               
├── /runs/classify/train8/   
└── /sample_images/          
```

---

## Example Workflow
1. Launch the application:
   ```bash
   streamlit run anemia_prediction.py
   ```
2. Upload conjunctiva images.
3. View predictions along with confidence scores.
4. Repeat for batch image processing.

---

## Troubleshooting
### Common Issues
1. **Invalid Image Format**:
   - Ensure the uploaded files are in JPG, PNG, or JPEG format.
2. **Model File Missing**:
   - Verify the YOLOv8 model (`best.pt`) exists at the specified path.
3. **Dependencies Missing**:
   - Run `pip install -r requirements.txt` to install all dependencies.

---

## Credits
- **Developed by**: Solomon Odum
- **Built with**:
  - [Streamlit](https://streamlit.io/)
  - [YOLOv8](https://github.com/ultralytics/yolov8)
  - [OpenCV](https://opencv.org/)

---

## Future Enhancements
- Add **real-time webcam support** for live conjunctiva detection.
- Incorporate **additional health parameters** for a more comprehensive diagnostic tool.

---

## License
This project is licensed under the MIT License. 
