# TransitDelay AI 🚇
> A machine learning-powered web application designed to forecast public transport delay probabilities using historical transit logs and simulated environmental contexts.

## 📋 About the Project
TransitDelay AI is an intelligent predictive tool designed to address uncertainty in urban travel. By leveraging historical travel logs, scheduling metadata, and environmental conditions, the system forecasts whether a particular journey will run on schedule or encounter delays.

Using a pre-trained **Random Forest Classifier**, the system models complex relations between transit modes (Bus, Metro, Train, Tram), temporal factors (peak hours, weekdays, seasons), and environmental contexts (temperature, precipitation, and traffic load). A dynamic, glassmorphic dashboard provides an intuitive interface for commuters to plan their journeys with real-time confidence scores.

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