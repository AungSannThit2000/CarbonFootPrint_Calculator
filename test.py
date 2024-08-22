import streamlit as st
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import openai
import os
from dotenv import load_dotenv





# Load environment variables from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
def reset_input():
    st.session_state.waste_kg = 0.00
    st.session_state.electricity_kwh = 0.00
    st.session_state.distance_traveled = 0.00
    st.session_state.number_of_trips = 1

# Function to get AI-generated tips based on carbon footprint
def get_footprint_tips(footprint):
    # Define a prompt based on the carbon footprint value
    prompt = f"My monthly carbon footprint is {footprint:.2f} kg CO2. Is it good or bad?"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" or another model depending on your API provider
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar for navigation
st.image("Footprint.png", use_column_width=True, caption="Embrace a Greener Future")

st.sidebar.title("Choose an app")
page = st.sidebar.radio("Go to", ["Distance Calculator", "Carbon Footprint Calculator"])

# Page 1: Distance Calculator
if page == "Distance Calculator":
    st.title("Get the distance")

    # Session state to store selected points
    if 'points' not in st.session_state:
        st.session_state.points = []

    # Determine the center of the map
    if st.session_state.points:
        # Center the map on the last selected point
        map_center = st.session_state.points[-1]
    else:
        # Default location (Assumption University of Thailand)
        map_center = [13.612015, 100.836967]

    zoom_level = 15  # Zoom level for the map

    # Create the map centered on the last clicked location or default location
    m = folium.Map(location=map_center, zoom_start=zoom_level)

    # Add markers for all stored points
    for point in st.session_state.points:
        folium.Marker(location=point).add_to(m)

    # Add map functionality to capture clicks
    data = st_folium(m, height=500, width=700)

    # Handle map clicks and store the points
    if data and data['last_clicked']:
        lat_lon = [data['last_clicked']['lat'], data['last_clicked']['lng']]
        st.session_state.points.append(lat_lon)

        # Display the selected coordinates
        st.write(f"Selected Location: Latitude = {lat_lon[0]}, Longitude = {lat_lon[1]}")

        # Limit the number of points to 2
        if len(st.session_state.points) > 2:
            st.session_state.points = st.session_state.points[-2:]

    # Distance calculation and display
    if len(st.session_state.points) == 2:
        loc1 = st.session_state.points[0]
        loc2 = st.session_state.points[1]

        # Calculate the distance
        distance = geodesic(loc1, loc2).kilometers

        # Display the distance
        st.write(f"The distance between the two locations is: **{distance:.2f} kilometers**")

    # Reset button to clear points and reset the map
    if st.button("Reset Map"):
        # Clear the session state
        st.session_state.points = []

        # Reinitialize the map by creating a new folium Map object centered at the default location
        m = folium.Map(location=[13.6525, 100.4931], zoom_start=zoom_level)
        st_folium(m, height=500, width=700)
        st.write("Map has been reset. Please select new locations.")

# Page 2: Carbon Footprint Calculator
elif page == "Carbon Footprint Calculator":
    st.title("Monthly Carbon Footprint Calculator")

    # Session state to store transportation records
    if 'transportation_records' not in st.session_state:
        st.session_state.transportation_records = []

    # Input for adding a new transportation record
    st.subheader("Add Transportation Record")
    transport_type = st.selectbox("Select Transportation Type",
                                  ["Car", "Public Transport (Bus/Train)", "Short-haul Flight", "Long-haul Flight"])
    distance_traveled = st.number_input("Distance Traveled (in kilometers)", min_value=0.0, format="%.2f", value=0.0, key= 'distance_traveled')
    number_of_trips = st.number_input("Number of Trips", min_value=1, value=1, key= 'number_of_trips')

    # Button to add the transportation record
    if st.button("Add Transportation Record"):
        if distance_traveled > 0 and number_of_trips > 0:
            st.session_state.transportation_records.append({
                "type": transport_type,
                "distance": distance_traveled,
                "trips": number_of_trips
            })
            st.success(f"Added {transport_type} - {distance_traveled} km x {number_of_trips} trips")

    # Display the added transportation records
    if st.session_state.transportation_records:
        st.subheader("Transportation Records")
        for idx, record in enumerate(st.session_state.transportation_records):
            st.write(f"{idx + 1}. {record['type']} - {record['distance']} km x {record['trips']} trips")

    # Conversion factors for carbon emissions
    EMISSION_FACTORS = {
        "Car": 0.271,  # kg CO2 per km
        "Public Transport (Bus/Train)": 0.1,  # kg CO2 per km
        "Short-haul Flight": 0.255,  # kg CO2 per km
        "Long-haul Flight": 0.150  # kg CO2 per km
    }

    # Calculate the total transportation carbon footprint
    total_transportation_footprint = 0
    for record in st.session_state.transportation_records:
        emission_factor = EMISSION_FACTORS.get(record["type"], 0)
        total_transportation_footprint += record["distance"] * record["trips"] * emission_factor

    # Input fields for Electricity Usage
    st.subheader("Electricity Usage")
    electricity_kwh = st.number_input("How many kilowatt-hours (kWh) of electricity did you use?",min_value=0.0, format="%.2f", value=0.0 , key = 'electricity_kwh' )
    ELECTRICITY_EMISSION_FACTOR = 0.92  # kg CO2 per kWh
    electricity_footprint = electricity_kwh * ELECTRICITY_EMISSION_FACTOR

    # Input fields for Food Consumption
    st.subheader("Food Consumption")
    diet_type = st.selectbox("What is your diet type?", ["Omnivore", "Vegetarian", "Vegan"])
    FOOD_EMISSION_FACTOR = {"Omnivore": 2.5, "Vegetarian": 1.7, "Vegan": 1.5}  # kg CO2 per day
    food_footprint = FOOD_EMISSION_FACTOR[diet_type] * 30  # Assume 30 days in a month

    # Input fields for Waste Generation
    st.subheader("Waste Generation")
    waste_kg = st.number_input("How many kilograms of waste did you generate?", min_value=0.0, format="%.2f", value=0.0, key = 'waste_kg')
    WASTE_EMISSION_FACTOR = 0.5  # kg CO2 per kg of waste
    waste_footprint = waste_kg * WASTE_EMISSION_FACTOR

    # Calculate total carbon footprint
    total_carbon_footprint = total_transportation_footprint + electricity_footprint + food_footprint + waste_footprint

    # Display the results
    st.header("Your Estimated Monthly Carbon Footprint")
    st.write(f"**Transportation:** {total_transportation_footprint:.2f} kg CO2")
    st.write(f"**Electricity Usage:** {electricity_footprint:.2f} kg CO2")
    st.write(f"**Food Consumption:** {food_footprint:.2f} kg CO2")
    st.write(f"**Waste Generation:** {waste_footprint:.2f} kg CO2")
    st.write(f"### Total Monthly Carbon Footprint: {total_carbon_footprint:.2f} kg CO2")

    # Generate AI tips based on the carbon footprint
    if total_carbon_footprint > 0:
        st.subheader("Carbonbot's Tips to Reduce Your Carbon Footprint")
        ai_tips = get_footprint_tips(total_carbon_footprint)
        st.write(ai_tips)
# Button to reset all inputs
    button = st.button("Reset Carbon Footprint Calculator",on_click = reset_input)
        # Reset session state variables


def get_bot_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can change the model if needed
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"




# New Section: Carbonbot
    st.subheader("Carbonbot: Your Personal Sustainability Assistant")

    # Initialize the chat history in session state if not already present
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Text input for the user's message
    user_input = st.text_input("Ask Carbonbot for tips or advice:")

    # Button to submit the message
    if st.button("Send"):
        if user_input:
            # Append the user input to the chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Get the chatbot response
            bot_response = get_bot_response(user_input)

            # Append the bot response to the chat history
            st.session_state.chat_history.append({"role": "bot", "content": bot_response})

        else:
            st.write("Please enter a message to send to Carbonbot.")

    # Display the conversation history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message['role'] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**Carbonbot:** {message['content']}")

    # Button to clear the chat
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.write("Chat cleared.")