import pandas as pd
def check_cv_match(df_jd, df_cv, threshold=0.8):
    matched_skills = set()
    total_score = 0
    total_skills = len(df_jd)  # Total number of skills in the job description
    # print(total_skills)
    compt = 0  

    for idx_jd, row_jd in df_jd.iterrows():
        skill = row_jd['full']
        if skill in df_cv['full'].values:
            score_cv = df_cv.loc[df_cv['full'] == skill, 'score'].values[0]
            total_score += score_cv
            matched_skills.add(skill)
            compt += 1

    
    average_score = total_score / total_skills  
   
    return {
        'matched_skills': list(matched_skills),
        'match_percentage': average_score
    }
# def check_cv_match(df_jd, df_cv, threshold=0.8):
#     # Merge DataFrames on 'name' column (skill names)
#     df_merged = pd.merge(df_jd, df_cv, on='name', suffixes=('_jd', '_cv'))
    
#     # Calculate the weighted score for matching skills
#     df_merged['weighted_score'] = df_merged['score_jd'] * df_merged['score_cv']
    
#     # Compute the total weighted score
#     total_weighted_score = df_merged['weighted_score'].sum()
    
#     # Sum of the weights in the job description
#     total_score_jd = df_jd['score'].sum()
    
#     # Compute the match percentage (normalized score)
#     match_percentage = total_weighted_score / total_score_jd if total_score_jd != 0 else 0
    
#     return {
#         'matched_skills': df_merged['name'].tolist(),
#         'match_percentage': match_percentage
#     }
    