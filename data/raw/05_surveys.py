import pandas as pd

background_col_raw = [
    'User ID',
    'Year of birth (for example 1995)', 
    'Sex', 
    'Height (cm)', 
    'Weight (kg)',
    'Shoulder circumference (cm)',
    'How long have you been in Singapore (in years)?',
    'Can you say that you are used to the weather in Singapore?',
    'Can you say that you are satisfied with the weather in this city (outdoor weather conditions)?',
    'Do you suffer from sweating in Singapore?',
    'Do you enjoy being outdoor in Singapore?',
    'What is your estimation of your time (hours) spent outdoor (per day) during the weekdays? (for example 2 hrs)',
    'What is your estimation of your time (hours) spent outdoor (per day) during the weekend? (for example 4 hrs)',
]

hsps_cols_raw = [
    'Do you seem to be aware of subtleties in your environment? ',
    'Are you easily overwhelmed by things like bright lights, strong smells, coarse fabrics, or sirens close by?',
    'Do you have a rich, complex inner life?',
    'Do you get rattled when you have a lot to do in a short amount of time?',
    'Are you deeply moved by the arts or music?',
    'Are you annoyed when people try to get you to do too many things at once?',
    'Do you make a point to avoid violent movies and TV shows?',
    'Do you find it unpleasant to have a lot going on at once?',
    'Do changes in your life shake you up?',
    'Do you notice and enjoy delicate or fine scents, tastes, sounds, works of art?',
    'Are you bothered by intense stimuli, like loud noises or chaotic scenes?',
    'When you must compete or be observed while performing a task, do you become so nervous or shaky that you do much worse than you would otherwise?',
]

swls_cols_raw = [
    'In most ways my life is close to my ideal',
    'The conditions of my life are excellent',
    'I am satisfied with my life',
    'So far I have gotten the important things I want in life',
    'If I could live my life over, I would change almost nothing',
]
    
b5p_cols_raw = [
    'Extraverted, enthusiastic', 
    'Critical, quarrelsome',
    'Dependable, self-disciplined', 
    'Anxious, easily upset',
    'Open to new experience, complex', 
    'Reserved, quiet',
    'Sympathetic, warm', 
    'Disorganized, careless',
    'Calm, emotionally stable',
    'Conventional, unreactive'
]      

background_cols = [
    'user_id',
    'yob', 
    'sex', 
    'height', # cm
    'weight', # kg
    'shoulder_circumference', # cm
    'years_here', # How long have you been in Singapore (in years)?
    'used_weather', #Can you say that you are used to the weather in Singapore?
    'satisfaction_weather', # Can you say that you are satisfied with the weather in this city (outdoor weather conditions)?
    'sweating', #Do you suffer from sweating in Singapore?
    'enjoy_ourdoor', # Do you enjoy being outdoor in Singapore?',
    'outdoor_hr_weekday', # What is your estimation of your time (hours) spent outdoor (per day) during the weekdays? (for example 2 hrs)
    'outdoor_hr_weekend', # What is your estimation of your time (hours) spent outdoor (per day) during the weekend? (for example 4 hrs)',
    
]
hsps_cols = [
    'subtleties_awareness',
    'overwhelemed_awareness',
    'rich_life',
    'rattled',
    'deeply_moved',
    'annoyed',
    'violent_movies',
    'unpleasant',
    'changes_shake',
    'delicates',
    'stimuli_awareness',
    'nervous',
]

swls_cols = [
    'life_ideal',
    'life_conditions',
    'life_satisfaction',
    'important_things',
    'life_changes',
]

b5p_cols = [
    'extraverted',
    'critical',
    'dependable',
    'anxious',
    'new_exp',
    'reserved',
    'sympathetic',
    'disorganized',
    'calm',
    'conventional',
]

# load raw file
df_surveys = pd.read_csv('onboarding/ENTH - 03_Participant Onboarding Survey (Responses) - Form Responses 1.csv')

# rename file with short and useful columns names TODO and save
new_names = background_cols.copy()
new_names.extend(hsps_cols)
new_names.extend(swls_cols)
new_names.extend(b5p_cols)

df_surveys.columns = new_names

df_surveys.to_csv('../processed/enth_surveys_renamed.csv', index=False)

# compute the score of Highly Sensitive Person Scale (HSPS)
df_surveys['hsps'] = round(
    df_surveys[[x for x in new_names
                if x in hsps_cols]].sum(axis=1)/12 + 1, 1
    )

# compute score of Satisfaction With Life Scale (SWLS)
df_surveys['swls'] = df_surveys[[x for x in new_names
    if x in swls_cols]].replace(
        {"Strongly Disagree": 1,
         "Disagree": 2,
         "Slightly Disagree": 3,
         "Neither agree nor disagree": 4,
         "Slightly Agree": 5,
         "Agree": 6,
         "Strongly Agree": 7,
         }
    ).sum(axis=1)

# compute big five personality trait

# remap the values
for col in b5p_cols:
    df_surveys[col] = df_surveys[col].replace({
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Slightly Disagree": 3,
        "Neither agree nor disagree": 4,
        "Slightly Agree": 5,
        "Agree": 6,
        "Strongly Agree": 7,
    })
# mapping from TIPI to B5
# ref: http://gosling.psy.utexas.edu/wp-content/uploads/2014/09/JRP-03-tipi.pdf
b5p_qns = {
    'extraversion': ['extraverted', 'reserved'],
    'agreeableness': ['critical', 'sympathetic'],
    'conscientiousness': ['dependable', 'disorganized'],
    'emotional_stability': ['anxious', 'calm'],
    'openness_to_experiences': ['new_exp', 'conventional']
}

reversed = ['reserved', 'critical', 'disorganized', 'anxious', 'conventional']
# calculate reverse score
for rev in reversed:
    df_surveys[rev] = df_surveys[rev].replace({1: 7, 2: 6, 3: 5, 4: 4})
# calculate 5 personality traits
for trait in b5p_qns.keys():
    qns1 = b5p_qns[trait][0]
    qns2 = b5p_qns[trait][1]
    df_surveys[trait] = (df_surveys[qns1] + df_surveys[qns2])/2

# remove original raw questions
df_surveys = df_surveys.drop(hsps_cols, axis=1)
df_surveys = df_surveys.drop(swls_cols, axis=1)
df_surveys = df_surveys.drop(b5p_cols, axis=1)

df_surveys.to_csv('../processed/enth_surveys_calc.csv', index=False)
