import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Page title
st.title("Customize Your Smoothie! 🥤")

# Connect to Snowflake
conn = st.connection("snowflake")
session = conn.session()

# Get available fruits from Snowflake
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Customer name
customer_name = st.text_input("Name for your smoothie:")

if customer_name:
    st.write("Name of your smoothie is:", customer_name)

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Process selected ingredients
if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    st.write("Your ingredients:", ingredients_string)

    # Submit button
    if st.button("Submit Order"):

        if not customer_name:
            st.warning("Please enter your name before submitting the order.")

        else:

            # Insert order into Snowflake
            my_insert_stmt = """
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (INGREDIENTS, NAME_ON_ORDER)
                VALUES (?, ?)
            """

            session.sql(
                my_insert_stmt,
                params=[ingredients_string, customer_name]
            ).collect()

            st.success(
                "Your Smoothie is ordered!",
                icon="✅"
            )

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

# st.text(smoothiefroot_response.json())

sf_df = st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
