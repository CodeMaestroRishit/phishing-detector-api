# 🛡️ Dual AI Phishing Detector

A Dual-AI system combining email and URL machine-learning models for real-time phishing detection.

## Overview

This project implements a **production-grade phishing detection system** combining machine learning models for **email** and **URL** phishing detection. It provides a FastAPI backend serving predictions, a Streamlit dashboard for monitoring and testing, and a Chrome extension for real-time phishing alerts.

## ✨ Features

- **Dual Detection Models**: Separate high-accuracy models for email text and URLs
- **Large-scale Training**: Trained on 400,000+ real-world samples from 9 datasets
- **State-of-the-art Accuracy**: 99.35% for email phishing, 100% for URLs
- **Interactive Dashboard**: Streamlit app showcasing performance metrics
- **REST API**: Powered by FastAPI for easy integration
- **Chrome Extension**: Browser integration for instant phishing alerts
- **Lightweight & Scalable**: Ready for cloud deployment

## 📁 Project Structure

```
.
├── api.py                      # FastAPI backend server
├── streamlit_app.py            # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── chrome_extensions/          # Chrome extension files
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── content.js
└── trained_models/             # ML model files (not in repo)
    ├── email_model.pkl
    ├── email_vectorizer.pkl
    └── url_model.pkl
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for extension)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dual-ai-phishing-detector.git
   cd dual-ai-phishing-detector
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download trained models**
   
   The trained model files are not included in the repository due to size. You have two options:
   
   **Option A**: Train the models yourself (see Training section below)
   
   **Option B**: Download pre-trained models from a cloud storage and place them in the `trained_models/` directory:
   - `email_model.pkl`
   - `email_vectorizer.pkl`
   - `url_model.pkl`

### Running the Application

1. **Start the FastAPI backend**
   ```bash
   uvicorn api:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`

2. **Run the Streamlit dashboard** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```
   The dashboard will open at `http://localhost:8501`

3. **Install Chrome extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `chrome_extensions` folder from this project
   - The extension is now active!

## 📡 API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /` - Health check and model status
- `POST /predict/url` - Analyze a URL for phishing
- `POST /predict/email` - Analyze email text for phishing
- `POST /predict/dual` - Combined analysis of text with URLs
- `POST /predict` - Compatibility endpoint for Chrome extension

### Example API Usage

```python
import requests

# Check API status
response = requests.get("http://127.0.0.1:8000/")
print(response.json())

# Analyze an email
email_data = {
    "text": "URGENT: Click here to verify your account..."
}
response = requests.post("http://127.0.0.1:8000/predict/email", json=email_data)
print(response.json())
```

## 🎯 Usage Examples

### Chrome Extension

1. Navigate to any webpage with text
2. Select suspicious text on the page
3. A tooltip will automatically appear showing the phishing analysis
4. Click the extension icon for manual analysis

### Streamlit Dashboard

1. Start the Streamlit app (see installation steps above)
2. Navigate to the "Live Testing" tab
3. Paste email text or URLs in the input fields
4. Click "Analyze" to see predictions with confidence scores

## 🧪 Training the Models

### Email Model

To train the email phishing detection model:

1. Prepare your email dataset (CSV format with text and labels)
2. Run the training script to generate models

### URL Model

The URL model requires a phishing dataset. The API will automatically train the URL model on startup if:
- A dataset file (`phishing_clean.csv`, `phishing_dataset.csv`, or `phishing.csv`) is present in the project root
- The dataset contains URL features and a class/label column

## 🛠️ Technology Stack

- **Backend**: FastAPI, uvicorn
- **Machine Learning**: scikit-learn (Random Forest)
- **Dashboard**: Streamlit, Plotly
- **Extension**: Chrome Extension Manifest V3
- **Data Processing**: pandas, numpy

## 📊 Model Performance

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Email Detection | 99.35% | 99% | 99% | 99% |
| URL Detection | 100% | 100% | 100% | 100% |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Rishit Guha**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Portfolio: [Your Portfolio](https://yourportfolio.com)

## 🙏 Acknowledgments

- Dataset contributors and researchers in phishing detection
- FastAPI and Streamlit communities
- Open-source ML libraries (scikit-learn)

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

⭐ If you find this project helpful, please give it a star!
