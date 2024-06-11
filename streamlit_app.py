# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
# Write directly to the app
st.title("Customize Your Smoothie! :balloon:")
st.write(
    """Choose the fruits you want in your custome Smoothie!
    """
)

#Adding Interactive Elements
#import streamlit as st

# option =st.selectbox(
#   'How would you like to be contacted?',
#    ('Email','Home Phone','Mobile phone')
# )

# st.write('You selected:',option)

#Let's ask about fruits instead of contact methods.

# option =st.selectbox(
#    'What is your fevorite fruit?',
#    ('Banana','Strawberries','Peaches')
# )

# st.write('You selected:',option)


#COl statmenet
#from snowflake.snowpark.functions import col
#session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
st.dataframe(data=my_dataframe, use_container_width=True)
st.stop()

#Add a Multiset
name_on_order = st.text_input('Name on the Smoothie:')
st.write('The name on the Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose upto 5  ingredients:'
    ,my_dataframe
    ,max_selections=5
)
if ingredients_list:
   #st.write(ingredients_list)
   #st.text(ingredients_list)
   ingredients_string=''
for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ''
    st.subheader(fruit_chosen + 'Nutrition Information')
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+ fruit_chosen)
    fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
#st.write(ingredients_string)


my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

st.write(my_insert_stmt)
# st.stop()

time_to_insert = st.button('Submit Order')
if time_to_insert:
   session.sql(my_insert_stmt).collect()
   st.success('Your Smoothie is ordered!',icon="✅")

















    
