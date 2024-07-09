import spacy
import pandas as pd 
import json 
import pickle as pickle
import os
from rapidfuzz import fuzz, distance
import preprocessing
from fuzzy import FuzzyMatching


def get_skills_full_match(data, full_matcher, text, nlp):
    
    #skills_list = list(pd.DataFrame(data)['name'])
    doc = nlp.make_doc(text)
    skills_clean = []
    for match_id, start, end in full_matcher(doc):
        skills_clean.append(doc[start:end].text)

    # Create a mapping dictionary from cleaned_name to name
    # Step 2: Filter the DataFrame to only include rows with cleaned names in the extracted list

    filtered_df = data[data['pprocess'].isin(skills_clean)]
    #skills = pd.DataFrame(data)[pd.DataFrame(data)['cleaned_name'].isin(skills_clean)]
    #print(skills_clean)
    #for skill in skills_clean:
    
    filtered_df['score'] = 1
    #print(filtered_df)

    filtered_data = data[~data.index.isin(filtered_df.index)]

    return filtered_data, filtered_df



def get_skills_abbv_match(data, abbv_matcher, text, nlp):
    doc = nlp(text)  # Use nlp(text) directly to process the text
    skills_clean = []
    for match_id, start, end in abbv_matcher(doc):
        skills_clean.append(doc[start:end].text)

    # Step 2: Convert the extracted skills with scores to a DataFrame
    extracted_df = pd.DataFrame(skills_clean, columns=['abbv'])

    # Step 3: Merge the DataFrames on the cleaned_name column
    filtered_df = pd.merge(extracted_df, pd.DataFrame(data), on='abbv', how='left').dropna()

    #filtered_df = pd.DataFrame(data)[pd.DataFrame(data)['abbv'].isin(skills_clean)]
    if filtered_df.empty:
        return data, filtered_df
    else:
        filtered_df['score'] = 1
        filtered_data = data[~data.index.isin(filtered_df.index)]

    return filtered_data, filtered_df



def merge_skill_dicts(skill_dicts_list):
    common_columns = ['full', 'type', 'score']
    dfs_list = [df[common_columns] for df in skill_dicts_list if not df.empty]
    
    if not dfs_list:  # Check if dfs_list is empty after filtering
        return pd.DataFrame(columns=common_columns)  # Return an empty DataFrame with the common columns
    
    return pd.concat(dfs_list, ignore_index=True)


def skills_extraction_pipeline(data, text, full_matcher, abbv_matcher, nlp):
    
    skills_db = pd.DataFrame(data)
    
    # print(skills_db.shape)
    processed_text = preprocessing.preprocessing_job(text)

    skills_db = skills_db[skills_db['pprocess'].apply(lambda x: fuzz.partial_token_set_ratio(x, text) > 50)]
    # print(skills_db.shape)
    
   

    # FULL MATCH
    skills_db, full_match_skills = get_skills_full_match(skills_db, full_matcher, processed_text, nlp)
    # print(skills_db.shape, skills_full_match.shape[0])
    # print("full")
    # print(list(full_match_skills.columns()))
    # print(full_match_skills)
    text = preprocessing.remove_stopwords(text)

    # ABBREVIATIONS MATCH
    skills_db, abbv_skills = get_skills_abbv_match(skills_db, abbv_matcher, processed_text, nlp)
    # print(skills_db.shape, abbv_skills.shape[0])
    
    # print("abbv")
    # print(list(abbv_skills.columns()))
    # print(abbv_skills)

    # FUZZY-LEMMA-NGRAMs MATCH
    fuzzy_skills = FuzzyMatching(skills_db, text)
    # print("fuzzy")
    # print(list(fuzzy_skills.columns()))
    # print(fuzzy_skills)
    # COMBINATION
    all_matcher_results = [full_match_skills, abbv_skills, fuzzy_skills]

    merged_skills = merge_skill_dicts(all_matcher_results)
    # print(merged_skills)
    return merged_skills


def load_matchers_and_data():
    
    def load_matcher(specific_file, default_file):
        if specific_file and os.path.exists(specific_file):
            with open(specific_file, "rb") as f:
                return pickle.load(f)
        else:
            with open(default_file, "rb") as f:
                return pickle.load(f)

    # Default file paths
    default_full_matcher_path = "full_matcher.pkl"
    default_abbv_matcher_path = "abbv_matcher.pkl"

    # Specific file paths (change these to the specific paths if needed)
    specific_full_matcher_path = "updated_full_matcher.pkl"
    specific_abbv_matcher_path = "updated_abbv_matcher.pkl"

    # Load matchers
    full_matcher = load_matcher(specific_full_matcher_path, default_full_matcher_path)
    abbv_matcher = load_matcher(specific_abbv_matcher_path, default_abbv_matcher_path)
    
    # Define the default file path
    # de:fault_file_path = "dictionnary_skills.json"

    # Check if the provided file path exists
    file_path = "skills.csv"  # Change this to test different scenarios

    data = pd.read_csv('skills.csv')

    nlp = spacy.load("en_core_web_sm")

    return full_matcher, abbv_matcher, data, nlp