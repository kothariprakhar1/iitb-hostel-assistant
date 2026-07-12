import streamlit as st
from rag_chain import answer_question

st.set_page_config(page_title="IITB Hostel & Campus Life Assistant", page_icon="🏠")

st.title("🏠 IITB Hostel & Campus Life Assistant")
st.caption("Ask me anything about IITB hostel rules, mess, facilities, or allotment. "
           "I only answer from real institute documents — if I don't know, I'll say so.")

# Keep chat history across interactions
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 Sources used"):
                for s in msg["sources"]:
                    st.write(f"- **{s['source']}** (chunk {s['chunk_index']}, distance={s['distance']:.3f})")

# Chat input box
query = st.chat_input("Ask a question about IITB hostel life...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching hostel documents..."):
            result = answer_question(query)

        st.write(result["answer"])

        grounded_label = "✅ Grounded" if result["grounded"] else "⚠️ Not grounded"
        st.caption(grounded_label)

        if result["sources"]:
            with st.expander("📄 Sources used"):
                for s in result["sources"]:
                    st.write(f"- **{s['source']}** (chunk {s['chunk_index']}, distance={s['distance']:.3f})")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })