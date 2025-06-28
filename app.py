import streamlit as st
from openai import OpenAI
import googlemaps

from weather import get_flood_risk
from earthquake import get_earthquake_risk
# from fire import get_fire_risk
from preparedness import generate_preparation_checklist

# Setup OpenAI API client
openai_client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

# Setup Google Maps client
gmaps_client = googlemaps.Client(
    key=st.secrets["GOOGLE_MAPS_API_KEY"],
)

if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = {
        "household_name": "",
        "address": "",
        "family_members": [],
        "flood_risk": {},
        "earthquake_risk": {},
    }

if "preparedness_checklist" not in st.session_state:
    st.session_state["preparedness_checklist"] = {}


if "show_family_members" not in st.session_state:
    st.session_state["show_family_members"] = False

if "add_family_member" not in st.session_state:
    st.session_state["add_family_member"] = False

def main():
    # Sidebar
    # Sidebar contains the user profile
    with st.sidebar:
        st.title("User Profile")
        st.session_state["user_profile"]["household_name"] = st.text_input("Household Name", value=st.session_state.user_profile["household_name"])
        st.session_state["user_profile"]["address"] = st.text_input("Address", value=st.session_state.user_profile["address"])
        
        # Family Members
        st.subheader("Family Members")
        
        # Show add family member form when + button is clicked
        if st.button("Add"):
            st.session_state["add_family_member"] = True

        # Add a new family member
        name = st.text_input("Name", disabled=not st.session_state["add_family_member"])
        contact_number = st.text_input("Contact Number", disabled=not st.session_state["add_family_member"])
        email = st.text_input("Email", disabled=not st.session_state["add_family_member"])
        age = st.text_input("Age", disabled=not st.session_state["add_family_member"])
        mobility_needs = st.text_input("Mobility Needs", disabled=not st.session_state["add_family_member"])
        medication = st.text_input("Medication", disabled=not st.session_state["add_family_member"])

        if st.button("Add Family Member", disabled=not st.session_state["add_family_member"]):
            st.session_state["add_family_member"] = False

            st.session_state["user_profile"]["family_members"].append({
                "name": name,
                "contact_number": contact_number,
                "email": email,
                "age": age,
                "mobility_needs": mobility_needs,
                "medication": medication
            })


        # Show family members
        st.session_state["show_family_members"] = st.checkbox("Show Family Members", value=False)
        if st.session_state["show_family_members"]:
            for member in st.session_state["user_profile"]["family_members"]:
                st.write(f"Name: {member['name']}")
                st.write(f"Contact Number: {member['contact_number']}")
                st.write(f"Email: {member['email']}")
                st.write(f"Age: {member['age']}")
                st.write(f"Mobility Needs: {member['mobility_needs']}")
                st.write(f"Medication: {member['medication']}")
                st.write("---")


    # Main Content Area
    st.title("Disaster Preparedness Assistant")
    
    # Risk Dashboard
    st.subheader("Risk Dashboard")

    if st.button("Analyze Risk"):
        # Fetch and display risk data
        flood_risk = get_flood_risk(
            openai_client,
            gmaps_client,
            st.session_state["user_profile"]["address"]
        )
        # Get flood risk number
        flood_risk_rating = flood_risk.split("\n")[0].split(":")[1].strip()
        flood_risk_explanation = flood_risk.split("\n")[1].split(":")[1].strip()
        st.session_state["user_profile"]["flood_risk"] = {
            "rating": flood_risk_rating,
            "explanation": flood_risk_explanation
        }
        st.write(f"Flood Risk Rating: {flood_risk_rating}")
        st.write(f"Flood Risk Explanation: {flood_risk_explanation}")

        earthquake_risk = get_earthquake_risk(
            openai_client,
            gmaps_client,
            st.session_state["user_profile"]["address"]
        )
        # Get earthquake risk number
        earthquake_risk_rating = earthquake_risk.split("\n")[0].split(":")[1].strip()
        earthquake_risk_explanation = earthquake_risk.split("\n")[1].split(":")[1].strip()
        st.session_state["user_profile"]["earthquake_risk"] = {
                "rating": earthquake_risk_rating,
                "explanation": earthquake_risk_explanation
        }
        st.write(f"Earthquake Risk Rating: {earthquake_risk_rating}")
        st.write(f"Earthquake Risk Explanation: {earthquake_risk_explanation}")

        # fire_risk = get_fire_risk(
        #     openai_client,
        #     gmaps_client,
        #     st.session_state["user_profile"]["address"]
        # )
        # st.write(f"{fire_risk}")

    # Generate Preparation Checklist
    st.subheader("Preparation Checklist")
    if st.button("Generate Checklist"):
        checklist = generate_preparation_checklist(
            openai_client,
            st.session_state["user_profile"]
        )

        for task in checklist:
            st.session_state["preparedness_checklist"][task] = False

    # Show preparedness checklist as list of checkboxes
    if st.session_state["preparedness_checklist"]:
        st.write("Preparedness Checklist:")
        for task, is_done in st.session_state["preparedness_checklist"].items():
            is_done = st.checkbox(task, value=is_done)

    print("Hello from disaster-preparedness-assistant!")


if __name__ == "__main__":
    main()
