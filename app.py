import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk

from model import build_demo_model, predict_movement


st.set_page_config(
    page_title="E-AWARE — Fish Intelligence",
    page_icon="🐟",
    layout="wide",
)

st.title("🐟 E-AWARE")
st.caption("Community Ocean Intelligence for Resilient Fisheries")

st.info(
    "MVP DEMO: the current observations and predictions are synthetic demonstration data. "
    "They are NOT real fishing advice. Replace them with validated IMARPE/Copernicus data before deployment."
)


# ============================================================
# DEMO DATA
# ============================================================

rng = np.random.default_rng(42)

# Costanera / Lobitos demonstration area
fish = pd.DataFrame({
    "lat": [
        -4.98, -5.03, -5.08, -5.13,
        -5.19, -5.25, -5.31, -5.37
    ],
    "lon": [
        -81.10, -81.06, -81.02, -80.98,
        -80.94, -80.90, -80.86, -80.82
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
        0.48, 0.61, 0.74, 0.88,
        0.95, 0.83, 0.68, 0.52
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
# SYNTHETIC OCEAN DATA
# ============================================================

n = 220

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
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("Controls")

layer = st.sidebar.selectbox(
    "Ocean layer",
    [
        "Fish habitat",
        "SST",
        "Chlorophyll-a",
        "Upwelling",
    ],
)

show_observed = st.sidebar.checkbox(
    "Observed fish",
    True,
)

show_estimated = st.sidebar.checkbox(
    "Estimated fish",
    True,
)


# ============================================================
# TOP METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Fish concentration",
    "HIGH",
)

c2.metric(
    "Estimated depth",
    "47–68 m",
)

c3.metric(
    "Environmental risk",
    "MEDIUM",
)

c4.metric(
    "Prediction confidence",
    "76%",
)


# ============================================================
# MAP
# ============================================================

st.subheader("🌊 Live Fish & Ocean Map")


if layer == "Fish habitat":

    map_data = fish.copy()

    # Colour is stored in the dataframe.
    map_data["color"] = map_data["status"].map({
        "Observed": [30, 170, 90, 210],
        "Estimated": [245, 180, 45, 190],
    })

    if not show_observed:
        map_data = map_data[
            map_data["status"] != "Observed"
        ]

    if not show_estimated:
        map_data = map_data[
            map_data["status"] != "Estimated"
        ]

    layer_obj = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position="[lon, lat]",
        get_radius="biomass_index * 5000",
        get_fill_color="color",
        pickable=True,
        opacity=0.8,
    )

    tooltip = {
        "html": (
            "<b>{status}</b><br/>"
            "Depth: {depth_min}–{depth_max} m<br/>"
            "Confidence: {confidence}"
        ),
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
        },
    }


else:

    value_col = {
        "SST": "sst",
        "Chlorophyll-a": "chlorophyll",
        "Upwelling": "upwelling",
    }[layer]

    layer_obj = pdk.Layer(
        "ScatterplotLayer",
        data=ocean,
        get_position="[lon, lat]",
        get_radius=1700,
        get_fill_color="[80, 150, 220, 150]",
        pickable=True,
    )

    tooltip = {
        "text": f"{layer}: {{{value_col}}}"
    }


deck = pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=-5.16,
        longitude=-80.98,
        zoom=9.2,
        pitch=35,
    ),
    layers=[layer_obj],
    tooltip=tooltip,
)

st.pydeck_chart(
    deck,
    width="stretch",
    height=520,
)


# ============================================================
# CURRENT HOTSPOT
# ============================================================

st.subheader("📍 Most Probable Aggregation")

hotspot = fish.iloc[4]

a, b, c, d = st.columns(4)

a.metric(
    "Latitude",
    f"{abs(hotspot['lat']):.2f}°S",
)

b.metric(
    "Longitude",
    f"{abs(hotspot['lon']):.2f}°W",
)

c.metric(
    "Depth",
    f"{int(hotspot['depth_min'])}–{int(hotspot['depth_max'])} m",
)

d.metric(
    "Confidence",
    f"{int(hotspot['confidence'] * 100)}%",
)


# ============================================================
# VERTICAL OCEAN PROFILE
# ============================================================

st.subheader("🌊 Vertical Ocean Profile")

depths = np.arange(
    0,
    101,
    5,
)

temperature = (
    23.0
    - 0.055 * depths
    + 0.7
    * np.exp(-((depths - 48) ** 2) / 500)
)

profile = pd.DataFrame({
    "Depth (m)": depths,
    "Temperature (°C)": temperature,
})

profile["Fish aggregation"] = np.where(
    (
        profile["Depth (m)"] >= hotspot["depth_min"]
    )
    & (
        profile["Depth (m)"] <= hotspot["depth_max"]
    ),
    1,
    0,
)

st.line_chart(
    profile.set_index("Depth (m)")[
        ["Temperature (°C)"]
    ]
)

st.caption(
    "The aggregation range is represented numerically in the demo. "
    "A production UI would overlay the fish aggregation directly on the profile."
)


# ============================================================
# PREDICTION ENGINE
# ============================================================

st.subheader("🔮 7-Day Movement Prediction")

model = build_demo_model()

current = {
    "sst": 22.0,
    "chlorophyll": 4.1,
    "upwelling": 0.72,
    "thermocline_depth": 48,
    "current_speed": 0.32,
}

prediction = predict_movement(
    model,
    current,
)

p1, p2, p3, p4 = st.columns(4)

p1.metric(
    "Movement",
    prediction["direction"],
)

p2.metric(
    "Depth forecast",
    prediction["depth_range"],
)

p3.metric(
    "7-day confidence",
    f'{prediction["confidence"]}%',
)

p4.metric(
    "Habitat suitability",
    f'{prediction["hsi"]:.2f}',
)

st.write(
    f"**Forecast:** most probable aggregation shifts "
    f"approximately **{prediction['distance_km']} km "
    f"{prediction['direction'].lower()}** under the current "
    f"demo conditions."
)


# ============================================================
# FISHING MANAGEMENT
# ============================================================

st.subheader("🎣 Fishing Management")

hsi = prediction["hsi"]
risk = prediction["risk"]

recommended_pressure = max(
    0,
    min(
        100,
        round((1 - risk) * 100),
    ),
)

m1, m2, m3 = st.columns(3)

m1.metric(
    "Habitat suitability",
    f"{hsi:.2f}",
)

m2.metric(
    "Ecological risk",
    f"{risk:.2f}",
)

m3.metric(
    "E-AWARE recommended pressure",
    f"{recommended_pressure}%",
)

st.progress(
    recommended_pressure / 100
)

st.warning(
    "This is an ecological recommendation for the prototype, "
    "not a legal fishing quota. Legal limits must come from "
    "the relevant authority and current regulations."
)


# ============================================================
# PRIVATE FISHER VIEW
# ============================================================

st.subheader("🔐 Private Fisher Recommendation")

st.caption(
    "Design principle: individual fishing information remains "
    "private; only aggregated information is used for "
    "community/scientific intelligence."
)

home_port = st.selectbox(
    "Your departure area",
    [
        "Lobitos",
        "Piedritas",
        "Sichez",
    ],
)

vessel_type = st.selectbox(
    "Vessel type",
    [
        "Small-scale boat",
        "Larger vessel",
    ],
)

private_rec = {
    "Lobitos": (
        "South-east",
        "12–18 km offshore",
        "45–65 m",
    ),
    "Piedritas": (
        "South",
        "10–16 km offshore",
        "40–60 m",
    ),
    "Sichez": (
        "South-west",
        "14–20 km offshore",
        "50–70 m",
    ),
}[home_port]

st.success(
    f"**Private recommendation for {home_port}:** "
    f"search zone trend **{private_rec[0]}**, approximately "
    f"**{private_rec[1]}**, with expected depth "
    f"**{private_rec[2]}**."
)

st.caption(
    "In production, this recommendation would be generated "
    "from validated ocean/fisheries data, the fisher's chosen "
    "privacy settings, vessel characteristics and the trained model."
)


# ============================================================
# OPTIONAL CATCH OBSERVATION
# ============================================================

with st.expander(
    "➕ Submit an optional catch observation"
):

    st.write(
        "The prototype never requires a fisherman to reveal "
        "an exact commercial fishing spot."
    )

    species = st.selectbox(
        "Species",
        [
            "Anchoveta",
            "Other",
        ],
    )

    depth = st.number_input(
        "Approximate depth (m)",
        0,
        500,
        50,
    )

    catch = st.number_input(
        "Approximate catch (kg)",
        0.0,
        100000.0,
        100.0,
    )

    area = st.selectbox(
        "Area (coarse)",
        [
            "Near shore",
            "Offshore",
            "Far offshore",
        ],
    )

    if st.button(
        "Save anonymised observation"
    ):
        st.success(
            "Observation stored for the demo model "
            "as an anonymised/coarse report."
        )


# ============================================================
# DATA SOURCES & SYSTEM HEALTH
# ============================================================

st.subheader(
    "🛰️ Data Sources & System Health"
)

health = pd.DataFrame({
    "Source": [
        "IMARPE",
        "Copernicus Marine",
        "Satellite",
        "Fisher observations",
    ],
    "Status": [
        "PLANNED",
        "PLANNED",
        "DEMO",
        "DEMO",
    ],
    "Role": [
        "Fish surveys / scientific observations",
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

st.caption(
    "Next integration step: replace synthetic data with "
    "validated feeds and preserve Observed / Estimated / "
    "Predicted labels throughout the interface."
)
