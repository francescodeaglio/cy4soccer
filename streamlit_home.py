import streamlit as st
from streamlit_pages.geovisualization import geovisualization
from streamlit_pages.intro import intro
from streamlit_pages.passagesonar import passagesonar
from streamlit_pages.pattern_finder import pattern_finder
from streamlit_pages.pca import pca_page
from streamlit_pages.sunburst_mongo import sunburst_mongo
from streamlit_pages.writeYourOwnQuery import wyoq
from streamlit_pages.pattern_positions import pattern_positions


if __name__ == '__main__':
    st.sidebar.title("Cy4soccer")
    page = st.sidebar.selectbox("Select the page",
                                ["Intro", "Pattern Finder", "Sunburst diagram", "Pattern positions", "Passing Sonar",
                                 "Geovisualization", "PCA", "Write your own query", "Credits"])

    if page == "Intro":
        intro()

    if page == "Passing Sonar":
        passagesonar()


    if page == "Pattern positions":
        pattern_positions()

    if page == "Write your own query":
        wyoq()

    if page == "Pattern Finder":
        pattern_finder()


    if page == "Sunburst diagram":
        sunburst_mongo()

    if page == "Geovisualization":
        geovisualization()

    if page == "PCA":
        pca_page()

    if page == "Credits":
        st.title("Credits")
        st.write("""
        The tool has been developed by Francesco Deaglio. Feel free to use the database and the various tools as you wish but mention the source. 

If you want to collaborate, have ideas or doubts write me at fdeaglio@ethz.ch and I will be happy to answer. 

All images were taken from Neo4j, if you want to have access to them write me and I'll send you the credentials (or a dump of the database if you want to work on your own).

Thanks to Filippo Costa for hosting and precious help in the development.

To see the code you can refer to my github page www.github.com/francescodeaglio/cy4soccer where you can also find a notebook with the preprocessing, done in Jsoniq/Rumble.
        """)



