import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

def build_demo_model():
    """Train a tiny synthetic model only so the Streamlit MVP behaves like a real pipeline."""
    rng = np.random.default_rng(7)
    n = 700

    X = np.column_stack([
        rng.normal(22.0, 1.0, n),       # SST
        rng.uniform(0.5, 6.5, n),       # chlorophyll
        rng.uniform(0.0, 1.0, n),       # upwelling
        rng.uniform(20, 90, n),         # thermocline depth
        rng.uniform(0.05, 0.8, n),      # current speed
    ])

    # Synthetic relationship used only for UI demonstration.
    hsi = (
        0.35
        + 0.18 * np.exp(-((X[:,0] - 21.8) ** 2) / 1.5)
        + 0.16 * np.tanh(X[:,1] / 4)
        + 0.18 * X[:,2]
        + 0.10 * np.exp(-((X[:,3] - 50) ** 2) / 700)
        - 0.05 * X[:,4]
    )
    hsi = np.clip(hsi + rng.normal(0, 0.025, n), 0, 1)

    reg = RandomForestRegressor(n_estimators=120, random_state=7, min_samples_leaf=6)
    reg.fit(X, hsi)

    return {"hsi_model": reg}

def predict_habitat(model, conditions):
    x = [[
        conditions["sst"],
        conditions["chlorophyll"],
        conditions["upwelling"],
        conditions["thermocline_depth"],
        conditions["current_speed"],
    ]]
    return float(np.clip(model["hsi_model"].predict(x)[0], 0, 1))

def predict_movement(model, conditions):
    hsi = predict_habitat(model, conditions)

    # Demonstration movement logic.
    # This will be replaced by a trained spatiotemporal model once historical
    # observations are connected.
    direction = "South-east"
    distance_km = int(8 + 18 * hsi)
    depth_center = int(45 + 25 * (1 - hsi))
    depth_range = f"{depth_center-10}–{depth_center+10} m"

    risk = float(np.clip(
        0.82
        - 0.45 * hsi
        + 0.18 * max(0, conditions["sst"] - 22.5),
        0, 1
    ))

    confidence = int(np.clip(55 + 35 * hsi, 0, 95))

    return {
        "direction": direction,
        "distance_km": distance_km,
        "depth_range": depth_range,
        "hsi": round(hsi, 2),
        "risk": round(risk, 2),
        "confidence": confidence,
    }
