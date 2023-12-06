import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


from backend.Sharks_streamlit_utils_v1 import get_session_state, extract_popular_activities, order_and_hide_pages

var_list = get_session_state(['transformed_data/sharks','generated_data/business','generated_data/tracking', 'transformed_data/activities_words'])
sharks, businness, tracking, activities = var_list[0], var_list[1].sort_values('date'), var_list[2], var_list[3]
figs_height = 350

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()

st.title('Business Tracker')
st.divider()
c1,ch, c2 = st.columns([20,1,10])

#region -> Cumulative revenue
fig = px.area(businness.assign(cumsum_revenue = businness.revenue_from_attacks.cumsum()), x = 'date',y = 'cumsum_revenue', title = 'Cumulative revenue', hover_data= {'date':False}, height = figs_height,
              color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_layout(hovermode="x unified")

c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Cumulative representation of number of sharks caught vs number of attacks
fig = px.line(businness.assign(cumsum_attacks = businness.number_of_successful_attacks.cumsum()), x = 'date', y = 'cumsum_attacks', title = 'Cumulative number of sharks caught vs recorded attacks ', hover_data= {'date':False}, height = figs_height,
              color_discrete_sequence=px.colors.qualitative.Set3)
fig.add_trace(px.line(businness.assign(cumsum_caught = businness.number_of_sharks_caught.cumsum()), x = 'date', y = 'cumsum_caught', color_discrete_sequence=["#ff97ff"], hover_data= {'date':False}).data[0])
fig.update_layout(hovermode="x unified")

c2.plotly_chart(fig, use_container_width= True)
#endregion

#region ->Successful Activities
popular_activities = extract_popular_activities(activities)
popular_activities['color'] = px.colors.qualitative.Set3[:len(popular_activities)]
print(popular_activities)
random_activities = popular_activities.sample(5).reset_index(drop = True)
for activity in random_activities.Activity.unique():
    random_activities.loc[random_activities.Activity == activity, 'occurences'] = np.random.randint(2,25)

fig = px.pie(random_activities,
             values='occurences', names='Activity', title = 'Repartition of sucessful activities', height = figs_height,
             color_discrete_sequence=random_activities.sort_values('occurences',ascending = False).color)
print(random_activities)
print(random_activities.sort_values('occurences',ascending = True).color)#
fig.update_traces(hoverinfo='label+percent+value', textinfo='label+percent', textfont_size=20, marker=dict(line=dict(color='#000000', width=1)))

c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Tracking
fig = px.scatter_geo(tracking.assign(object_type = tracking.id.str[:-2]), color = 'object_type', lat = 'latitude',lon = 'longitude', animation_frame='timeline',height = 800,
                     color_discrete_sequence=['rgb(255,255,179)', '#ff97ff'],
                     symbol='object_type', symbol_sequence=['arrow-right','circle'])
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 100
fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 30
fig.update_traces(marker=dict(size=15, line=dict(width=2, color="Black")))#selector=dict(mode="markers"),

#fig.layout.updatemenus = [dict(type="buttons",buttons=[dict(label="Play",method="animate",args=[None])])]
#fig.layout.updatemenus[0].buttons[0]['label'] = 'Launch livestream'
fig.layout.sliders = None
fig.layout.updatemenus = [{'buttons': [{'args': [None, {'frame': {'duration':
                                                      100, 'redraw': True}, 'mode':
                                                      'immediate', 'fromcurrent':
                                                      True, 'transition':
                                                      {'duration': 30, 'easing':
                                                      'linear'}}],
                                             'label': 'Launch livestream',
                                             'method': 'animate'},
                                            ],
                                'direction': 'left',
                                #'pad': {'r': 10, 't': 70}, #pad': {'r': 10, 't': 70},
                                'showactive': False,
                                'type': 'buttons',}]
                                #'x': 0.115, #0.095, #'x': 0.29,
                                #'xanchor': 'right',
                                #'y': 0.09, #0.17, #y': 0.16,
                                #'yanchor': 'top'}]

fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)')) #Color when zoom out of map
fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
#fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=0.97, bgcolor="Grey", bordercolor="Black", borderwidth=2))

fig.update_geos(showcoastlines=True, coastlinecolor = '#afe3e0',
                showland=True, landcolor='#76b0a6',
                showocean=True, oceancolor= '#50545c', )

c1a,c1b,c1c = c1.columns((3))
#c1a.markdown(f'Number of sharks currently tracked :')
#c1a.markdown(f'\n{len(tracking[tracking.id.str.contains("shark")].id.unique())} 🦈')
#c1b.markdown(f'Number of cruises currently tracked :')
#c1b.markdown(f'{len(tracking[tracking.id.str.contains("cruise")].id.unique())} ⛵')
#c1c.markdown(f'Total Revenue :')
#c1c.markdown(f'{businness.revenue_from_attacks.sum()} 💲')

c1a.metric(f'Number of sharks currently tracked :',value = f'{len(tracking[tracking.id.str.contains("shark")].id.unique())} 🦈')
c1b.metric(f'Number of cruises currently tracked :', value = f'{len(tracking[tracking.id.str.contains("cruise")].id.unique())} ⛵')
c1c.metric(f'Total Revenue :',value = f'{int(businness.revenue_from_attacks.sum()/1000)}k 💲')

c1.header('Sharks & Cruise realtime tracking')
c1.plotly_chart(fig, use_container_width= True)
#endregion