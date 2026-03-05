import streamlit as st
import requests
import json

# 1. Setup the UI Page
st.set_page_config(page_title="Miracle Analyst AI", page_icon="📊")
st.title("📊 Miracle Analyst AI")

# 2. Your Definitive Backend URL
# Based on your Swagger screenshot for the POST /run endpoint
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
            # THE PAYLOAD: Matches the "Run Agent" schema exactly
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
            
            # --- ERROR HANDLING FOR NON-JSON RESPONSES ---
            if response.status_code != 200:
                # If server returns HTML error or 404, this prevents the "Expecting value" crash
                error_msg = f"**Server Error {response.status_code}:** {response.text}"
                message_placeholder.error(error_msg)
            
            elif response.text:
                try:
                    data = response.json()
                    
                    # Extracting answer from the 'events' list
                    events = data.get("events", [])
                    ai_answer = ""

                    if events:
                        # Search for the most recent text response in content.parts
                        for event in reversed(events):
                            parts = event.get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                ai_answer = parts[0]["text"]
                                break
                    
                    if not ai_answer:
                        ai_answer = "The agent processed the request but did not return a text response."

                    message_placeholder.markdown(ai_answer)
                    st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                
                except Exception as json_err:
                    message_placeholder.error(f"Failed to parse JSON. Raw Response: {response.text}")
            else:
                message_placeholder.error("Server sent an empty response.")
                
        except Exception as e:
            message_placeholder.error(f"Connection failed: {e}")
