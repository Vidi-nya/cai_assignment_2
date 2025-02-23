import streamlit as st
import random
import time

# Dummy API Call
def dummy_api_call(query):
    """Simulates an API call and returns a dummy answer with a confidence score."""
    time.sleep(2.5)  # Simulate processing delay
    dummy_answers = [
        "The company's revenue increased by 20% last year.",
        "The net profit margin showed a decline due to rising expenses.",
        "The balance sheet indicates strong liquidity ratios.",
        "The company's debt-to-equity ratio improved significantly."
    ]
    answer = random.choice(dummy_answers)
    confidence = round(random.uniform(0.6, 0.95), 2)
    return answer, confidence

# Initialize Session State for Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "loading" not in st.session_state:
    st.session_state.loading = False

# Layout and Title
st.title("Financial RAG Chat Assistant")

# Display Chat History
for chat in st.session_state.chat_history:
    # st.markdown(f"**You:** {chat['question']}")
    # st.markdown(f"**Assistant:** {chat['answer']}")
    # User's query on the right
    st.markdown(
        f"""
        <div style='text-align: right; max-width: 75%; float: right; clear: both;'>
            <div style='font-size: 13px; color: #b2aca2; margin: 0 10px;'>You</div>
            <div style='background-color: #32500a; padding: 10px; border-radius: 10px; 
                        box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);'>
                {chat['question']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Assistant's label and response on the left
    if chat["answer"] is not None:
        st.markdown(
            f"""
            <div style='text-align: left; max-width: 75%; float: left; clear: both;'>
                <div style='font-size: 13px; color: #b2aca2; margin: 0 10px;'>Assistant</div>
                <div style='background-color: #26292b; padding: 10px; border-radius: 10px; 
                        box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);'>
                    {chat['answer']}
                </div>
            </div>
            """,
        unsafe_allow_html=True
    )
    
    # Confidence Score (Below the answer)
    if chat["confidence"] is not None:
        st.markdown(
            f"<div style='clear: both; color: #b2aca2; font-size: 13px;'>Confidence: {chat['confidence'] * 100}%</div>",
            unsafe_allow_html=True
        )
        st.divider()  # Adds a visual divider between Q&A pairs

# User Input (Always at the Bottom)
user_input = st.chat_input("Ask a financial question...")

# If user inputs a question
if user_input:
    # Add question to chat history and show loading animation
    st.session_state.chat_history.append({
        "question": user_input,
        "answer": None,  # Placeholder for the answer
        "confidence": None  # Placeholder for the confidence score
    })
    st.session_state.loading = True
    st.rerun()  # Refresh to display the question immediately

# If loading, simulate the API call and update the last question's answer
if st.session_state.loading:
    with st.spinner("Fetching answer..."):
        # Get the last question
        last_question = st.session_state.chat_history[-1]["question"]

        # Dummy API Call
        answer, confidence = dummy_api_call(last_question)

        # Update the last chat history item with the answer and confidence
        st.session_state.chat_history[-1]["answer"] = answer
        st.session_state.chat_history[-1]["confidence"] = confidence

    # Stop loading and refresh to show the answer
    st.session_state.loading = False
    st.rerun()
