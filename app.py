import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk

from model import build_demo_model, predict_movement


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="E-AWARE — Fishing Intelligence",
    page_icon="🐟",
    layout="wide",
)

st.title("🐟 E-AWARE")
st.caption("Daily Ocean Intelligence & Fishing Decision Support")

st.info(
    "DEMO MVP: ocean and fisheries data are currently synthetic. "
    "This system demonstrates the decision-support workflow and "
    "must not be used as real fishing advice."
)


# ============================================================
# DEMO FISH DATA
# ============================================================

rng = np.random.default_rng(42)

fish = pd.DataFrame({
    "lat": [
        -4.98,
        -5.03,
        -5.08,
        -5.13,
        -5.19,
        -5.25,
        -5.31,
        -5.37,
    ],
    "lon": [
        -81.10,
        -81.06,
        -81.02,
        -80.98,
        -80.94,
        -80.90,
        -80.86,
        -80.82,
    ],
    "depth_min": [
        32, 36, 40, 43,
        47, 51, 55, 58
    ],
    "depth_max": [
        45, 50, 54, 58,
        63, 68, 73, 78
    ],
    "biomass_index": [
        0.48,
        0.61,
        0.74,
        0.88,
        0.95,
        0.83,
        0.68,
        0.52,
    ],
    "status": [
        "Observed",
        "Observed",
        "Observed",
        "Observed",
        "Observed",
        "Estimated",
        "Estimated",
        "Estimated",
    ],
})

fish["mean_depth"] = (
    fish["depth_min"] + fish["depth_max"]
) / 2

fish["confidence"] = [
    0.91,
    0.90,
    0.88,
    0.87,
    0.84,
    0.76,
    0.69,
    0.61,
]


# ============================================================
# OCEAN DATA
# ============================================================

n = 250

ocean = pd.DataFrame({
    "lat": rng.uniform(-5.55, -4.75, n),
    "lon": rng.uniform(-81.35, -80.55, n),
})

ocean["sst"] = (
    21.2
    + 1.1 * np.sin((ocean["lat"] + 5.15) * 4)
    + rng.normal(0, 0.18, n)
)

ocean["chlorophyll"] = np.clip(
    2.5
    + 1.7
    * np.exp(-((ocean["lon"] + 80.95) ** 2) / 0.04)
    + rng.normal(0, 0.35, n),
    0.3,
    7.0,
)

ocean["upwelling"] = np.clip(
    0.55
    + 0.25 * np.cos((ocean["lon"] + 80.95) * 5)
    + rng.normal(0, 0.08, n),
    0,
    1,
)


# ============================================================
# MODEL
# ============================================================

model = build_demo_model()

current_conditions = {
    "sst": 22.0,
    "chlorophyll": 4.1,
    "upwelling": 0.72,
    "thermocline_depth": 48,
    "current_speed": 0.32,
}

prediction = predict_movement(
    model,
    current_conditions,
)


# ============================================================
# DECISION VARIABLES
# ============================================================

hsi = float(prediction["hsi"])
risk = float(prediction["risk"])
confidence = int(prediction["confidence"])

recommended_pressure = max(
    0,
    min(
        100,
        round((1 - risk) * 100),
    ),
)


if confidence >= 70 and risk < 0.70:
    decision_status = "RECOMMENDED"
    decision_icon = "🟢"
elif confidence >= 50 and risk < 0.80:
    decision_status = "CAUTION"
    decision_icon = "🟠"
else:
    decision_status = "LOW CONFIDENCE / NO-GO"
    decision_icon = "🔴"


# ============================================================
# TODAY'S DECISION
# ============================================================

st.subheader("☀️ Today's Fishing Decision")

d1, d2, d3, d4 = st.columns(4)

d1.metric(
    "Status",
    f"{decision_icon} {decision_status}",
)

d2.metric(
    "Direction",
    prediction["direction"],
)

d3.metric(
    "Expected depth",
    prediction["depth_range"],
)

d4.metric(
    "Confidence",
    f"{confidence}%",
)


st.markdown(
    f"""
### {decision_icon} Primary recommendation

**Direction:** {prediction["direction"]}  
**Expected range:** approximately {prediction["distance_km"]} km  
**Expected anchoveta depth:** {prediction["depth_range"]}  
**Habitat suitability:** {hsi:.2f}  
**Ecological risk:** {risk:.2f}  
**Prediction confidence:** {confidence}%

> E-AWARE converts ocean and fisheries information into a
> simple decision recommendation. The final fishing decision
> remains with the fisher and applicable authorities.
"""
)


# ============================================================
# MAP CONTROLS
# ============================================================

st.sidebar.header("Map")

layer = st.sidebar.selectbox(
    "Select layer",
    [
        "Decision zones",
        "Fish observations",
        "SST",
        "Chlorophyll-a",
        "Upwelling",
    ],
)


# ============================================================
# DECISION ZONE MAP
# ============================================================

st.subheader("🧭 Decision Map")

if layer == "Decision zones":

    # Main recommended zone
    recommended_zone = pd.DataFrame({
        "lat": [-5.17],
        "lon": [-80.90],
        "label": ["PRIMARY — South-East"],
        "status": ["Recommended"],
        "depth": ["50–70 m"],
        "confidence": [confidence],
        "color": [[35, 180, 90, 190]],
    })

    # Alternative zone
    alternative_zone = pd.DataFrame({
        "lat": [-5.08],
        "lon": [-80.94],
        "label": ["ALTERNATIVE — South"],
        "status": ["Alternative"],
        "depth": ["45–60 m"],
        "confidence": [64],
        "color": [[240, 170, 50, 150]],
    })

    zones = pd.concat(
        [
            recommended_zone,
            alternative_zone,
        ],
        ignore_index=True,
    )

    zone_layer = pdk.Layer(
        "ScatterplotLayer",
        data=zones,
        get_position="[lon, lat]",
        get_radius=11000,
        get_fill_color="color",
        pickable=True,
        stroked=True,
        filled=True,
        opacity=0.45,
    )

    # Movement arrow / line
    movement_line = pd.DataFrame({
        "start": [[-5.13, -80.98]],
        "end": [[-5.17, -80.90]],
    })

    line_layer = pdk.Layer(
        "LineLayer",
        data=movement_line,
        get_source_position="start",
        get_target_position="end",
        get_width=7,
        get_color=[40, 120, 220],
        pickable=False,
    )

    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=-5.14,
            longitude=-80.96,
            zoom=9.5,
            pitch=0,
        ),
        layers=[
            zone_layer,
            line_layer,
        ],
        tooltip={
            "html": """
            <b>{label}</b><br/>
            Status: {status}<br/>
            Depth: {depth}<br/>
            Confidence: {confidence}%
            """
        },
    )

    st.pydeck_chart(
        deck,
        width="stretch",
        height=520,
    )

    st.markdown(
        """
        **Map legend**

        🟢 Primary recommended zone  
        🟠 Alternative zone  
        🔵 Predicted movement direction
        """
    )


# ============================================================
# FISH OBSERVATIONS
# ============================================================

elif layer == "Fish observations":

    fish_map = fish.copy()

    fish_map["color"] = fish_map["status"].map({
        "Observed": [30, 170, 90, 210],
        "Estimated": [245, 180, 45, 190],
    })

    fish_layer = pdk.Layer(
        "ScatterplotLayer",
        data=fish_map,
        get_position="[lon, lat]",
        get_radius="biomass_index * 4500",
        get_fill_color="color",
        pickable=True,
        opacity=0.8,
    )

    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=-5.16,
            longitude=-80.98,
            zoom=9.5,
            pitch=0,
        ),
        layers=[fish_layer],
        tooltip={
            "html": """
            <b>{status}</b><br/>
            Depth: {depth_min}–{depth_max} m<br/>
            Confidence: {confidence}
            """
        },
    )

    st.pydeck_chart(
        deck,
        width="stretch",
        height=520,
    )


# ============================================================
# ENVIRONMENTAL MAPS
# ============================================================

else:

    value_col = {
        "SST": "sst",
        "Chlorophyll-a": "chlorophyll",
        "Upwelling": "upwelling",
    }[layer]

    env_layer = pdk.Layer(
        "ScatterplotLayer",
        data=ocean,
        get_position="[lon, lat]",
        get_radius=1800,
        get_fill_color="[80, 150, 220, 150]",
        pickable=True,
    )

    deck = pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        initial_view_state=pdk.ViewState(
            latitude=-5.16,
            longitude=-80.98,
            zoom=9.5,
            pitch=0,
        ),
        layers=[env_layer],
        tooltip={
            "text": f"{layer}: {{{value_col}}}"
        },
    )

    st.pydeck_chart(
        deck,
        width="stretch",
        height=520,
    )


# ============================================================
# 7 DAY FORECAST
# ============================================================

st.subheader("🔮 7-Day Movement Forecast")

f1, f2, f3, f4 = st.columns(4)

f1.metric(
    "Movement",
    prediction["direction"],
)

f2.metric(
    "Distance",
    f'{prediction["distance_km"]} km',
)

f3.metric(
    "Depth",
    prediction["depth_range"],
)

f4.metric(
    "Confidence",
    f'{prediction["confidence"]}%',
)


# ============================================================
# ECOLOGICAL MANAGEMENT
# ============================================================

st.subheader("🌱 Ecological Decision Support")

e1, e2, e3 = st.columns(3)

e1.metric(
    "Habitat suitability",
    f"{hsi:.2f}",
)

e2.metric(
    "Ecological risk",
    f"{risk:.2f}",
)

e3.metric(
    "Recommended pressure",
    f"{recommended_pressure}%",
)

st.progress(
    recommended_pressure / 100
)

st.warning(
    "E-AWARE's recommended fishing pressure is an ecological "
    "decision-support indicator, NOT a legal quota. Legal "
    "limits and closures must come from the relevant authority."
)


# ============================================================
# DAILY MESSAGE PREVIEW
# ============================================================

st.subheader("📱 04:00 Fisher Brief")

message = f"""🐟 E-AWARE | 04:00

{decision_icon} {decision_status}

📍 Primary direction: {prediction["direction"]}
📏 Distance: ~{prediction["distance_km"]} km
🌊 Depth: {prediction["depth_range"]}

🎯 Habitat suitability: {hsi:.2f}
⚠️ Ecological risk: {risk:.2f}
📊 Confidence: {confidence}%

🎣 Recommended pressure: {recommended_pressure}%

Updated before departure.

E-AWARE is decision support,
not a legal fishing instruction.
"""

st.code(
    message,
    language="text",
)

st.caption(
    "The same message can be automatically sent to registered "
    "fishers through Telegram using the daily GitHub workflow."
)


# ============================================================
# DATA HEALTH
# ============================================================

st.subheader("🛰️ Data Sources")

health = pd.DataFrame({
    "Source": [
        "IMARPE",
        "Copernicus Marine",
        "Satellite",
        "Fisher observations",
    ],
    "Current MVP": [
        "PLANNED",
        "PLANNED",
        "DEMO",
        "DEMO",
    ],
    "Purpose": [
        "Fish distribution and scientific surveys",
        "Ocean conditions and forecasts",
        "SST / chlorophyll / environmental signals",
        "Optional local observations",
    ],
})

st.dataframe(
    health,
    hide_index=True,
    width="stretch",
)


# ============================================================
# PRIVACY PRINCIPLE
# ============================================================

with st.expander("🔐 Fisher Privacy"):

    st.write(
        """
        **Private by default. Collective when beneficial.**

        Individual fishing locations and catches should remain
        private.

        Aggregated environmental and scientific information can
        be used to improve community-level intelligence.

        The system should not require fishermen to reveal
        commercially sensitive fishing spots.
        """
    )


st.caption(
    "E-AWARE MVP — Community Ocean Intelligence for Resilient Fisheries"
)
