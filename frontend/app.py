import streamlit as st
import requests
import os

# FastAPI backend URL (change if running on a different host)
FASTAPI_URL = "http://127.0.0.1:3002/chat"
UPLOAD_FOLDER = "./data_files" 
st.title("Labeler Codes with FastAPI Backend")

# Input fields for car details
st.header("Enter Label Code Details")
title = st.text_input("Label Code")
# st.header("Upload Data File (Optional - for Vector Store)")
# uploaded_file = st.file_uploader("Choose a CSV, PDF, or Excel file", type=["csv", "pdf", "xlsx", "xls"])


if st.button("Submit"):
   
    
    # uploaded_filename = None
    # if uploaded_file:
    #     try:
    #         file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    #         with open(file_path, "wb") as f:
    #             f.write(uploaded_file.getvalue())
    #         uploaded_filename = uploaded_file.name
    #         st.success(f"File '{uploaded_filename}' saved to '{UPLOAD_FOLDER}'")
    #     except Exception as e:
    #         st.error(f"Error saving file: {e}")

    payload = {
        "title": title,
#        "file": uploaded_filename  # Send the filename to the API
    }


    response = requests.post(FASTAPI_URL, json=payload,timeout=600)
   

    if response.status_code == 200:
        bot_response = response.json().get("response", "Error: No response received.")
    else:
        bot_response = "Error: Unable to reach the backend."

    st.subheader("Response")
    st.write(bot_response)