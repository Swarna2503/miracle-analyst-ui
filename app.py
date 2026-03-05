import streamlit as st
import requests
import json

# 1. Setup the UI Page
st.set_page_config(page_title="Miracle Analyst AI", page_icon="📊")
st.title("📊 Miracle Analyst AI")

# 2. Your Definitive Backend URL
# Based on your Swagger screenshot: POST /run
API_URL = "https://adk-default-service-name-43463140793.us-east1.run.app/run"

# 3. Setup Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Cloud Data Analyst. Ask me anything about the ecommerce dataset."}
    ]

# 4. Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The Input Box
if prompt := st.chat_input("Ex: List the tables in thelook_ecommerce"):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Querying BigQuery...*")
        
        try:
            # ---------------------------------------------------------
            # THE PAYLOAD: Matching your Swagger Schema exactly
            # ---------------------------------------------------------
            payload = {
                "appName": "ecommerce_agent",
                "userId": "swarna",
                "sessionId": "chat_01",
                "newMessage": {
                    "parts": [{"text": prompt}]
                }
            }
            
            response = requests.post(
                API_URL, 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # NAVIGATION LOGIC: 
                # We look into the 'events' list returned by the ADK
                events = data.get("events", [])
                ai_answer = ""

                if events:
                    # Search backwards for the most recent text response
                    for event in reversed(events):
                        # Look for content -> parts -> text structure from your schema
                        parts = event.get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            ai_answer = parts[0]["text"]
                            break
                
                if not ai_answer:
                    ai_answer = "I've processed the request, but no text response was generated. Please check the session state."

                message_placeholder.markdown(ai_answer)
                st.session_state.messages.append({"role": "assistant", "content": ai_answer})
            
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                message_placeholder.error(f"Backend Error {response.status_code}: {error_detail}")
                
        except Exception as e:
            message_placeholder.error(f"Connection failed: {e}")
