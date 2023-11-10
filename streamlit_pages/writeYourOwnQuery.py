import streamlit as st


def wyoq():
    """
    Streamlit wrapper
    """
    st.title("Write your own query")
    st.write("There are 3 ways to access the graph database to write and execute new queries.")

    with st.expander("Jupyter notebook"):
        st.write("""
        I created an example notebook with all the functions to access the database from python. You can download it and modify it to your liking. You can find the link on Github, in the section notebooks
        """)
        st.code("https://github.com/francescodeaglio/cy4soccer")

    with st.expander("Local database"):
        st.write("""
        You can download the database dump and load it into your own neo 4j installation (there is both an online version, Aura, and an offline version). 
You can use the rumble_preprocessing notebook to reproduce the loading or directly use the dump that you find at the following link
        """)
        st.code("https://polybox.ethz.ch/index.php/s/inIZZMX3XzoOSYA")
