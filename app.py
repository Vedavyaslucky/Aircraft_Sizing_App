import streamlit as st
import math

# Page setup
st.set_page_config(page_title="Aircraft Sizing Estimator", page_icon="✈️", layout="centered")

st.title("✈️ Custom Aircraft Configuration & Sizing Tool")
st.write("Enter your passenger capacity requirements below to generate complete conceptual aircraft dimensions, subsystem specifications, and landing gear sizing.")

st.markdown("---")

# 1. THE ONLY CUSTOMER INPUT
st.subheader("Step 1: Enter Your Mission Requirements")
num_passengers = st.number_input("Desired Number of Passengers", min_value=1, max_value=100, value=8, step=1)

# 2. AUTOMATICALLY SCALE CREW & FUSELAGE (No hardcoded values)
if num_passengers > 50:
    num_crew = 5
elif num_passengers > 19:
    num_crew = 4
else:
    num_crew = 2

# Dynamically scale fuselage length: ~13 meters baseline for cockpit/tail + 1.2 meters per passenger pair
fuselage_length = round(13.0 + (num_passengers * 0.6), 3)

# 3. INTERNAL AERODYNAMIC CONSTANTS
v_stall_knots = 120
cl_max = 1.8
aspect_ratio = 8.7
rho_sea_level = 1.225  
g = 9.81

# 4. BACKEND SIZING ENGINE (Calculations triggered by user input)
# Mission weight fractions
w1_w0 = 0.97    # Takeoff
w2_w1 = 0.985   # Climb
w3_w2 = 0.774   # Cruise
w4_w3 = 1.0     # Descent
w5_w4 = 0.994   # Loiter
w6_w5 = 0.995   # Landing

mission_fuel_fraction = w1_w0 * w2_w1 * w3_w2 * w4_w3 * w5_w4 * w6_w5
mission_fuel_weight_fraction = 1.06 * (1.0 - mission_fuel_fraction)
empty_weight_fraction = 0.685

# Component Mass Breakdowns (kg per person)
passenger_weight = 90
passenger_luggage = 23
crew_weight = 90
crew_luggage = 10

w_payload = (passenger_weight + passenger_luggage) * num_passengers
w_crew = (crew_weight + crew_luggage) * num_crew
total_payload_weight = w_payload + w_crew

# Takeoff Weight Optimization
denominator = 1.0 - mission_fuel_weight_fraction - empty_weight_fraction
takeoff_weight = round(total_payload_weight / denominator)

# Wing Area and Geometry
v_stall_ms = v_stall_knots * 0.51444
wing_loading_stall = 0.5 * rho_sea_level * (v_stall_ms ** 2) * cl_max

wing_area = round((takeoff_weight * g) / wing_loading_stall, 2)
wing_span = round(math.sqrt(aspect_ratio * wing_area), 2)

# Scale root chord based on the dynamic wing area and aspect ratio
root_chord = round((2 * wing_area) / (wing_span * (1 + 0.25)), 3)
taper_ratio = 0.25
mean_aerodynamic_chord = round((2/3) * root_chord * ((1 + taper_ratio + taper_ratio**2) / (1 + taper_ratio)), 3)

# Tail Surface Area Sizing (Using the dynamic fuselage length!)
l_vt = 0.45 * fuselage_length
l_ht = l_vt
c_vt = 0.09
c_ht = 1.0

s_vt = round((c_vt * wing_area * wing_span) / l_vt, 2)
s_ht = round((c_ht * wing_area * mean_aerodynamic_chord) / l_ht, 2)

b_vt = round(math.sqrt(1.2 * s_vt), 2)
b_ht = round(math.sqrt(5 * s_ht), 2)

# Control Surfaces
b_a = round(0.3 * wing_span, 2)
c_a = round(0.25 * mean_aerodynamic_chord, 2)
b_r = round(0.8 * b_vt, 2)
c_r = round(0.25 * (mean_aerodynamic_chord * 1.2), 2)
b_e = round(0.9 * b_ht, 2)
c_e = round(0.3 * mean_aerodynamic_chord, 2)

# Landing Gear Structural Envelope
main_gear_load = 0.9 * takeoff_weight
nose_gear_load = 0.1 * takeoff_weight

main_gear_diameter = round(8.3 * ((main_gear_load / 4) ** 0.251), 2)
main_gear_width = round(3.5 * ((main_gear_load / 4) ** 0.216), 2)
nose_gear_diameter = round(8.3 * ((nose_gear_load / 2) ** 0.251), 2)
nose_gear_width = round(3.5 * ((nose_gear_load / 2) ** 0.216), 2)

# 5. CUSTOMER-FACING DISPLAY INTERFACE
st.markdown("---")
st.subheader("Step 2: Generated Aircraft Specifications")

# Primary High-Level Output Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Takeoff Weight", f"{takeoff_weight:,} kg")
    st.metric("Estimated Fuselage Length", f"{fuselage_length} m")
with col2:
    st.metric("Wing Area (S)", f"{wing_area} m²")
    st.metric("Total Wing Span (b)", f"{wing_span} m")
with col3:
    st.metric("Horizontal Tail Area", f"{s_ht} m²")
    st.metric("Vertical Tail Area", f"{s_vt} m²")

# Tabular structural breakdowns for clarity
tab1, tab2, tab3 = st.tabs(["📐 Control Surfaces", "⚙️ Landing Gear Sizing", "📖 Geometry Reference"])

with tab1:
    st.write("### Control Surface Dimensions")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write("**Ailerons (Roll Control)**")
        st.write(f"• Span: {b_a} m")
        st.write(f"• Chord: {c_a} m")
    with c2:
        st.write("**Rudder (Yaw Control)**")
        st.write(f"• Span: {b_r} m")
        st.write(f"• Chord: {c_r} m")
    with c3:
        st.write("**Elevators (Pitch Control)**")
        st.write(f"• Span: {b_e} m")
        st.write(f"• Chord: {c_e} m")

with tab2:
    st.write("### Recommended Tire Specifications")
    col_gear1, col_gear2 = st.columns(2)
    with col_gear1:
        st.write("**Main Landing Gear (Per Wheel)**")
        st.write(f"• Wheel Diameter: {main_gear_diameter} cm")
        st.write(f"• Wheel Width: {main_gear_width} cm")
    with col_gear2:
        st.write("**Nose Landing Gear (Per Wheel)**")
        st.write(f"• Wheel Diameter: {nose_gear_diameter} cm")
        st.write(f"• Wheel Width: {nose_gear_width} cm")

with tab3:
    st.write("### Calculated Aerodynamic Baselines")
    st.write(f"• Mean Aerodynamic Chord (MAC): **{mean_aerodynamic_chord} m**")
    st.write(f"• Root Chord: **{root_chord} m**")
    st.write(f"• Assumed Aspect Ratio: **{aspect_ratio}**")
    st.write(f"• Automatically Allocated Crew Count: **{num_crew} personnel**")
