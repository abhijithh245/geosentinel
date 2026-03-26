import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# -------------------------------
# 📌 Page Config
# -------------------------------
st.set_page_config(layout="wide")
st.title("Chennai Compound Risk Early Warning Dashboard")
st.caption("Interactive Digital Twin for Multi-Hazard Risk Simulation")

# -------------------------------
# 📂 Load Data
# -------------------------------
gdf = gpd.read_file("final_risk.geojson")
gdf = gdf.to_crs(epsg=4326)

# -------------------------------
# 🎨 Color function
# -------------------------------
def get_color(score):
    if score > 70:
        return "red"
    elif score >= 40:
        return "yellow"
    else:
        return "green"

# -------------------------------
# ⏳ Digital Twin (DAY SLIDER)
# -------------------------------
st.subheader("Digital Twin Simulation")
day = st.slider("Select Prediction Day", 1, 30)

# -------------------------------
# 🗺️ Dynamic Map
# -------------------------------
st.subheader("Risk Map")

m = folium.Map(location=[13.08, 80.27], zoom_start=10)

for _, row in gdf.iterrows():
    score = row.get(f"day{day}_predicted", row["compound_score"])

    folium.GeoJson(
        row["geometry"],
        style_function=lambda x, score=score: {
            "fillColor": get_color(score),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=f"{row['name']} | Score: {score:.2f}"
    ).add_to(m)

st_folium(m, width=900, height=500)

# -------------------------------
# 🚨 Alert Panel
# -------------------------------
st.subheader("⚠️ Critical Zones")

critical = gdf[gdf["compound_score"] > 70]

for _, row in critical.iterrows():
    st.error(f"{row['name']} → {row['compound_score']:.1f}")

# -------------------------------
# 🏘️ Zone Selection
# -------------------------------
zone = st.selectbox("Select Zone", gdf["name"])
selected = gdf[gdf["name"] == zone].iloc[0]

# -------------------------------
# 📊 Component Scores
# -------------------------------
st.subheader("Component Risk Scores")

st.write(f"Heat: {selected['heat_score']:.1f}")
st.write(f"Flood: {selected['flood_score']:.1f}")
st.write(f"AQI: {selected['aqi_score']:.1f}")

# -------------------------------
# 📈 30-Day Prediction
# -------------------------------
st.subheader("30-Day Risk Prediction")

prediction_cols = [f"day{i}_predicted" for i in range(1, 31)]
predictions = [selected.get(c, selected["compound_score"]) for c in prediction_cols]

st.line_chart(predictions)

# -------------------------------
# 🌍 Scenario Simulation
# -------------------------------
st.subheader("Scenario Simulation")

heat_input = st.slider("Increase Heat Stress", 0.0, 10.0, 0.0)
flood_input = st.slider("Increase Flood Risk", 0.0, 10.0, 0.0)
aqi_input = st.slider("Increase Air Pollution", 0.0, 10.0, 0.0)

base_heat = selected["heat_score"]
base_flood = selected["flood_score"]
base_aqi = selected["aqi_score"]

new_heat = min(base_heat + heat_input, 100)
new_flood = min(base_flood + flood_input, 100)
new_aqi = min(base_aqi + aqi_input, 100)

# 🔥 TRAIN MODEL (NO CACHE → NO ERROR)
X = gdf[["heat_score", "flood_score", "aqi_score"]].values
y = gdf["compound_score"].values

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Predict
new_prediction = model.predict([[new_heat, new_flood, new_aqi]])[0]

# Display
st.write("### Scenario Result")
st.write(f"Original Risk: {selected['compound_score']:.2f}")
st.write(f"Simulated Risk: {new_prediction:.2f}")

if new_prediction > 70:
    st.error(f"🔴 High Risk Scenario: {new_prediction:.2f}")
elif new_prediction >= 40:
    st.warning(f"🟡 Moderate Risk Scenario: {new_prediction:.2f}")
else:
    st.success(f"🟢 Low Risk Scenario: {new_prediction:.2f}")

# -------------------------------
# 🧠 AI Briefing (FROM FILE)
# -------------------------------
st.subheader("AI Briefing")

if "ai_briefing" in gdf.columns:
    st.write(selected["ai_briefing"])
else:
    st.info("No AI briefing available.")
