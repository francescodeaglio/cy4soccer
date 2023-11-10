import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


def pca_page():
    """
    Streamlit wrapper
    """
    st.title("PCA")

    st.write(
        """Data has already been preprocessed to speedup loading. The table was obtained as follows:

1) for each team, the number of passes per pattern made during the entire competition was counted.

2) the number of passes was divided by the number of matches played in order to take into account that different teams played different numbers of matches (this was not necessary in La Liga data as each team played 38 matches).

3) each value was normalized (i.e. removed the average of the pattern and divided by the standard deviation)"""
    )

    fp = open(os.path.join(os.curdir, "data", "pca", "pca_table_new.json"), "r")

    data = json.load(fp)

    df = pd.DataFrame(data)

    with st.expander("See the data"):
        st.table(df)

    # st.subheader("Original dimensions, before PCA")

    features = ["ABAB", "ABAC", "ABCB", "ABCA", "ABCD"]

    fig = px.scatter_matrix(
        df, dimensions=features, color=df.index, labels={"index": "Team"}
    )
    fig.update_traces(diagonal_visible=True)
    fig.update_layout(
        title={
            "text": "Original dimensions, before PCA",
            "y": 0.95,  # new
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",  # new
        }
    )
    st.plotly_chart(fig)

    # st.subheader("First 2 principal components and 4-means")

    pca = PCA(n_components=2)
    components = pca.fit_transform(df)

    model = KMeans(n_clusters=4)

    # Fit model to samples
    model.fit(components)

    fig = px.scatter(
        x=components[:, 0],
        y=components[:, 1],
        color=model.labels_,
        text=df.index,
        labels={
            "x": "First Principal Component",
            "y": "Second Principal Component",
        },
    )
    fig.update_traces(
        textposition="middle right",
        showlegend=False,
        marker_coloraxis=None,
        marker=dict(size=12),
        textfont_size=8,
    )

    fig.update_layout(
        title={
            "text": "First 2 principal components and 4-mean clustering",
            "y": 0.95,  # new
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",  # new
        }
    )
    st.plotly_chart(fig)
