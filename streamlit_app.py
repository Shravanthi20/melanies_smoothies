import streamlit as st
from snowflake.snowpark.functions import col

# Page title
st.title("Customize Your Smoothie! :cup_with_straw:")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get available fruits from Snowflake
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME")
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

    # Convert list into a comma-separated string
    ingredients_string = ", ".join(ingredients_list)

    st.write("Your ingredients:", ingredients_string)

    # Submit button
    submit = st.button("Submit Order")

    if submit:

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
