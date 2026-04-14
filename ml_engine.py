"""
Smart Weather Prediction Engine (SWIE Module 1)
ML-based weather classification: Rainy, Sunny, Cloudy, Storm.
Models: Decision Tree, SVM, Random Forest, XGBoost.
"""

import os
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_predict, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib

# XGBoost optional
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

LABELS = ["Sunny", "Cloudy", "Rainy", "Storm"]
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def _generate_training_data(n_samples=5000):
    """Generate synthetic training data aligned with weather logic."""
    np.random.seed(42)
    data = []
    for _ in range(n_samples):
        temp = np.random.uniform(-5, 45)
        rainfall = np.random.uniform(0, 80)
        wind = np.random.uniform(0, 120)
        humidity = np.random.uniform(10, 100)
        pressure = np.random.uniform(980, 1040)
        # Simple rule-based labels for training
        if rainfall > 15 or humidity > 85:
            if wind > 60 or (rainfall > 30 and wind > 40):
                label = 3  # Storm
            else:
                label = 2  # Rainy
        elif rainfall > 2 or (humidity > 75 and np.random.random() > 0.5):
            label = 1  # Cloudy
        else:
            label = 0  # Sunny
        data.append([temp, rainfall, wind, humidity, pressure, label])
    df = pd.DataFrame(data, columns=["temp", "rainfall", "wind", "humidity", "pressure", "label"])
    return df


def _get_features_from_weather(current: dict, daily_today: dict) -> np.ndarray:
    """Extract feature vector from API current + daily data."""
    temp = current.get("temperature_2m") or (daily_today.get("temperature_2m_max", 0) + daily_today.get("temperature_2m_min", 0)) / 2
    rainfall = current.get("precipitation") or daily_today.get("precipitation_sum") or 0
    wind = current.get("wind_speed_10m") or 0
    humidity = current.get("relative_humidity_2m") or 50
    pressure = current.get("pressure_msl") or 1013
    return np.array([[temp, rainfall, wind, humidity, pressure]])


class SmartWeatherPredictionEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.models = {}
        self.model_metrics = {}
        self.feature_names = ["temp", "rainfall", "wind", "humidity", "pressure"]
        self._trained = False

    def _train_models(self):
        df = _generate_training_data(6000)
        X = df[self.feature_names].values
        y = df["label"].values
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        models = {
            "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
            "SVM": SVC(kernel="rbf", probability=True, random_state=42),
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        }
        if HAS_XGB:
            models["XGBoost"] = xgb.XGBClassifier(n_estimators=100, max_depth=6, random_state=42, use_label_encoder=False, eval_metric="logloss")

        for name, clf in models.items():
            clf.fit(X_scaled, y)
            self.models[name] = clf

        # Cross-validation metrics for model comparison
        for name, clf in self.models.items():
            scores = cross_validate(clf, X_scaled, y, cv=5, scoring=["accuracy", "precision_macro", "recall_macro", "f1_macro"])
            self.model_metrics[name] = {
                "accuracy": float(np.mean(scores["test_accuracy"]) * 100),
                "precision": float(np.mean(scores["test_precision_macro"]) * 100),
                "recall": float(np.mean(scores["test_recall_macro"]) * 100),
                "f1_score": float(np.mean(scores["test_f1_macro"]) * 100),
            }
        self._trained = True
        return self

    def ensure_trained(self):
        if not self._trained:
            self._train_models()
        return self

    def predict(self, temp: float, rainfall: float, wind: float, humidity: float, pressure: float):
        """Predict weather class and probability. Returns label name, probability, all probs."""
        self.ensure_trained()
        X = np.array([[temp, rainfall, wind, humidity, pressure]])
        X_scaled = self.scaler.transform(X)
        # Use Random Forest for main prediction (best balance)
        clf = self.models["Random Forest"]
        pred = clf.predict(X_scaled)[0]
        proba = clf.predict_proba(X_scaled)[0]
        return {
            "prediction": LABELS[pred],
            "probability": float(proba[pred]),
            "probabilities": {LABELS[i]: float(proba[i]) for i in range(len(LABELS))},
        }

    def get_feature_importance(self):
        """Explainable AI: feature importance from Random Forest."""
        self.ensure_trained()
        rf = self.models["Random Forest"]
        imp = rf.feature_importances_
        return {name: float(imp[i]) for i, name in enumerate(self.feature_names)}

    def get_model_comparison(self):
        """Return accuracy/precision/recall/F1 for each model (for dashboard)."""
        self.ensure_trained()
        return self.model_metrics

    def predict_from_api_data(self, current: dict, daily_today: dict):
        """Convenience: predict from Open-Meteo style current + daily."""
        temp = current.get("temperature_2m", 20)
        rainfall = current.get("precipitation") or daily_today.get("precipitation_sum") or 0
        wind = current.get("wind_speed_10m", 0)
        humidity = current.get("relative_humidity_2m", 50)
        pressure = current.get("pressure_msl", 1013)
        return self.predict(temp, rainfall, wind, humidity, pressure)


# Singleton for app use
_engine = None


def get_ml_engine():
    global _engine
    if _engine is None:
        _engine = SmartWeatherPredictionEngine()
        _engine.ensure_trained()
    return _engine
