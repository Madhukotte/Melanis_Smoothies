import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title and introduction
st.title("Customize Your Smoothie! :balloon:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name on order
name_on_order = st.text_input('Name on the Smoothie:')
st.write('The name on the Smoothie will be:', name_on_order)

# Snowflake connection setup
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark Dataframe to Pandas Dataframe
pd_df = my_dataframe.to_pandas()

# Multiselect for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Processing selected ingredients
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        # Find corresponding SEARCH_ON value for the chosen fruit
        search_on_value = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Retrieve and display nutrition information using an API
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on_value}")
            if fruityvice_response.status_code == 200:
                fv_json = fruityvice_response.json()
                # st.json(fv_json)
                # Convert JSON data to Pandas DataFrame
                fv_df = pd.DataFrame([fv_json])
                # fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
                st.dataframe(data=fv_df, use_container_width=True)
            else:
                st.error(f"Failed to fetch nutrition info for {fruit_chosen}. Status code: {fruityvice_response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching nutrition info for {fruit_chosen}: {e}")

        ingredients_string += fruit_chosen + ' '

    # Insert order into Snowflake table
    if name_on_order and ingredients_string.strip():
        my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                            VALUES ('{ingredients_string.strip()}', '{name_on_order}')"""
        
        time_to_insert = st.button('Submit Order')

        if time_to_insert:
            try:
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie order has been submitted!')
            except Exception as e:
                st.error(f"Failed to submit order: {e}")
        else:
            st.warning('Click "Submit Order" to place your order.')
