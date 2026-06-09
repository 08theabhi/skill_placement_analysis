"""
Prediction Pipeline — XGBoost + LightGBM Ensemble + SHAP Explainability
Implements Agent 4: Placement Prediction Agent ML backbone
Models: XGBoost, LightGBM, KMeans (salary clustering), Prophet (time forecasting)
"""
import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

class PlacementPredictor:
    def __init__(self):
        self.xgb_model = None
        self.lgb_model = None
        self.shap_explainer = None
        self.is_trained = False
        self.model_path = os.getenv("MODEL_STORE_PATH", "./ml_models")
        os.makedirs(self.model_path, exist_ok=True)
        self._try_load()

    def _extract_features(self, students: List[Dict]) -> pd.DataFrame:
        HIGH_VALUE = {"GenAI","Machine Learning","Cloud Computing","DevOps","Python","AWS","Deep Learning","Kubernetes"}
        DEPT_MAP = {"CSE":0,"IT":1,"ECE":2,"EEE":3,"Mechanical":4,"Civil":5}
        rows = []
        for s in students:
            skills = s.get("skills",[])
            rows.append({
                "cgpa": s.get("cgpa",0),
                "backlogs": s.get("backlogs",0),
                "internships": s.get("internships",0),
                "projects": s.get("projects",0),
                "certifications": s.get("certifications",0),
                "avg_mock": s.get("avg_mock_score",0),
                "skill_count": len(skills),
                "batch": s.get("batch",2022),
                "communication": s.get("communication_score",7),
                "aptitude": s.get("aptitude_score",7),
                "attendance": s.get("attendance",75),
                "lms_activity": s.get("lms_activity",70),
                "has_python": int("Python" in skills),
                "has_ml": int("Machine Learning" in skills),
                "has_cloud": int("Cloud Computing" in skills),
                "has_genai": int("GenAI" in skills),
                "has_devops": int("DevOps" in skills),
                "has_sql": int("SQL" in skills),
                "high_value_skills": sum(1 for sk in skills if sk in HIGH_VALUE),
                "dept_encoded": DEPT_MAP.get(s.get("department","CSE"),0),
            })
        return pd.DataFrame(rows)

    def train(self, students: List[Dict]) -> Dict:
        import xgboost as xgb
        import lightgbm as lgb
        import shap
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import roc_auc_score

        labeled = [s for s in students if "placed" in s]
        if len(labeled) < 10:
            return {"status": "error", "message": "Need at least 10 labeled students"}

        X = self._extract_features(labeled)
        y = np.array([1 if s.get("placed") else 0 for s in labeled])

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        self.xgb_model = xgb.XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.1,
            use_label_encoder=False, eval_metric="logloss", random_state=42)
        self.xgb_model.fit(X_train, y_train)

        self.lgb_model = lgb.LGBMClassifier(n_estimators=200, max_depth=5, learning_rate=0.1,
            random_state=42, verbose=-1)
        self.lgb_model.fit(X_train, y_train)

        self.shap_explainer = shap.TreeExplainer(self.xgb_model)
        self.feature_names = X.columns.tolist()
        self.is_trained = True

        xgb_auc = roc_auc_score(y_test, self.xgb_model.predict_proba(X_test)[:,1])
        lgb_auc = roc_auc_score(y_test, self.lgb_model.predict_proba(X_test)[:,1])

        self._save()
        return {
            "status": "success",
            "students_trained": len(labeled),
            "xgb_auc": round(xgb_auc, 4),
            "lgb_auc": round(lgb_auc, 4),
            "ensemble_auc": round((xgb_auc + lgb_auc) / 2, 4)
        }

    def predict(self, student: Dict) -> Dict:
        if not self.is_trained:
            return {"error": "Models not trained. Please train first."}
        X = self._extract_features([student])
        xgb_prob = self.xgb_model.predict_proba(X)[0][1]
        lgb_prob = self.lgb_model.predict_proba(X)[0][1]
        ensemble_prob = round((xgb_prob + lgb_prob) / 2 * 100, 1)

        shap_vals = self.shap_explainer.shap_values(X)[0]
        shap_dict = {feat: round(float(val)*100, 2) for feat, val in zip(self.feature_names, shap_vals)}
        top_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:6]

        label = "Likely Placed" if ensemble_prob >= 65 else "Borderline" if ensemble_prob >= 45 else "At Risk"
        predicted_salary = round(300000 + (ensemble_prob/100) * 900000)

        return {
            "placement_probability": ensemble_prob,
            "xgb_probability": round(xgb_prob*100, 1),
            "lgb_probability": round(lgb_prob*100, 1),
            "prediction_label": label,
            "predicted_salary": predicted_salary,
            "shap_top_factors": [{"feature": k, "impact": v} for k, v in top_factors],
        }

    def _save(self):
        try:
            with open(f"{self.model_path}/model.pkl", "wb") as f:
                pickle.dump({"xgb": self.xgb_model, "lgb": self.lgb_model,
                             "explainer": self.shap_explainer, "features": self.feature_names}, f)
        except Exception:
            pass

    def _try_load(self):
        try:
            path = f"{self.model_path}/model.pkl"
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = pickle.load(f)
                self.xgb_model = data["xgb"]
                self.lgb_model = data["lgb"]
                self.shap_explainer = data["explainer"]
                self.feature_names = data["features"]
                self.is_trained = True
        except Exception:
            pass

class SalaryClusterer:
    def cluster(self, students: List[Dict]) -> Dict:
        from sklearn.cluster import KMeans
        import numpy as np
        if not students:
            return {"clusters": []}
        X = np.array([[len(s.get("skills",[])), s.get("cgpa",0),
                       s.get("internships",0), s.get("avg_mock_score",0)] for s in students])
        k = min(5, len(students))
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        clusters = []
        for i in range(k):
            idx = np.where(labels == i)[0]
            cluster_students = [students[j] for j in idx]
            skills_all = []
            for s in cluster_students:
                skills_all.extend(s.get("skills",[]))
            from collections import Counter
            top_skills = [sk for sk,_ in Counter(skills_all).most_common(3)]
            clusters.append({
                "cluster_id": i+1,
                "size": len(idx),
                "avg_skills": round(np.mean([len(students[j].get("skills",[])) for j in idx]),1),
                "avg_cgpa": round(np.mean([students[j].get("cgpa",0) for j in idx]),2),
                "top_skills": top_skills,
                "label": f"Cluster {i+1}"
            })
        return {"clusters": clusters, "total_students": len(students)}

class PlacementTrendForecaster:
    def forecast(self, records: List[Dict], periods: int = 6) -> Dict:
        if not PROPHET_AVAILABLE:
            return {"status": "prophet_not_installed", "message": "Install prophet for forecasting"}
        try:
            if len(records) < 3:
                return {"status": "insufficient_data"}
            df = pd.DataFrame(records)
            df["ds"] = pd.to_datetime(df["placement_date"])
            df["y"] = 1
            monthly = df.set_index("ds").resample("M")["y"].count().reset_index()
            monthly.columns = ["ds", "y"]
            if len(monthly) < 3:
                return {"status": "insufficient_data"}
            model = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
            model.fit(monthly)
            future = model.make_future_dataframe(periods=periods, freq="M")
            forecast = model.predict(future)
            return {
                "status": "success",
                "trend": "increasing" if forecast["trend"].iloc[-1] > forecast["trend"].iloc[0] else "decreasing",
                "forecast": [{"month": row["ds"].strftime("%Y-%m"),
                               "predicted": max(0, round(row["yhat"])),
                               "lower": max(0, round(row["yhat_lower"])),
                               "upper": max(0, round(row["yhat_upper"]))}
                              for _, row in forecast.tail(periods).iterrows()]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

_predictor = None
_clusterer = None
_forecaster = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = PlacementPredictor()
    return _predictor

def get_clusterer():
    global _clusterer
    if _clusterer is None:
        _clusterer = SalaryClusterer()
    return _clusterer

def get_forecaster():
    global _forecaster
    if _forecaster is None:
        _forecaster = PlacementTrendForecaster()
    return _forecaster
