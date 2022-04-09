import streamlit as st
from intro import intro
from pattern_finder import pattern_finder
from pcapage import pca_page
from sunburst import sunburst
from heatmaps import heatmap
from writeYourOwnQuery import wyoq
from arrows import arrows
if __name__ == '__main__':
    st.sidebar.title("Cy4soccer")
    page = st.sidebar.selectbox("Select the page", ["Intro", "Pattern Finder", "Sunburst diagram", "PCA", "Heatmap", "Arrows", "Write you own query", "Credits"])

    if page == "Intro":
        intro()

    if page == "Arrows":
        arrows()
    
    if page == "Heatmap":
        heatmap()

    if page == "Write you own query":
        wyoq()

    if page == "Pattern Finder":
        pattern_finder()

    if page == "Sunburst diagram":
        sunburst()

    if page == "Credits":
        st.title("Credits")
        st.write("""
        The tool has been developed by Francesco Deaglio. Feel free to use the database and the various tools as you wish but mention the source. 

If you want to collaborate, have ideas or doubts write me at fdeaglio@ethz.ch and I will be happy to answer. 

All images were taken from Neo4j, if you want to have access to them write me and I'll send you the credentials (or a dump of the database if you want to work on your own).

Thanks to Filippo Costa for hosting and precious help in the development.

To see the code you can refer to my github page www.github.com/francescodeaglio/cy4soccer where you can also find a notebook with the preprocessing, done in Jsoniq/Rumble.
        """)

    if page == "PCA":
        pca_page()
