import streamlit as st
import os
import json

# Path to chat folder
CHAT_DIR = "chat"

st.title("💬 Chatbot")
st.caption("🚀 Chatbot")

# Ensure chat directory exists
if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

# Load chats into session state if not already loaded
if "chats" not in st.session_state:
    st.session_state.chats = {}
    for filename in os.listdir(CHAT_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CHAT_DIR, filename), "r", encoding="utf-8") as f:
                chat_data = json.load(f)
                st.session_state.chats[chat_data["id"]] = chat_data


# Function to save chat
def save_chat(chat_id, chat_data):
    with open(os.path.join(CHAT_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)


# List of existing chat names
chat_names = list(st.session_state.chats.keys())

# Sidebar for chat selection
st.sidebar.header("Select or Create Chat")
selected_chat = st.sidebar.selectbox(
    "Choose an existing chat or create a new one",
    ["Create New Chat"] + chat_names
)

# Handle chat creation or selection
if selected_chat == "Create New Chat":
    chat_name = st.sidebar.text_input("Enter new chat name")
    if chat_name:
        chat_id = f"chat_{chat_name}"
        if chat_id not in st.session_state.chats:
            new_chat = {"id": chat_id, "messages": []}
            st.session_state.chats[chat_id] = new_chat
            save_chat(chat_id, new_chat)
            st.success(f"Chat '{chat_name}' created successfully!")
        else:
            st.warning(f"Chat '{chat_name}' already exists.")
else:
    # Load selected chat data
    chat_id = selected_chat
    chat_data = st.session_state.chats[chat_id]
    messages = chat_data["messages"]

    # Display chat history only if a chat is selected
    if messages:
        st.write("### Chat History")
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            with st.chat_message(role):
                st.write(content)
                # Display links if available
                if "links" in msg:
                    for link in msg["links"]:
                        st.markdown(f"[{link['text']}]({link['url']})")

    # Handle new user input
    prompt = st.chat_input("Enter your message")
    if prompt:
        user_message = {"role": "user", "content": prompt}
        messages.append(user_message)
        with st.chat_message("user"):
            st.write(prompt)

        # Placeholder response logic
        assistant_content = f"Response to: {prompt}"
        assistant_links = [
            {"text": "Example Link 1", "url": "https://example.com/1"},
            {"text": "Example Link 2", "url": "https://example.com/2"}
        ]
        assistant_message = {"role": "assistant", "content": assistant_content, "links": assistant_links}

        messages.append(assistant_message)
        with st.chat_message("assistant"):
            st.write(assistant_content)
            # Display links for assistant's response
            for link in assistant_links:
                st.markdown(f"[{link['text']}]({link['url']})")

        # Update session state and save chat
        st.session_state.chats[chat_id]["messages"] = messages
        save_chat(chat_id, chat_data)
