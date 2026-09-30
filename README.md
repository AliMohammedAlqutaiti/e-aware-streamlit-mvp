# E-AWARE Streamlit MVP

A prototype of **E-AWARE — Community Ocean Intelligence for Resilient Fisheries**.

## What this MVP demonstrates

- Interactive Peru/Costanera-area fish map
- Observed vs estimated fish locations
- Fish depth ranges
- Ocean layers (SST, chlorophyll-a, upwelling)
- Vertical temperature profile
- Habitat suitability model
- 7-day movement prediction
- Ecological fishing-pressure recommendation
- Private fisher recommendation
- Optional anonymised/coarse fisher observation
- Data-source health panel

## Important

The current app uses **synthetic demonstration data**. It is not real fishing advice and should not be used for real fishing decisions.

The next development stage is to connect validated data sources such as IMARPE and Copernicus Marine, then train/validate the movement model on historical observations.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Suggested GitHub → Streamlit deployment

1. Create a GitHub repository, e.g. `e-aware-streamlit`.
2. Upload:
   - `app.py`
   - `model.py`
   - `requirements.txt`
   - `README.md`
3. In Streamlit Community Cloud, create a new app and select the repository and `app.py`.

Streamlit supports interactive map visualisation through `st.map` and `st.pydeck_chart`; this MVP uses PyDeck because it gives us more control over layers and tooltips.

## Roadmap

### V0 — current
Synthetic data + working UI + demo model.

### V1
Connect:
- IMARPE scientific observations
- Copernicus Marine ocean conditions
- Satellite SST/chlorophyll

### V2
Historical database:
- fish observations
- depth
- biomass/density
- ocean conditions
- time/season
- fishing effort

### V3
Validated prediction:
- habitat suitability
- location probability
- depth prediction
- movement forecast
- uncertainty/confidence

### V4
Community system:
- private fisher accounts
- coarse/anonymised observations
- weekly reports
- safety alerts
- conservation indicators
