import streamlit as st


if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = {
        "household_name": "",
        "address": "",
        "family_members": [],
        "risk_factors": [],
        "preparedness_level": "",
    }

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



    print("Hello from disaster-preparedness-assistant!")


if __name__ == "__main__":
    main()
