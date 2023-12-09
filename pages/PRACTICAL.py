import pandas as pd
import streamlit as st
import plotly.express as px

from backend.Sharks_streamlit_utils_v1 import get_session_state, build_activities_map, render_activities_chart, initialize_state_activities, order_and_hide_pages, activities_mapping
from backend.etl_utils import extract_popular_activities, extract_activities, extract_body_parts

var_list = get_session_state(['transformed_data/sharks'])
sharks = var_list[0]

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()

#if '_start_year_sidebar_' in st.session_state and '_end_year_sidebar_' in st.session_state:
minyear = 1700

with st.sidebar:
    st.subheader(':blue[Select a period range:]')
    period_start = st.selectbox('Historical Period start', options=[*range(minyear, int(sharks.year.max()+1),1)], index = 2019-minyear-9,placeholder='Start year (included)...')
    period_end = st.selectbox('Historical Period end', options=[*range(period_start, int(sharks.year.max()+1),1)], index = len([*range(period_start, int(sharks.year.max()+1),1)])-1, placeholder='End year (included)...')+1
    current_selection_size = len(sharks.query("year >= @period_start").query("year <= @period_end"))
    st.divider()
    st.info(f'Selected period contains: \n\n **{current_selection_size}** attacks (**{current_selection_size/len(sharks):.1%}** of the dataset) :orange[**Note:** only attacks in the selected period will be showed within the visualizations]', icon = "ℹ️")
    with st.expander('View historical data distribution:'):
        #Distribution of attacks over the years (excluding unformatted dates)
        year_dist = sharks.query('year >= @minyear').groupby(['year']).agg(nbr_attacks = ('date','count')) #sharks['date'].dt.year.value_counts().reset_index()
        fig = px.bar(year_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the years', height = 350)
        st.plotly_chart(fig, use_container_width= True)

initial_update = False
if '_start_year_sidebar_' not in st.session_state or  '_end_year_sidebar_' not in st.session_state:
    st.session_state['_start_year_sidebar_'] = period_start
    st.session_state['_end_year_sidebar_'] = period_end
    initial_update = True
    
#If changed year value, recompute df & store them
if initial_update or (st.session_state['_start_year_sidebar_'] != period_start or st.session_state['_end_year_sidebar_'] != period_end):
    with st.spinner('Updating and filtering data based on selected years...'):
        sharks = sharks.query("year >= @period_start").query("year <= @period_end").reset_index(drop = True).copy()
        activities = extract_activities(sharks)
        popular_activities = extract_popular_activities(activities)
        body_parts = extract_body_parts(sharks)
        #Store the values:
        st.session_state['_popular_activities_'] = popular_activities
        st.session_state['_body_parts_'] = body_parts
        st.session_state['_start_year_sidebar_'] = period_start
        st.session_state['_end_year_sidebar_'] = period_end
#Else use the stored values
else:
    sharks = sharks.query("year >= @period_start").query("year <= @period_end").reset_index(drop = True).copy()
    popular_activities = st.session_state['_popular_activities_']
    body_parts = st.session_state['_body_parts_']

#st.title('Historical data information',) # #Practical information about past attacks
st.divider()
c1,c2 = st.columns(2)

#region -> Distribution of attacks over the months (excluding unformatted dates)
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
month_dist = sharks.assign(month = sharks.date.dt.month_name()).groupby(['month']).agg(nbr_attacks = ('month','count'))
fig = px.bar(month_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the months',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_xaxes(categoryorder='array', categoryarray= month_order)

c1.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Distribution of attacks over accross the day (excluding unformatted times)
time_dist = sharks.time.groupby(sharks.time).size()
time_dist.index = pd.PeriodIndex("01-01-2001 "+ time_dist.index.astype(str), freq = 'T')
time_dist = time_dist.resample('30T').sum().rename('nbr_attacks').reset_index()
time_dist.time = time_dist.time.dt.strftime('%H:%M')
fig = px.bar(time_dist, x= 'time',y = 'nbr_attacks', title = 'Distribution of the number of sharks attacks accross a day (30 mins interval)',
             color_discrete_sequence=px.colors.qualitative.Set3)

c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Distribution of attacks accross genders
sex_dist = sharks.groupby('Sex').Sex.count().rename('nbr_attacks').reset_index()
fig = px.pie(sex_dist, values='nbr_attacks', names='Sex', title = 'Repartition of attacks accross genders',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_traces(hoverinfo='label+percent+value', textinfo='label+percent', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Popularity of body parts
fig = px.bar(body_parts.assign(injury_term = body_parts.injury_term.str.capitalize()).drop(body_parts[body_parts.injury_term.isin(['left','right'])].index).sort_values('occurences',ascending = False).head(12),y = 'injury_term',x = 'occurences', orientation = 'h', title = 'Appearance of the different "Body part" terms in the Injury attribute',
             color= 'injury_term', color_discrete_sequence=[px.colors.qualitative.Set3[0]],)
#fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Popularity & mapping of activities
with st.expander('Interactive activities charts', expanded= True):
    initialize_state_activities()
    c1,c2 = st.columns(2)
    
    with c1:
        render_activities_chart(popular_activities, activities_mapping)
        c1a,c1b,c1c = st.columns([1,1,1])

        #May reset activity or use the one selected
        if c1b.button('Reset selection', use_container_width= True):
            st.session_state['_selected_activity_'] = 0
        selected_activity = [st.session_state['_selected_activity_']]

        #Display chosen activity
        if selected_activity == [0]:
            c1a.info(f"You can select an activity to filter the map")
        else:
            c1a.success(f"Selected activity : **{selected_activity[0].capitalize()}**")

        #Toggle
        show_unselected = c1c.toggle('Show unselected data', value= True)

    with c2:
        #Set unselected activities to grey opacity
        unselected_color = "rgba(41, 40, 39,50)"
        #popular_activities['color'] = px.colors.qualitative.Set3[:len(popular_activities)]
        popular_activities['color'] = popular_activities.Activity.map(activities_mapping)
        if selected_activity != [0]:
            popular_activities.loc[~popular_activities.Activity.isin(selected_activity),'color'] = unselected_color

        fig = build_activities_map(popular_activities,sharks, unselected_color, show_unselected)
        st.plotly_chart(fig, use_container_width= True)
#endregion