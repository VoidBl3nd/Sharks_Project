import pandas as pd
import streamlit as st
from typing import Set
from typing import Dict
import plotly.express as px
from streamlit_plotly_events import plotly_events

df =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE'])
df['selected'] = False

def initialize_state():
    """Initializes all Session State variables"""

    for session_name in ['_selected_country_','_due_to_rerun_', '_selected_index_', '_curve_number_', '_widget_rerun_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

def build_plotly_chart(df):
    """Build a plotly chloropleth map used to select countries"""
    #Build figure
    #---------------------------------------------------
    fig = px.choropleth(df,
                        locations="CODE",
                        color = 'selected',
                        hover_name="COUNTRY",
                        template = 'seaborn',
                        #projection="orthographic"
    )

    #Make it kind to the eye in Streamlit
    #---------------------------------------------------
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
    fig.update_layout(showlegend=False) # Remove legend

    return fig

def render_plotly_chart(df, debug_st = False, selection_menu = False):
    #Filter Previously selected points
    #---------------------------------------------------
    if '_selected_country_' in st.session_state:
        if debug_st:
            st.write('----- Lastly Selected country --------')
            st.write("country: ", st.session_state['_selected_country_'])
        df.loc[df.COUNTRY == st.session_state['_selected_country_'], 'selected'] = True

    #Render the plot & capture selection
    #---------------------------------------------------
    fig = build_plotly_chart(df)
    map_selection = plotly_events(fig, select_event=True, key=f"_country_selector_")
    if debug_st:
        print(map_selection)

    #If rerun, do not change the selected value (given that we change the df_selectable indexes due to coloring but don't change the selected index from plotlu event)
    #---------------------------------------------------
    if st.session_state['_due_to_rerun_'] or st.session_state['_widget_rerun_']:
        selected_country = st.session_state['_selected_country_']
    else:
        selected_country = 0

    #If run not due to forced rerun,
    #---------------------------------------------------
    try:
        if map_selection[0]['curveNumber'] == 0 and not st.session_state['_due_to_rerun_']:
            df_selectable = df.drop(df[df.selected == True].index).reset_index(drop = True) #Isolate selectable indexes (for curveNumber = 0)
            selected_index = map_selection[0]['pointNumber']
            selected_country = df_selectable.iloc[selected_index].COUNTRY

            if st.session_state['_curve_number_'] == map_selection[0]['curveNumber'] \
            and st.session_state['_selected_index_'] == selected_index \
            and df.selected.sum() > 0 :    
                selected_country = 0

            st.session_state['_selected_index_'] = map_selection[0]['pointNumber']
            st.session_state['_curve_number_'] = map_selection[0]['curveNumber']
    except:
        pass #no selection made

    if st.session_state['_due_to_rerun_'] or st.session_state['_widget_rerun_']:
        if st.session_state['_selected_country_'] == 0:
            country_to_display = None
        else:
            country_to_display = int(df[df.COUNTRY == st.session_state['_selected_country_']].index.values[0])

        if selection_menu:
            picked_country = st.selectbox('Sélectionner un pays de départ',df.COUNTRY.tolist(), index = country_to_display, placeholder='Choisir un pays ou le sélectionner sur la carte')
            if debug_st:
                print('picked country :',picked_country)
                print('selected country : ', selected_country)
            if picked_country !=  None and picked_country != selected_country: #TO REVIEW
                selected_country = picked_country
                st.session_state['_curve_number_'] = 0
                if debug_st:
                    print('selected-------------------------------------------------------------------------')
        if country_to_display == None:
            chosen_country = ''
        else:
            chosen_country = df.COUNTRY.tolist()[country_to_display]
        #if picked_country
        #selected_country =     
    else:
        chosen_country = ''
    if debug_st:
        print("---->", chosen_country)


    #else:  
    #    picked_country = st.selectbox('Sélectionner un pays de départ',df.COUNTRY, index = None, placeholder='Choisir un pays ou le sélectionner sur la carte')
    #    st.session_state['_selected_country_'] = picked_country
    if debug_st:
        st.write("Returned selection object: ", map_selection)
        st.write("Previous selected country: ", st.session_state['_selected_country_'])
        st.write("Currently selected country: ", st.session_state['_selected_country_'])

    return selected_country, chosen_country

def update_state(selected_country, debug_st = False):
    """
    - Selection triggers run from top to bottom.
    - Value selected is only returned during the rerun
    - If value selected, need to store it and rerun 
    """
    #If selected something during this run, rerun to make updates :)
    if debug_st:
        print('current value: ',selected_country)
        print('previous value: ' ,st.session_state['_selected_country_'])
    try:
        if selected_country != st.session_state['_selected_country_']:
            st.session_state['_selected_country_'] = selected_country
            st.session_state['_due_to_rerun_'] = 1
            st.rerun()
            
        else:
            st.session_state['_due_to_rerun_'] = 0
    except Exception as e:
        if debug_st:
            print('EXCEPTION 2 ')
            print(f'{e}')
        st.session_state['_selected_country_'] = selected_country
        st.session_state['_due_to_rerun_'] = 1
        st.rerun()

def notify_rerun():
    st.session_state['_widget_rerun_'] = 1
    print('WIDGET-----------------------------------')
        
if __name__ == "__main__":
    print('-----------------------------------------------------')
    initialize_state()
    selected_country, chosen_country = render_plotly_chart(df)

    print('due_to_rerun : ', st.session_state['_due_to_rerun_'])
    if st.session_state['_due_to_rerun_']:
        st.warning(f"RERUN { str(st.session_state['_due_to_rerun_'])}")

    update_state(selected_country)
    #Quand met en couleur, change l'index ! 