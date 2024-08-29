import hmac
import streamlit as st

def login():
    """Returns `True` if the user had a correct password."""
    

    
    def login_form():
        """Form with widgets to collect user information"""
        st.html("<div style='text-align: center'> <H2> Daytonna - Mini Payroll System</H2> </div>")
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

        col1, col2, col3 = st.columns(3)

        with col2:
            st.page_link("pages/view_payroll.py",label="📓Check Slip Gaji Bayangan")
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
            st.error("😕 User not known or password incorrect")

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    return False