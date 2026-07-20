import os
import joblib
import math
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.features.feature_engineering import FeatureEngineer

app = Flask(__name__)
CORS(app)

MODEL_PATH = "models/xgboost_model.pkl"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

# We need a fitted scaler. Since we don't have the original fitted scaler saved, 
# wait, did we save the scaler object?
# Let's try to load scaler if it exists, otherwise we'll have an issue.
import json

SCALER_PATH = "models/scaler.json"
if os.path.exists(SCALER_PATH):
    with open(SCALER_PATH, 'r') as f:
        scaler_data = json.load(f)
else:
    scaler_data = None

def compute_analytical_ik(x, y, L1, L2):
    solutions = []
    D_squared = x**2 + y**2
    if D_squared > (L1 + L2)**2 or D_squared < (L1 - L2)**2:
        return []
        
    cos_q2 = (D_squared - L1**2 - L2**2) / (2 * L1 * L2)
    cos_q2 = max(-1.0, min(1.0, cos_q2))
    q2_1 = math.acos(cos_q2)
    q2_2 = -q2_1
    
    for q2 in [q2_1, q2_2]:
        sin_q2 = math.sin(q2)
        k1 = L1 + L2 * cos_q2
        k2 = L2 * sin_q2
        q1 = math.atan2(y, x) - math.atan2(k2, k1)
        q1 = (q1 + math.pi) % (2 * math.pi) - math.pi
        solutions.append({"theta1": q1, "theta2": q2})
        
    return solutions

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    try:
        x = float(data.get("x", 0))
        y = float(data.get("y", 0))
        L1 = float(data.get("l1", 0))
        L2 = float(data.get("l2", 0))
    except Exception:
        return jsonify({"error": "Invalid input parameters"}), 400
        
    response = {}
    
    analytical = compute_analytical_ik(x, y, L1, L2)
    
    # ML Model
    if model and scaler_data:
        df = pd.DataFrame([{'x': x, 'y': y, 'l1': L1, 'l2': L2, 'q1': 0.0, 'q2': 0.0}])
        engineer = FeatureEngineer()
        df_eng = engineer.transform(df)
        
        # Transform features
        feat_cols = scaler_data['features']['cols']
        feat_mean = np.array(scaler_data['features']['mean'])
        feat_scale = np.array(scaler_data['features']['scale'])
        X_scaled = (df_eng[feat_cols] - feat_mean) / feat_scale
        
        pred_scaled = model.predict(X_scaled)[0]
        
        # Inverse transform targets
        targ_mean = np.array(scaler_data['targets']['mean'])
        targ_scale = np.array(scaler_data['targets']['scale'])
        pred_unscaled_arr = pred_scaled * targ_scale + targ_mean
        
        pred_unscaled = {'q1': pred_unscaled_arr[0], 'q2': pred_unscaled_arr[1]}
        
        ml_th1 = float(pred_unscaled['q1'])
        ml_th2 = float(pred_unscaled['q2'])
        
        err_th1 = None
        err_th2 = None
        ana_th1 = None
        ana_th2 = None
        
        if analytical:
            # Find the analytical solution closest to the ML prediction
            best_sol = min(analytical, key=lambda sol: (sol['theta1'] - ml_th1)**2 + (sol['theta2'] - ml_th2)**2)
            
            # Compute percentage error (using absolute difference / pi * 100 as a stable metric, 
            # or relative to the true value if true value is non-zero)
            # Let's use relative error: |(pred - true) / true| * 100. If true is 0, use absolute error.
            def calc_err(pred, true_val):
                if abs(true_val) < 1e-5:
                    return abs(pred) * 100 # Just absolute scaled by 100
                return abs((pred - true_val) / true_val) * 100
                
            err_th1 = calc_err(ml_th1, best_sol['theta1'])
            err_th2 = calc_err(ml_th2, best_sol['theta2'])
            ana_th1 = best_sol['theta1']
            ana_th2 = best_sol['theta2']
        
        response["solution"] = {
            "theta1": ml_th1,
            "theta2": ml_th2,
            "analytical_theta1": ana_th1,
            "analytical_theta2": ana_th2,
            "error_theta1": err_th1,
            "error_theta2": err_th2
        }
    else:
        response["error"] = "ML Model not loaded."
        
    if not analytical:
        response["warning"] = "Target is unreachable analytically."
        
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
