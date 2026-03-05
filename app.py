import streamlit as st
import requests
import json

# 1. Setup the UI Page
st.set_page_config(page_title="Miracle Analyst AI", page_icon="📊")
st.title("📊 Miracle Analyst AI")

# 2. Your Deployed Backend URL
API_URL = "https://adk-default-service-name-43463140793.us-east1.run.app/apps/ecommerce_agent/users/swarna/sessions/chat_01"
# 3. Setup Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Cloud Data Analyst. What would you like to know about bigquery-public-data.thelook_ecommerce dataset?"}
    ]

# 4. Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The Input Box
if prompt := st.chat_input("Ask about top product categories..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Calling Cloud Run API...")
        
        try:
            # ---------------------------------------------------------
            # THE BRIDGE: Python talks to Cloud Run (No CORS Error!)
            # ---------------------------------------------------------
            response = requests.post(
                API_URL, 
                json={"text": prompt},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # For the demo, we will cleanly print the JSON response returned from your backend
                formatted_response = f"**Success! Data received from backend:**\n```json\n{json.dumps(data, indent=2)}\n```"
                
                message_placeholder.markdown(formatted_response)
                st.session_state.messages.append({"role": "assistant", "content": formatted_response})
            else:
                error_msg = f"Backend Error: {response.status_code}"
                message_placeholder.markdown(error_msg)
                
        except Exception as e:
            message_placeholder.markdown(f"Connection failed: {e}")
