import streamlit as st
import plotly.express as px
import pandas as pd
import hvplot.pandas
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
from dotenv import load_dotenv
import holoviews as hv

hv.extension("bokeh", logo=False)
from config import api_key
import holoviews.plotting.bokeh

# Read the Mapbox API key
load_dotenv()
map_box_api = api_key
px.set_mapbox_access_token(map_box_api)

file_path = Path("Data/sfo_neighborhoods_census_data.csv")
sfo_data = pd.read_csv(file_path, index_col="year")
file_path = Path("Data/neighborhoods_coordinates.csv")
coord_data = pd.read_csv(file_path)
coord_data.columns = ["neighborhood", "Lat", "Lon"]
avg_housing_units = sfo_data.groupby("year")["housing_units"].mean()
avg_housing_units = pd.DataFrame(avg_housing_units).reset_index()

avg_sale_price = sfo_data.groupby("year")["sale_price_sqr_foot"].mean()
avg_sale_price = pd.DataFrame(avg_sale_price).reset_index()
avg_sale_price.round(2)

avg_rent = sfo_data.groupby("year")["gross_rent"].mean()
avg_rent = pd.DataFrame(avg_rent).reset_index()

nbhd_means = sfo_data.groupby(["year", "neighborhood"])
nbhd_means = nbhd_means.mean().reset_index()
nbhd_means.round(2)

top_10_prices = (
    nbhd_means.groupby("neighborhood")["sale_price_sqr_foot"].mean().reset_index()
)
top_10_prices = top_10_prices.sort_values(
    by="sale_price_sqr_foot", ascending=False
).head(10)

rent_means = nbhd_means.groupby("neighborhood")["gross_rent"].mean().reset_index()
coord_rent = pd.merge(coord_data, rent_means, on="neighborhood", how="inner")

df_expensive_neighborhoods_per_year = sfo_data[
    sfo_data["neighborhood"].isin(top_10_prices["neighborhood"])
]
df_expensive_neighborhoods_per_year = (
    df_expensive_neighborhoods_per_year.groupby("neighborhood").mean().reset_index()
)
df_expensive_neighborhoods_per_year = df_expensive_neighborhoods_per_year.round(2)


# Define Panel Visualization Functions
def housing_units_per_year():
    """Housing Units Per Year."""

    fig, ax = plt.subplots(figsize=(8, 4.5))
    p = sns.barplot(
        data=avg_housing_units, x="year", y="housing_units", color="olivedrab", ax=ax
    )
    for index, row in avg_housing_units.iterrows():
        ax.text(
            index,
            row["housing_units"],
            int(row["housing_units"]),
            ha="center",
            va="bottom",
            fontsize=7,
        )
    plt.title("Housing Units in San Francisco from 2010 to 2016\n", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Housing Units")
    ax.set_ylim(370000, 385000)
    st.pyplot(fig)


def average_gross_rent():
    """Average Gross Rent in San Francisco Per Year."""

    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.lineplot(data=avg_rent, x="year", y="gross_rent", color="midnightblue", ax=ax)
    plt.title("Average Gross Rent from 2010 to 2016\n", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Rent (USD)")
    st.pyplot(fig)


def average_sales_price():
    """Average Sales Price Per Year."""

    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.lineplot(data=avg_sale_price, x="year", y="sale_price_sqr_foot", color="indigo")
    plt.title("Average Price per SqFt from 2010 to 2016\n", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Price (USD)")
    st.pyplot(fig)


def average_price_by_neighborhood():
    """Average Prices by Neighborhood."""

    neighborhood_list = nbhd_means["neighborhood"].unique().tolist()

    selected_neighborhood = st.selectbox("Select a Neighborhood", neighborhood_list)

    subset = nbhd_means[nbhd_means["neighborhood"] == selected_neighborhood]

    plot = subset.hvplot.line(y="sale_price_sqr_foot", x="year").opts(
        title=f"Average Price Per Sq Ft in {selected_neighborhood}",
        xlabel="Year",
        ylabel="Price per Sq Ft",
    )

    bokeh_plot = hv.render(plot)
    st.bokeh_chart(bokeh_plot)


def average_rent_by_neighborhood():
    """Average Rent by Neighborhood."""

    neighborhood_list = nbhd_means["neighborhood"].unique().tolist()

    selected_neighborhood = st.selectbox("Select a Neighborhood", neighborhood_list)

    subset = nbhd_means[nbhd_means["neighborhood"] == selected_neighborhood]

    plot = subset.hvplot.line(y="gross_rent", x="year").opts(
        title=f"Average Rent in {selected_neighborhood}",
        xlabel="Year",
        ylabel="Rent (USD)",
    )

    bokeh_plot = hv.render(plot)
    st.bokeh_chart(bokeh_plot)


def top_most_expensive_neighborhoods():
    """Top 10 Most Expensive Neighborhoods."""

    fig, ax = plt.subplots(figsize=(20, 12))
    p = sns.barplot(
        data=top_10_prices,
        x="neighborhood",
        y="sale_price_sqr_foot",
        color="olivedrab",
        ax=ax,
    )
    plt.title("Top 10 Most Expensive Neighborhoods (On Average)\n", fontsize=20)
    plt.xlabel("Neighborhoods", fontsize=20)
    plt.ylabel("Average Sale Price per Square Foot", fontsize=20)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=18)
    plt.tight_layout()
    st.pyplot(fig)


def most_expensive_neighborhoods_rent_sales():
    """Comparison of Rent and Sales Prices of Most Expensive Neighborhoods."""


def grouped_bars(data, neighborhood):
    subset = data[data["neighborhood"] == neighborhood]

    bars1 = hv.Bars(
        subset, kdims=["year"], vdims=["gross_rent"], label="Gross Rent"
    ).opts(color="darkslategray", width=800, height=600, tools=["hover"])

    bars2 = hv.Bars(
        subset, kdims=["year"], vdims=["sale_price_sqr_foot"], label="Price per Sq Ft"
    ).opts(color="lightslategray", width=800, height=600, tools=["hover"])

    return (bars1 * bars2).opts(
        title=f"Rent vs. Price per Sq Ft in {neighborhood}",
        xlabel="Year",
        ylabel="Value",
        legend_position="top_left",
    )


def display_grouped_bars(data):
    # Dropdown for neighborhood selection
    neighborhood_list = data["neighborhood"].unique().tolist()
    selected_neighborhood = st.selectbox("Select a Neighborhood", neighborhood_list)

    # Generate plot for the selected neighborhood
    plot = grouped_bars(data, selected_neighborhood)

    # Render and display the plot
    st_bokeh = hv.render(plot)
    st.bokeh_chart(st_bokeh)


st.title("San Francisco Real Estate Analysis")


def mapbox():
    px.set_mapbox_access_token(api_key)

    fig = px.scatter_mapbox(
        coord_rent,
        lat="Lat",
        lon="Lon",
        color="gross_rent",
        size="gross_rent",
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=15,
        zoom=10,
    )

    st.plotly_chart(fig)


def parallel_cat():
    fig_parallel = px.parallel_categories(
        df_expensive_neighborhoods_per_year,
        dimensions=[
            "neighborhood",
            "sale_price_sqr_foot",
            "housing_units",
            "gross_rent",
        ],
        color="sale_price_sqr_foot",
        color_continuous_scale=px.colors.sequential.Inferno,
        labels={
            "sale_price_sqr_foot": "Sale Price Per Square Foot",
            "housing_units": "Housing Units",
            "gross_rent": "Gross Rent",
            "neighborhood": "Neighborhood",
        },
    )
    fig_parallel.update_layout(
        width=1000, height=500, margin=dict(t=50, l=100, b=50, r=50)
    )
    st.plotly_chart(fig_parallel)


def parallel_coord():
    fig_parallel = px.parallel_coordinates(
        df_expensive_neighborhoods_per_year,
        color="sale_price_sqr_foot",
        labels={
            "sale_price_sqr_foot": "Sale Price Per Square Foot",
            "housing_units": "Housing Units",
            "gross_rent": "Gross Rent",
        },
    )
    fig_parallel.update_layout(
        width=1000, height=500, margin=dict(t=50, l=100, b=50, r=50)
    )
    st.plotly_chart(fig_parallel)


# Tabs for each plot
tabs = [
    "Housing Units Per Year",
    "Average Gross Rent",
    "Average Sales Price",
    "Average Price by Neighborhood",
    "Average Rent by Neighborhood",
    "Top 10 Most Expensive Neighborhoods",
    "Comparison of Rent and Sales Prices",
    "Scatter Mapbox",
    "Parallel Categories Plot",
    "Parallel Coordinates Plot",
]

selected_tab = st.selectbox("Choose a Visualization", tabs)

if selected_tab == "Housing Units Per Year":
    housing_units_per_year()

elif selected_tab == "Average Gross Rent":
    average_gross_rent()

elif selected_tab == "Average Sales Price":
    average_sales_price()

elif selected_tab == "Average Price by Neighborhood":
    average_price_by_neighborhood()

elif selected_tab == "Average Rent by Neighborhood":
    average_rent_by_neighborhood()

elif selected_tab == "Top 10 Most Expensive Neighborhoods":
    top_most_expensive_neighborhoods()

elif selected_tab == "Comparison of Rent and Sales Prices":
    st.write("## Comparison of Rent and Sales Prices by Year, By Neighborhood")
    display_grouped_bars(nbhd_means)

elif selected_tab == "Scatter Mapbox":
    mapbox()

elif selected_tab == "Parallel Categories Plot":
    parallel_cat()

elif selected_tab == "Parallel Coordinates Plot":
    parallel_coord()
