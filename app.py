import streamlit as st
import requests
import json

# 1. Setup the UI Page
st.set_page_config(page_title="Miracle Analyst AI", page_icon="📊")
st.title("📊 Miracle Analyst AI")

# 2. Your Deployed Backend URL
# We use the /run endpoint to ensure the agent actually executes its logic
API_URL = "https://adk-default-service-name-43463140793.us-east1.run.app/apps/ecommerce_agent/users/swarna/sessions/chat_01"
# 3. Setup Chat Memory (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Cloud Data Analyst. What would you like to know about the `thelook_ecommerce` dataset?"}
    ]

# 4. Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. The Input Box
if prompt := st.chat_input("Ask about top product categories..."):
    # Show user message in UI
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 *Querying BigQuery via Cloud Run...*")
        
        try:
            # Send the request to your Cloud Run Backend
            response = requests.post(
                API_URL, 
                json={"text": prompt},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # DATA EXTRACTION LOGIC:
                # The agent stores its final answer in the 'events' list.
                # We look for the last 'text' event to show the user.
                events = data.get("events", [])
                
                if events:
                    # Find the last event that contains text (the AI's answer)
                    ai_answer = ""
                    for event in reversed(events):
                        if "text" in event:
                            ai_answer = event["text"]
                            break
                    
                    if not ai_answer:
                        ai_answer = "I processed the data, but didn't generate a text summary. Check the raw logs."
                else:
                    ai_answer = "The agent received your message but hasn't generated an event yet. Please try a more specific question."

                # Update the UI with the actual answer
                message_placeholder.markdown(ai_answer)
                st.session_state.messages.append({"role": "assistant", "content": ai_answer})
                
            elif response.status_code == 404:
                message_placeholder.error("Backend Error: 404. Please check if the API URL and Agent Name are correct.")
            else:
                message_placeholder.error(f"Backend Error: {response.status_code}")
                
        except Exception as e:
            message_placeholder.error(f"Connection failed: {e}")
