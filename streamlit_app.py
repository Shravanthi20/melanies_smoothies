import streamlit as st
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! :cup_with_straw:")
cnx= st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(
    col("FRUIT_NAME")
)

fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

customer_name = st.text_input("Name for your smoothie:")

if customer_name:
    st.write("Name of your smoothie is:", customer_name)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen

    st.write(ingredients_string)

    my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                        VALUES ('""" + ingredients_string + """', '""" + customer_name + """')"""

    submit = st.button("Submit Order")

    if submit:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
