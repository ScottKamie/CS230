"""
Program Name: final_project--Scott_Kamieneski
Name: Scott Kamieneski
Class: CS 230 - 5
Date: 12/9/21

Data: Fortune_500_Corporate_Headquarters
URL:
Description: Use data file and packages to present information on user-friendly site.
Statement: I worked on and completed this project individually.
"""

# Import data editing, calculations, charting, mapping, and web packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st

# Names of US regions
northeast = ['NORTHEAST']
south = ['SOUTH']
midwest = ['MIDWEST']
west = ['WEST']
regions = ['NORTHEAST', 'SOUTH', 'MIDWEST', 'WEST']
regions_capitalize = [region.capitalize() for region in regions]

# List US regions
northeast_list = ['PA', 'NY', 'NJ', 'CT', 'RI', 'MA', 'VT', 'NH', 'ME']
south_list = ['TX', 'OK', 'AR', 'LA', 'MS', 'AL', 'TN', 'KY', 'GA', 'FL', 'SC', 'NC', 'VA', 'WV', 'DE', 'MD', 'DC']
midwest_list = ['ND', 'SD', 'NE', 'KS', 'MN', 'IA', 'MO', 'WI', 'IL', 'IN', 'MI', 'OH']
west_list = ['WA', 'OR', 'CA', 'AK', 'HI', 'NV', 'AZ', 'NM', 'UT', 'CO', 'ID', 'WY', 'MT']
regions_list = [northeast_list, south_list, midwest_list, west_list]
regions_list.sort()
for region in regions_list:
    region.sort()

# List US states
states_list = []
for region in regions_list:
    for state in region:
        states_list.append(state)
states_list.sort()


# Read + edit data
def read_file():
    # Read csv file
    df_companies = pd.read_csv("Fortune_500_Corporate_Headquarters.csv").set_index("OBJECTID")

    # Add region column to dataframe
    df_companies['REGION'] = ''
    for index, row in df_companies.iterrows():
        if df_companies.at[index, 'STATE'] in northeast_list:
            df_companies.at[index, 'REGION'] = 'NORTHEAST'
        elif df_companies.at[index, 'STATE'] in south_list:
            df_companies.at[index, 'REGION'] = 'SOUTH'
        elif df_companies.at[index, 'STATE'] in midwest_list:
            df_companies.at[index, 'REGION'] = 'MIDWEST'
        elif df_companies.at[index, 'STATE'] in west_list:
            df_companies.at[index, 'REGION'] = 'WEST'
    return df_companies


# CHART 1 + CHART 2: Filters
# Filter companies based on region
def filter_region(user_region):
    df_companies = read_file()
    df_companies = df_companies.loc[df_companies['REGION'].isin(user_region)]
    return df_companies


# Count frequency of companies in region filter
def count_companies_per_region(user_region):
    df_companies = filter_region(user_region)
    filtered_list = [df_companies.loc[df_companies['REGION'].isin([region])].shape[0] for region in regions]
    return filtered_list


# CHART 2: Filters
# Filter companies based on region and profit
def filter_region_profit(user_region, user_min_profit):
    df_companies = filter_region(user_region)
    df_companies = df_companies.loc[df_companies['PROFIT'] > user_min_profit]
    return df_companies


# List of company ranks in region/profit filter
def list_company_ranks(user_region, user_min_profit):
    df_companies = filter_region_profit(user_region, user_min_profit)
    company_ranks = []
    for index, row in df_companies.iterrows():
        company_ranks.append(df_companies.at[index, 'RANK'])
    return company_ranks


# List of company sizes (number of employees) in region/profit filter
def list_company_sizes(user_region, user_min_profit):
    df_companies = filter_region_profit(user_region, user_min_profit)
    company_sizes = []
    for index, row in df_companies.iterrows():
        company_sizes.append(df_companies.at[index, 'PROFIT'])
    return company_sizes


# Correlation coefficient in region/profit filter
def calculate_correlation(user_region, user_min_profit):
    xs = list_company_ranks(user_region, user_min_profit)
    ys = list_company_sizes(user_region, user_min_profit)
    correlation_matrix = np.corrcoef(xs, ys)
    correlation_list = []
    for row in correlation_matrix:
        for number in row:
            correlation_list.append(number)
    correlation = correlation_list[1]
    return correlation


# CHART 3: Filters
def filter_min_max_revenues(user_min_revenue=5000):
    df_companies = read_file()
    df_companies = df_companies.loc[df_companies['REVENUES'] > user_min_revenue]
    return df_companies


# Chart 1: Plot bar chart
def create_bar_chart(user_region=regions):
    plt.figure()

    xs = regions_capitalize
    ys = count_companies_per_region(user_region)

    plt.bar(xs, ys, width=0.5, color='g')

    for x in range(len(xs)):
        plt.text(x, ys[x], ys[x], ha="center", va="bottom")

    plt.xlabel('Regions')
    plt.ylabel('Frequency')
    plt.title(f'Frequency of Companies In {", ".join(user_region)}')
    return plt


# Chart 2: Plot scatter plot
def create_scatter_plot(user_region=regions, user_min_profit=0):
    plt.figure()

    xs = list_company_ranks(user_region, user_min_profit)
    ys = list_company_sizes(user_region, user_min_profit)

    plt.scatter(xs, ys, marker='.', color='g', s=10)

    plt.xlabel("Company's Rank")
    plt.ylabel("Company's Size (Number of Employees)")
    plt.title(f"Company's Size And Impact On Rank")
    return plt


# Chart 3: Map
def create_map(user_min_revenue=5000):
    # df_companies = read_file()
    df_companies = filter_min_max_revenues(user_min_revenue)
    df_companies = df_companies.filter(['NAME', 'LATITUDE', 'LONGITUDE'])

    view_state = pdk.ViewState(latitude=df_companies['LATITUDE'].mean(),
                               longitude=df_companies['LONGITUDE'].mean(),
                               zoom=3)
    layer = pdk.Layer('ScatterplotLayer',
                      data=df_companies,
                      get_position='[LONGITUDE, LATITUDE]',
                      get_radius=12500,
                      get_color=[115, 250, 112],
                      stroked=True,
                      get_line_color=[5, 122, 2],
                      line_width_min_pixels=0.75,
                      opacity=0.5,
                      pickable=True)
    tool_tip = {'html': 'Company:<br/> <b>{NAME}</b>', 'style': {'backgroundColor': 'green', 'color': 'white'}}
    mapping = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                       initial_view_state=view_state,
                       layers=[layer],
                       tooltip=tool_tip)

    st.pydeck_chart(mapping)


# Display to Streamlit
def main():
    # Welcome
    st.balloons()

    # Website text
    st.title("Welcome To Interactive Data-Explorer! ☕")
    st.write("Open the sidebar and make selections to visualize the Fortune 500 Corporate Headquarters data.")
    st.sidebar.write("Make Selections Below To Create Charts")
    st.text("")  # Line Space

    # Sidebar user inputs
    user_region = st.sidebar.multiselect("Chart 1 & 2: Choose Your Region(s)", regions)
    st.sidebar.text("")
    user_min_profit = st.sidebar.number_input("Chart 2: Enter A Minimum Profit", -100000, 50000)
    st.sidebar.text("")
    user_min_revenue = st.sidebar.slider("Chart 3: Choose A Minimum Revenue", 5000, 500000)

    # Chart 1: Bar Chart
    st.subheader("Chart 1: Bar Chart Based On Selections")
    st.pyplot(create_bar_chart(user_region))
    st.text("")

    # Chart 2: Scatter Plot
    st.subheader("Chart 2: Scatter Plot Based On Selections")
    st.pyplot(create_scatter_plot(user_region, user_min_profit))
    correlation = calculate_correlation(user_region, user_min_profit)
    st.text(f"The correlation coefficient between the company's size and its rank is: {correlation:.4f}")
    st.text("")

    # Chart 3: Map
    st.subheader("Chart 3: Map Based On Selections")
    create_map(user_min_revenue)

    st.text("")
    st.text("")

    # Fortune 500 images
    column1, column2 = st.columns(2)
    with column1:
        st.image("Fortune_500_Image.png", width=300)
    with column2:
        st.text("")
        st.text("")
        st.text("")
        st.text("")
        st.image("Fortune_500_Logos.jpg", width=400)

    # Outro
    st.text("")
    st.text("")
    st.markdown("<h3 style='text-align: center;'>Thank you for visiting my website!</h3>", unsafe_allow_html=True)

main()

