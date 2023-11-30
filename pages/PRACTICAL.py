import pandas as pd
import streamlit as st
import plotly.express as px


from backend.Sharks_streamlit_utils_v1 import get_session_state

var_list = get_session_state(['transformed_data/sharks', 'transformed_data/bodyparts_words'])
sharks, body_parts = var_list[0], var_list[1]

st.title('Historical data information',) # #Practical information about past attacks
st.divider()
c1,c2 = st.columns(2)

#Distribution of attacks over the months (excluding unformatted dates)
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
month_dist = sharks.assign(month = sharks.date.dt.month_name()).groupby(['month']).agg(nbr_attacks = ('month','count'))
fig = px.bar(month_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the months',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_xaxes(categoryorder='array', categoryarray= month_order)

c1.plotly_chart(fig, use_container_width= True)

#Distribution of attacks over accross the day (excluding unformatted times)
time_dist = sharks.time.groupby(sharks.time).size()
time_dist.index = pd.PeriodIndex("01-01-2001 "+ time_dist.index.astype(str), freq = 'T')
time_dist = time_dist.resample('30T').sum().rename('nbr_attacks').reset_index()
time_dist.time = time_dist.time.dt.strftime('%H:%M')
fig = px.bar(time_dist, x= 'time',y = 'nbr_attacks', title = 'Distribution of the number of sharks attacks accross a day (30 mins interval)',
             color_discrete_sequence=px.colors.qualitative.Set3)

c2.plotly_chart(fig, use_container_width= True)

#Distribution of attacks accross genders
sex_dist = sharks.groupby('Sex').Sex.count().rename('nbr_attacks').reset_index()
fig = px.pie(sex_dist, values='nbr_attacks', names='Sex', title = 'Repartition of attacks accross genders',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_traces(hoverinfo='label+percent+value', textinfo='label+percent', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width= True)

#Popularity of body parts
fig = px.bar(body_parts.drop(body_parts[body_parts.injury_term.isin(['left','right'])].index).sort_values('occurences',ascending = False).head(12),y = 'injury_term',x = 'occurences', orientation = 'h', title = 'Appearance of the different "Body part" terms in the Injury attribute',
             color= 'injury_term', color_discrete_sequence=px.colors.qualitative.Set3,)
#fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width= True)