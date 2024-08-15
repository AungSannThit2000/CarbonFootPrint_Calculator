import streamlit as st

def calculate_carbon_footprint(transport, energy, food, waste):
    # Simple coefficients for carbon footprint calculation (in metric tons of CO2e per year)
    transport_footprint = transport * 0.2  # Example: 0.2 tons CO2e per 1000 km/year
    energy_footprint = energy * 0.3  # Example: 0.3 tons CO2e per MWh
    food_footprint = food * 0.1  # Example: 0.1 tons CO2e per month for meat consumption
    waste_footprint = waste * 0.05  # Example: 0.05 tons CO2e per kg of waste

    total_footprint = transport_footprint + energy_footprint + food_footprint + waste_footprint
    return total_footprint

# Streamlit UI
st.title("Carbon Footprint Calculator")

st.header("Transportation")
transport = st.slider("How many kilometers do you travel by car per year?", 0, 50000, step=500)

st.header("Energy Usage")
energy = st.slider("How many MWh of electricity do you use per year?", 0, 50, step=1)

st.header("Food Consumption")
food = st.slider("How many times per month do you eat meat?", 0, 100, step=1)

st.header("Waste Production")
waste = st.slider("How many kilograms of waste do you produce per week?", 0, 50, step=1)

# Calculate footprint
carbon_footprint = calculate_carbon_footprint(transport, energy, food, waste)
st.subheader(f"Your estimated carbon footprint is {carbon_footprint:.2f} metric tons of CO2e per year.")

# Tips for reducing carbon footprint
st.header("Tips to Reduce Your Carbon Footprint")
st.write("""
- **Reduce car travel:** Consider carpooling, public transportation, biking, or walking.
- **Save energy:** Switch to energy-efficient appliances and use renewable energy sources.
- **Eat less meat:** Consider reducing your meat consumption or switching to plant-based alternatives.
- **Reduce waste:** Recycle, compost, and minimize single-use plastics.
""")