# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('name on Smoothies')
st.write('the name in your Smoothies will be:', name_on_order)

# Connection à Snowflake (à vérifier selon ta configuration)
cnx = st.experimental_connection("snowflake")
session = cnx.session
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# Convert DataFrame column to a list for multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    for fruit_chosen in ingredients_list:
        st.subheader(fruit_chosen + ' Nutrition information:')
        
        # Get fruit info from API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.dataframe(fv_data, use_container_width=True)
        else:
            st.error(f"Could not retrieve data for {fruit_chosen}")

    # SQL insert statement
    time_to_insert = st.button('Submit Order')
    if time_to_insert and name_on_order:
        session.sql(f"INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES ('{ingredients_string}', '{name_on_order}')").collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
    elif not name_on_order:
        st.error("Please enter a name for your order.")
