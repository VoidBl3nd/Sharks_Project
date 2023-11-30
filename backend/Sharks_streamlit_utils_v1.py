import pandas as pd
import streamlit as st

def get_session_state(var_list:list):
    var_data_list = []
    for var in var_list:
        if var not in st.session_state:
            var_data = pd.read_parquet(f'{var}.parquet')
            st.session_state[var] = var_data
        else:
            var_data = st.session_state[var]

        var_data_list.append(var_data)

    return var_data_list

def extract_popular_activities(activities):
    #popular_activites = activities.head(30).copy().extensions.explode().reset_index()
    #popular_activites[['Activity','occurence']] = popular_activites.extensions.str.split('(', expand = True)
    #popular_activites.occurence = popular_activites.occurence.str.replace(')', '', regex = True)
    #popular_activites = popular_activites.dropna().astype({'occurence':int})
    #popular_activites = (popular_activites
    #                    .drop('index', axis = 1)
    #                    .drop_duplicates()
    #                    .sort_values('occurence', ascending = False)
    #                    .drop(popular_activites[popular_activites.Activity.isin(['boardin','sharks','surface','walking','shupwreck'])].index)
    #                    .head(11)
    #                    .copy()
    #                    .reset_index(drop = True))
    popular_activites = (activities.drop(activities[activities.activity_term.isin(['water','shark','from','standing','boarding','boat','body','fell','free','with','into','overboard','capsized','sharks','boogie','fish','ship','ship','after','surf','floating','treading','board','overboard'])].index)
                        .head(10)
                        .reset_index()
                        .rename(columns = {'activity_term':'Activity','occurences':'occurence'})
                        .filter(['Activity','occurence']))
    return popular_activites