#Importer les packages nécessaires
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random

from datetime import datetime
import plotly.express as px

#Import de la base de données
sharks = pd.read_excel("input_data\sharks.xlsx")
sharks.head()


#Création du champ "date" sur base du champ "Case number"
#--------------------------------------------------------------------------------------
sharks['date'] = pd.to_datetime(sharks['Case Number'].str.replace("(?i)[^0-9]",'', regex= True),
                                   format = '%Y%m%d',
                                   errors = 'coerce')

#Considère les records ayant des case numbers différents comme non fiables
sharks.loc[sharks['Case Number'] != sharks['Case-Number'],'date'] = pd.NaT
#Rempli tout de même les champs year quand c'est possible
sharks['year'] = sharks.date.dt.year.fillna(0).astype(int)
sharks.loc[(sharks.date.isna()) & (sharks['Case Number'].str[:4].str.isnumeric()),'year'] = sharks.loc[(sharks.date.isna()) & (sharks['Case Number'].str[:4].str.isnumeric()), 'Case Number'].str[:4].astype(int)
sharks.loc[sharks.year < 1700,'year'] = 0

#Création du champ "time" sur base du champ "Time"
#--------------------------------------------------------------------------------------
sharks['time'] = pd.to_datetime(sharks.Time.str.replace("(?i)[^0-9]",'', regex= True)
                                           .str[:4],
                                format = '%H%M',
                                errors = 'coerce').dt.time

#Après avoir extrait les dates, certaines colonnes ne sont plus nécessaires et peuvent être remplacées.
sharks = (sharks.drop(columns = ['Case Number','Date', 'Year','Case-Number', 'Time']))
sharks = sharks[['date','year','time'] + [ col for col in sharks.columns if col not in ['time','date','year'] ] ].copy() #copy else, may return a (dead) view which may trigger SettingWithCopyWarning (cfr df._is_copy)

#Nettoyage du champ "Sex"
#--------------------------------------------------------------------------------------
sharks['Sex'] = (sharks['Sex'].fillna('U')
                              .replace(['N', 'lli', '.'], 'U')
                              .replace('M x 2', 'M')
                              .replace('M ', 'M'))

#Extraction des body parts depuis le champ "Injury"
#--------------------------------------------------------------------------------------
sharks.Injury = (sharks.Injury.str.lower()
                              .str.replace("(?i)[^a-z ]",'', regex= True))
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

#Extraction des activités depuis le champ "Activity"
#--------------------------------------------------------------------------------------
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


body_part_relevant.to_parquet('transformed_data/bodyparts_words.parquet')
activities.to_parquet('transformed_data/activities_words.parquet')
sharks.to_parquet('transformed_data/sharks.parquet')