import streamlit as st


def wyoq():
    st.title("Write your own query")
    st.write("There are 3 ways to access the graph database to write and execute new queries.")

    with st.expander("Neo4j console"):
        st.write("""
        You can write your queries directly on the Neo4j console that provides the graphical interface from which all the images in the Intro section are taken.

    To access it, go to the link
        """)
        st.code("https://browser.neo4j.io/")
        st.write("""
        And enter the following credentials
        """)
        st.code("""
        connect_url = neo4j+s://00e145e7.databases.neo4j.io:7687
username = soccer_analytics
password = night-candle-miracle-nickel-declare-32
        """)
        st.warning("The free version does not allow you to limit a user to doing only queries. Please do not perform any editing operations. All operations are logged, if suspicious operations are noticed the database will be deactivated.")

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
