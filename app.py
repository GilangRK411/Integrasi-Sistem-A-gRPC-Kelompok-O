import streamlit as st
from client.client import ChatClient
import time
import pandas as pd

# Inisialisasi client gRPC
client = ChatClient()

# Konfigurasi halaman
st.set_page_config(page_title="gRPC Chat App", layout="wide")
st.title("🛰️ gRPC Chat App")

# Sidebar
mode = st.sidebar.selectbox(
    "Select Chat Mode",
    ["Unary", "Server Streaming", "Client Streaming", "Bidirectional Streaming"]
)
user = st.sidebar.text_input("Your Name", "User1")
room = st.sidebar.text_input("Chat Room", f"{mode} Room")

# Reset histori
if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = []

# Inisialisasi histori
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mode: Unary
if mode == "Unary":
    st.subheader("💬 Unary RPC Chat")

    user_message = st.chat_input("Type your message...")
    if user_message:
        with st.chat_message(user):
            st.markdown(user_message)
        with st.spinner("Sending message..."):
            response, latency = client.unary_chat(room, user, user_message)
        with st.chat_message("Server"):
            st.markdown(response.message)

        st.session_state.chat_history.append({
            "mode": mode,
            "user": user,
            "message": user_message,
            "response": response.message,
            "latency": latency
        })

# Mode: Server Streaming
elif mode == "Server Streaming":
    st.subheader("📡 Server Streaming RPC Chat")

    user_message = st.chat_input("Type your message to start streaming...")
    if user_message:
        with st.chat_message(user):
            st.markdown(user_message)
        with st.spinner("Receiving stream..."):
            responses, latency, total_time = client.server_streaming_chat(room, user, user_message)
        for res in responses:
            with st.chat_message("Server"):
                st.markdown(f"{res.user}: {res.message}")
        st.info(f"First response latency: {latency:.2f} ms")
        st.info(f"Total streaming time: {total_time:.2f} ms")

        st.session_state.chat_history.append({
            "mode": mode,
            "user": user,
            "message": user_message,
            "response": "\n".join([r.message for r in responses]),
            "latency": total_time
        })

# Mode: Client Streaming
elif mode == "Client Streaming":
    st.subheader("📥 Client Streaming RPC Chat")

    default_text = "Hello Server\nThis is message 2\nAnd another one"
    user_message = st.chat_input("Send all messages at once (separated by \\n)", key="client_stream_input")
    if user_message:
        messages = user_message.strip().split("\n")
        with st.chat_message(user):
            for msg in messages:
                st.markdown(msg)
        with st.spinner("Sending message stream..."):
            response, latency = client.client_streaming_chat(room, user, messages)
        with st.chat_message("Server"):
            st.markdown(response.message)
        st.info(f"Total time: {latency:.2f} ms")
        st.info(f"Average latency per message: {latency/len(messages):.2f} ms")

        st.session_state.chat_history.append({
            "mode": mode,
            "user": user,
            "message": "\n".join(messages),
            "response": response.message,
            "latency": latency
        })

# Mode: Bidirectional Streaming
elif mode == "Bidirectional Streaming":
    st.subheader("🔄 Bidirectional Streaming RPC Chat")

    user_message = st.chat_input("Send multiple messages (separated by \\n)")
    if user_message:
        messages = user_message.strip().split("\n")
        with st.chat_message(user):
            for msg in messages:
                st.markdown(msg)
        with st.spinner("Chatting..."):
            responses, latency, total_time = client.bidirectional_chat(room, user, messages)
        for i, response in enumerate(responses):
            with st.chat_message("Server"):
                st.markdown(response.message)
        st.info(f"First response latency: {latency:.2f} ms")
        st.info(f"Total chat time: {total_time:.2f} ms")

        st.session_state.chat_history.append({
            "mode": mode,
            "user": user,
            "message": "\n".join(messages),
            "response": "\n".join([r.message for r in responses]),
            "latency": total_time
        })

# Tampilkan histori chat
if st.session_state.chat_history:
    st.divider()
    st.subheader("🕘 Chat History")
    df = pd.DataFrame(st.session_state.chat_history)
    st.dataframe(df)
