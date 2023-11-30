import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

from backend.Sharks_streamlit_utils_v1 import get_session_state, extract_popular_activities
from backend.plotly_event import initialize_state, build_plotly_chart, render_plotly_chart, update_state, notify_rerun

df_countries =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE']).assign(selected = False)
var_list = get_session_state(['transformed_data/sharks', 'transformed_data/activities_words'])
sharks, activities = var_list[0], var_list[1]

#Select departure country
with st.expander('Departure country',expanded = True):
    st.header(':blue[Step 1 :] Select the depature country')
    initialize_state()
    selected_country, chosen_country = render_plotly_chart(df_countries, debug_st = False)
    update_state(selected_country, debug_st =False)
    st.markdown('Chosen country :')
    st.markdown(chosen_country)

#with st.expander('Cruise parameters',expanded = True):
st.header(':blue[Step 2 :] Tweak cruise  parameters')
c1,c2,c3 = st.columns([15,2,40])
popular_activites = extract_popular_activities(activities)
c1.number_input('Cruise duration', min_value=1, placeholder= 'Duration in days',value = None, on_change=notify_rerun)
c1.multiselect('Activities', options= popular_activites.Activity.unique().tolist())
#c3.slider('Historical attacks period (included)',min_value= int(sharks.date.dt.year.min()), max_value= int(sharks.date.dt.year.max()), value = [2000,2019])
period_start = c1.date_input('Historical Period start', min_value= datetime(int(sharks.date.dt.year.min()),1,1), max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2000,1,1), format = 'DD-MM-YYYY')
period_end = c1.date_input('Historical Period end', min_value= period_start, max_value= datetime(int(sharks.date.dt.year.max()),1,1), value = datetime(2019,1,1), format = 'DD-MM-YYYY')

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


st.session_state['_widget_rerun_'] = 0

