import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from streamlit_extras.switch_page_button import switch_page 

from backend.Sharks_streamlit_utils_v1 import get_session_state, initialize_state_filters, order_and_hide_pages
from backend.plotly_event import initialize_state, build_plotly_chart, render_plotly_chart
from backend.etl_utils import extract_popular_activities

df_countries =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE']).assign(selected = False)
var_list = get_session_state(['transformed_data/sharks', 'transformed_data/activities_words'])
sharks, activities = var_list[0], var_list[1]

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "centered", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()

#Select departure country
with st.expander('Departure country',expanded = True):
    st.header(':blue[Step 1 :] Select the depature country')
    initialize_state()
    need_update = render_plotly_chart(df_countries)
    if need_update:
        st.rerun()

    c01, c02, c03 = st.columns(3)
    if st.session_state['_selected_country_'] == 0:
        c01.info('Please select a country')
    else:
        c01.info('Country selected :')
        c02.success(f"**{st.session_state['_selected_country_']}**")
        if c03.button('Reset and choose another country', type = 'primary'): 
            st.session_state['_selected_country_'] = 0
            st.rerun()

#with st.expander('Cruise parameters',expanded = True):
st.header(':blue[Step 2 :] Tweak cruise  parameters')
c1,c2,c3 = st.columns([15,2,40])
popular_activites = extract_popular_activities(activities)
number_activities = c1.number_input('Number of activities', min_value=1, max_value=5, placeholder= '1-5',value = None)
type_activities = c1.multiselect('Types of activities', options= popular_activites.Activity.unique().tolist(), placeholder='One or more...')
#c3.slider('Historical attacks period (included)',min_value= int(sharks.date.dt.year.min()), max_value= int(sharks.date.dt.year.max()), value = [2000,2019])
#period_start = c1.date_input('Historical Period start', min_value= datetime(int(sharks.date.dt.year.min()),1,1), max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2000,1,1), format = 'DD-MM-YYYY')
#period_end = c1.date_input('Historical Period end', min_value= period_start, max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2019,1,1), format = 'DD-MM-YYYY')
minyear = 1700
period_start = c1.selectbox('Historical Period start', options=[*range(minyear, int(sharks.year.max()+1),1)], index = 2019-minyear-9,placeholder='Start year (included)...')
period_end = c1.selectbox('Historical Period end', options=[*range(period_start, int(sharks.year.max()+1),1)], index = len([*range(period_start, int(sharks.year.max()+1),1)])-1, placeholder='End year (included)...')+1

initialize_state_filters()
st.session_state['_start_year_'] = period_start
st.session_state['_end_year_'] = period_end
st.session_state['_number_activities_'] = number_activities
st.session_state['_type_activities_'] = type_activities

current_selection_size = len(sharks.query("year >= @period_start").query("year <= @period_end"))
c1.markdown(f'⚠️*Selected period contains, **{current_selection_size}** attacks (**{current_selection_size/len(sharks):.1%}** of the dataset)*') #➡️
if c1.button('Generate Cruise',type = 'primary', use_container_width=True,):
    if type_activities == [] or number_activities == None or st.session_state['_selected_country_'] == 0:
        st.error('Please make sure to select a country, specify the number of activities and select at least one activity before submitting.')
    else:
        switch_page("Cruise visualization")

c3.markdown('###')
with c3.expander('View historical data distribution:'):
    #Distribution of attacks over the years (excluding unformatted dates)
    year_dist = sharks.query('year >= @minyear').groupby(['year']).agg(nbr_attacks = ('date','count')) #sharks['date'].dt.year.value_counts().reset_index()
    fig = px.bar(year_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the years', height = 350)
    st.plotly_chart(fig, use_container_width= True)

    
    st.markdown(':orange[**Note**: *Only attacks in the selected period range will be showed across the application*]')