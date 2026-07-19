# TransitDelay AI 🚇
> A machine learning-powered web application designed to forecast public transport delay probabilities using historical transit logs and simulated environmental contexts.

This repository features an end-to-end Machine Learning pipeline: from raw data cleaning and model training (via Jupyter Notebook) to a production-ready Flask API and a premium glassmorphic web dashboard.

---

## 🚀 Quick Start

### 1. Install Dependencies
Ensure you have Python 3.8+ installed. Install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Run the Application
Start the Flask local development server:
```bash
python app.py
```

### 3. Open the Interface
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🛠️ System Architecture

### 1. Data & Preprocessing
* **Source**: `public_transport_delays.csv` containing historical schedules, actual delays, weather parameters, and traffic indexes.
* **Feature Engineering**: Calculates peak hour schedules (morning/evening rush hour windows), estimated scheduled trip durations, and maps generic categorical dummy columns for 50 stations and 20 routes.

### 2. The Machine Learning Model
* **Model Type**: Random Forest Classifier (saved in `delay_prediction_model.pkl`).
* **Schema**: Evaluates a 157-feature vector containing temporal, operational, and dummy-encoded environmental features.
* **Outputs**: Returns binary classification (`0` for On-Time, `1` for Delayed) along with probability scores.

### 3. Flask Backend API (`app.py`)
* **Metadata Services**: Exposes unique stations and transport configurations dynamically.
* **Prediction Service**: Merges user trip selections with simulated live environmental features, processes dummy encoding internally, and executes predictions in under 5ms.

### 4. Interactive Frontend UI
* **Aesthetics**: Premium, dark-themed glassmorphism interface styled with Vanilla CSS.
* **Micro-Animations**: Features a custom `requestAnimationFrame` circular gauge animation that counts up progress and sweeps the border stroke over 1 second.
* **Realistic Inputs**: Automatically maps generic station IDs (e.g. `Station_31`) to realistic London transit hubs (e.g. `Richmond Station`) on the dropdown selectors.

---

## 📊 Presentation & Project Demo Guide

When presenting this college ML project, here are key points to explain:

### 1. The Contextual Simulation Note
> *"Currently, the contextual features (weather and traffic indexes) are simulated. In a production version, these variables would be automatically fetched using live weather (e.g., OpenWeatherMap) and traffic (e.g., Google Maps) APIs before executing the prediction."*

### 2. Model Performance
* The project compared multiple classifiers (Logistic Regression, Decision Trees, KNN, and SVM) before choosing **Random Forest** due to its high performance and robustness against mixed categorical and numerical schemas.

### 3. Explaining Counter-Intuitive Predictions
* **Why Clear weather might show more delay than Rain**: Machine learning models look at historical correlation. Clear weather correlates with higher passenger volume (dwell time at gates) and higher tourist/commuter traffic, which often causes cascading transit system delays compared to low-volume rainy days.