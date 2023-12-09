import pandas as pd

#Extraction des body parts depuis le champ "Injury"
#--------------------------------------------------------------------------------------
def extract_body_parts(sharks):
    injury_terms_list = (sharks.Injury.str.split(' ')
                                    .apply(pd.Series).stack().unique().tolist())
    injury_terms_dict = {}
    for injury_term in injury_terms_list:
        injury_terms_dict[injury_term] = len(sharks[sharks.Injury.str.contains(injury_term, na = False)])

    injuries = pd.DataFrame(injury_terms_dict.items(), columns = ['injury_term','occurences']).sort_values('occurences', ascending = False)
    injuries['len'] = injuries.injury_term.str.len()
    injuries = injuries.query('len > 2')
    injuries_dict = injuries.set_index('injury_term').to_dict()['occurences']

    #Based on the list of words extracted from the injury attribute, we identified the relevant ones tied to body parts
    white_listed = ['leg','left','right','foot','arm','hand','ankle','knee','finger','shoulder','torso','wrist','abdomen','head','toe','chest','elbow','face',]
    body_part_relevant = injuries.query('injury_term.isin(@white_listed)').reset_index(drop = True).copy()

    return body_part_relevant

#Extraction des activités depuis le champ "Activity"
#--------------------------------------------------------------------------------------
def extract_activities(sharks):
    sharks.Activity = (sharks.Activity.str.lower()
                                .str.replace("(?i)[^a-z ]",'', regex= True))

    s = sharks.copy()
    s['Activity_list'] = s.Activity.str.split(' ').fillna('-')
    activity_terms_list = (sharks.Activity.str.split(' ')
                                    .apply(pd.Series).stack().unique().tolist())
    activity_terms_dict = {}
    for activity_term in activity_terms_list:
        #activity_terms_dict[activity_term] = len(sharks[sharks.Activity.str.contains(activity_term, na = False)])
        activity_terms_dict[activity_term] = len(sharks[[activity_term in x for x in s.Activity_list]])

    activities = pd.DataFrame(activity_terms_dict.items(), columns = ['activity_term','occurences']).sort_values('occurences', ascending = False)
    #Remove expected stop words
    activities['len'] = activities.activity_term.str.len()
    activities = activities.query('len > 3')
    activities_dict = activities.set_index('activity_term').to_dict()['occurences']

    #Only keep root activities
    activities['extension'] = False
    activities['id'] = activities.activity_term + '(' + activities.occurences.astype(str) +')'
    activities['extensions'] = ''
    for act in activities.activity_term.unique():
        activities.loc[(activities.activity_term.str.contains(act)) & (activities.activity_term != act),'extension'] = True
    idx = activities.loc[(activities.activity_term == act)].index.values[0]
    activities.at[idx,'extensions'] = activities.loc[(activities.activity_term.str.contains(act)) & (activities.activity_term != act)]['id'].unique().tolist()

    return activities

def extract_popular_activities(activities):
    popular_activites = (activities.drop(activities[~activities.activity_term.isin(['surfing', 'swimming', 'fishing', 'diving', 'spearfishing', 'bathing', 'wading', 'scuba', 'snorkeling', 'kayaking'])].index)
                        .head(10)
                        .reset_index()
                        .rename(columns = {'activity_term':'Activity','occurences':'occurence'})
                        .filter(['Activity','occurence']))
    return popular_activites

def old_extract_popular_activities(activities):
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