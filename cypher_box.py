import streamlit as st

def cypher_box():
    st.title("Write your own query")
    query = st.text_input(label="Insert your query here", value="MATCH ")
    if st.button("Submit"):
        print(query)