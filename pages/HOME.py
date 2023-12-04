import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

from backend.Sharks_streamlit_utils_v1 import get_session_state, extract_popular_activities, initialize_state_filters
from backend.plotly_event import initialize_state, build_plotly_chart, render_plotly_chart

df_countries =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE']).assign(selected = False)
var_list = get_session_state(['transformed_data/sharks', 'transformed_data/activities_words'])
sharks, activities = var_list[0], var_list[1]

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "centered", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space

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
        if c03.button('Pick another country', type = 'primary'): 
            st.session_state['_selected_country_'] = 0
            st.rerun()

#with st.expander('Cruise parameters',expanded = True):
st.header(':blue[Step 2 :] Tweak cruise  parameters')
c1,c2,c3 = st.columns([15,2,40])
popular_activites = extract_popular_activities(activities)
c1.number_input('Cruise duration', min_value=1, placeholder= 'Duration in days',value = None)
c1.multiselect('Activities', options= popular_activites.Activity.unique().tolist())
#c3.slider('Historical attacks period (included)',min_value= int(sharks.date.dt.year.min()), max_value= int(sharks.date.dt.year.max()), value = [2000,2019])
#period_start = c1.date_input('Historical Period start', min_value= datetime(int(sharks.date.dt.year.min()),1,1), max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2000,1,1), format = 'DD-MM-YYYY')
#period_end = c1.date_input('Historical Period end', min_value= period_start, max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2019,1,1), format = 'DD-MM-YYYY')
period_start = c1.selectbox('Historical Period start', options=[*range(int(sharks.date.dt.year.min()), int(sharks.date.dt.year.max()+1),1)], index = 2019-1703-9,placeholder='Start year (included)...')
period_end = c1.selectbox('Historical Period end', options=[*range(period_start, int(sharks.date.dt.year.max()+1),1)], index = len([*range(period_start, int(sharks.date.dt.year.max()+1),1)])-1, placeholder='End year (included)...')+1

initialize_state_filters()
st.session_state['_start_year_'] = period_start
st.session_state['_end_year_'] = period_end



current_selection_size = len(sharks.query("date >= @period_start").query("date <= @period_end"))
c1.markdown(f'⚠️*Selected period contains, **{current_selection_size}** attacks (**{current_selection_size/len(sharks):.1%}** of the dataset)*') #➡️
c1.button('Generate Cruise',type = 'primary', use_container_width=True,)

c3.markdown('###')
with c3.expander('View historical data distribution:'):
    #Distribution of attacks over the years (excluding unformatted dates)
    year_dist = sharks.assign(year = sharks.date.dt.year).groupby(['year']).agg(nbr_attacks = ('date','count')) #sharks['date'].dt.year.value_counts().reset_index()
    fig = px.bar(year_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the years', height = 350)
    st.plotly_chart(fig, use_container_width= True)

    
    st.markdown(':orange[**Note**: *Only attacks in the selected period range will be showed across the application*]')

st.write(st.session_state)