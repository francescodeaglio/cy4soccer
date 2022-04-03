import streamlit as st
from intro import intro
from pattern_finder import pattern_finder
from cypher_box import cypher_box
from pcapage import pca_page

if __name__ == '__main__':
    st.sidebar.title("Cy4soccer")
    page = st.sidebar.selectbox("Select the page", ["Intro", "Pattern Finder", "Cypher", "PCA", "Credits"])

    if page == "Intro":
        intro()

    if page == "Pattern Finder":
        pattern_finder()

    if page == "Cypher":
        cypher_box()

    if page == "Credits":
        st.write("scrivi due cazzate")

    if page == "PCA":
        pca_page()