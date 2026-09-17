import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Page title
st.title("Customize Your Smoothie! 🥤")

# Connect to Snowflake
conn = st.connection("snowflake")
session = conn.session()

# Get fruit names and API search values from Snowflake
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Customer name
customer_name = st.text_input("Name for your smoothie:")

if customer_name:
    st.write(
        "The name on your Smoothie will be:",
        customer_name
    )

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Process selected ingredients
if ingredients_list:

    # Initialize ingredient string
    ingredients_string = ''

    # Process each selected fruit
    for fruit_chosen in ingredients_list:

        # Add fruit name to ingredient string
        ingredients_string += fruit_chosen + ', '

        # Find the API search value from SEARCH_ON
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Display search value
        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # Display nutrition heading
        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        # Display API response
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Display selected ingredients
    st.write(
        "Your ingredients:",
        ingredients_string
    )

    # Submit order
    if st.button("Submit Order"):

        # Make sure customer name is entered
        if not customer_name:
            st.warning(
                "Please enter your name before submitting the order."
            )

        else:

            # Insert order into Snowflake
            my_insert_stmt = """
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (INGREDIENTS, NAME_ON_ORDER)
                VALUES (?, ?)
            """

            session.sql(
                my_insert_stmt,
                params=[
                    ingredients_string,
                    customer_name
                ]
            ).collect()

            st.success(
                "Your Smoothie is ordered!",
                icon="✅"
            )
