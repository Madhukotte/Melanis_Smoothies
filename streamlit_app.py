import streamlit as st
from snowflake.snowpark.functions import col
import requests

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
        ingredients_string += fruit_chosen + ' '

        # Retrieve and display nutrition information using an API
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        fv_json = fruityvice_response.json()
        st.json(fv_json)

    # Insert order into Snowflake table
    my_insert_stmt = """INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                        VALUES ('{}', '{}')""".format(ingredients_string.strip(), name_on_order)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie order has been submitted!')

