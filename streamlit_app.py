import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Page title
st.title("Customize Your Smoothie! 🥤")

# Connect to Snowflake
conn = st.connection("snowflake")
session = conn.session()

# Get available fruits and API search values from Snowflake
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(
        col("FRUIT_NAME"),
        col("SEARCH_ON")
    )
)

# Convert to pandas dataframe
fruit_df = my_dataframe.to_pandas()

# Fruit names shown to the user
fruit_list = fruit_df["FRUIT_NAME"].tolist()

# Create mapping between GUI name and API search name
fruit_search_map = dict(
    zip(
        fruit_df["FRUIT_NAME"],
        fruit_df["SEARCH_ON"]
    )
)

# Customer name
customer_name = st.text_input("Name for your smoothie:")

if customer_name:
    st.write("Your name on the smoothie will be:", customer_name)

# Select ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Process selected ingredients
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ", "

        # Display nutrition information heading
        st.subheader(
            fruit_chosen + " Nutrition Information"
        )

        # Get the API search value from SEARCH_ON
        search_on = fruit_search_map[fruit_chosen]

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        # Display API response as dataframe
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    st.write("Your ingredients:", ingredients_string)

    # Submit button
    if st.button("Submit Order"):

        # Check name
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
                params=[ingredients_string, customer_name]
            ).collect()

            st.success(
                "Your Smoothie is ordered!",
                icon="✅"
            )
