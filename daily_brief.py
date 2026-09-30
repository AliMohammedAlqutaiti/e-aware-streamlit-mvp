from model import build_demo_model, predict_movement


def generate_daily_brief():
    """
    Generate the 04:00 E-AWARE fisher decision brief.

    Current version uses synthetic demo data.
    Replace with validated IMARPE/Copernicus data
    before real-world deployment.
    """

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
        status = "🟢 RECOMMENDED"

    elif confidence >= 50 and risk < 0.80:
        status = "🟠 CAUTION"

    else:
        status = "🔴 LOW CONFIDENCE / NO-GO"

    message = f"""🐟 E-AWARE | 04:00

{status}

📍 Primary direction: {prediction["direction"]}
📏 Distance: ~{prediction["distance_km"]} km
🌊 Expected depth: {prediction["depth_range"]}

🎯 Habitat suitability: {hsi:.2f}
⚠️ Ecological risk: {risk:.2f}
📊 Confidence: {confidence}%

🎣 Recommended pressure: {recommended_pressure}%

Updated before departure.

E-AWARE is decision support,
not a legal fishing instruction.

DEMO: synthetic data.
"""

    return message


if __name__ == "__main__":
    print(generate_daily_brief())
