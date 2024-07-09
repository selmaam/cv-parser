import requests
import json
from spacy.matcher import PhraseMatcher
import string
import re
import pandas as pd
import pickle 
import preprocessing

def Fetch_EMSISkills():
    # Authentication endpoint and credentials
    auth_endpoint = "https://auth.emsicloud.com/connect/token"
    client_id = "ng7bb7djfnu8ekob"
    client_secret = "WHNX3fMk"
    scope = "emsi_open"

    # Set credentials and scope for authentication
    payload = f"client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&scope={scope}"
    headers_auth = {'content-type': 'application/x-www-form-urlencoded'}

    # Get access token
    auth_response = requests.post(auth_endpoint, data=payload, headers=headers_auth)
    auth_response.raise_for_status()  # Ensure the request was successful
    access_token = auth_response.json()['access_token']

    # Define the API endpoint for skills retrieval
    url = "https://emsiservices.com/skills/versions/latest/skills"

    # Set the authorization header with the access token
    auth = f'Bearer {access_token}'
    headers = {'Authorization': auth, 'Content-Type': "application/json"}

    # Define the query parameters
    querystring = {"typeIds": "ST1,ST2,ST3", "fields": "category,subcategory,name,id,type"}

    # Make the API request
    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()  # Ensure the request was successful

    # Save JSON response to a text file
    with open("raw_skills.json", "w") as file:
        json.dump(response.json()['data'], file, indent=4)
    
    
def hierarchical_data(input_file, output_file):
    # Define the category IDs to exclude
    exclude_category_ids = [
        "19", "4", "28", "32", "20", "23", "12", "14", "21", 
        "10", "30", "24", "31", "27", "15", "8", "2", "25"
    ]

    exclude_subcategory_ids = [ "641", "642", "635", "646", "645", "633", "632", "504", "506", "502", "507", "508"]

    with open(input_file, 'r') as f:
        data = json.load(f)
        # print(data)

    # Create a dictionary to store categories and their subcategories
    category_map = {}

    for item in data:
        category_id = str(item['category']['id'])
        category_name = item['category']['name']
        subcategory_id = str(item['subcategory']['id'])
        subcategory_name = item['subcategory']['name']
        item_id = item['id']
        item_name = item['name']
        item_type = item['type']

        # If the category ID is in the exclude list, skip this item
        if category_id in exclude_category_ids:
            continue

        # If the category name is not "NULL", add it to the map
        if category_name != "NULL":
            if category_name not in category_map:
                category_map[category_name] = {'id': category_id, 'subcategories': {}}

            # If the subcategory ID is in the exclude list, skip this item
            if subcategory_id in exclude_subcategory_ids:
                continue
            # If the subcategory name is not "NULL", add it to the subcategories dictionary
            if subcategory_name != "NULL":
                if subcategory_id not in category_map[category_name]['subcategories']:
                    category_map[category_name]['subcategories'][subcategory_id] = {'name': subcategory_name, 'items': []}

                # Append the item details to the list of items for the subcategory
                category_map[category_name]['subcategories'][subcategory_id]['items'].append({
                    'id': item_id,
                    'name': item_name,
                    'type': item_type  # Added 'type' information to the item details
                })

    # Convert the dictionary to the desired structure
    cleaned_data = {"categories": []}
    for category_name, category in category_map.items():
        cleaned_category = {
            'name': category_name,
            'id': category['id'],
            'subcategories': category['subcategories']
        }
        cleaned_data["categories"].append(cleaned_category)

    # print(cleaned_data)
    with open(output_file, 'w') as f:
        json.dump(cleaned_data, f, indent=4)

#input_file = 'raw_skills.json'
#output_file = 'updated_skills.json'
#clean_json(input_file, output_file)
    


#nlp = spacy.load("en_core_web_sm")

# ------------------------------------------------------ ABBREVIATION EXTRACTION --------------------------------------------------------- #

def extract_abbreviations(text):
    # Pattern to match words with only uppercase letters or at least two uppercase letters anywhere
    pattern = re.compile(r'\b[A-Z/!@#$%^&*()-_=+\[\]{};:\'",.<>?~]{2,}\b|\b(?:\S*[A-Z]\S*[/!@#$%^&*()-_=+\[\]{};:\'",.<>?~]*){2,}\b')

    # Find all matches in the given text
    matches = pattern.findall(text)
    
    # Process each match: convert to lowercase and remove punctuation
    processed_matches = [re.sub(f"[{string.punctuation}]", " ", match.lower()) for match in matches]
    
    return processed_matches

def any_abbv_not_in_skill(string_list, target_string):
    return any(string.lower() not in target_string for string in string_list)

def filter_abbrv(strings):

    to_remove = []
    
    # Check if each string is a subset of any other string
    for s1 in strings:
        for s2 in strings:
            if s1 != s2 and s1 in s2:
                to_remove.append(s1)
                break  
        
    return [string for string in strings if string not in to_remove]


# ------------------------------------------------------ SKILLS DATASET PREPARATION --------------------------------------------------------- #

def skills_preparation(file_path='updated_skills.json'):

    # Open the JSON file and read its contents line by line
    with open(file_path, "r") as file:
        json_data = json.load(file)

    # Initialize a list to hold the extracted information
    extracted_data = []

    # Traverse the JSON structure to extract 'name' and 'type'
    for category in json_data["categories"]:
        for subcategory in category["subcategories"].values():
            for item in subcategory["items"]:
                item_name = item["name"]
                preprocessed_name = preprocessing.preprocessing(item_name)
                lemmatized_name = preprocessing.lemmatization(preprocessing.remove_stopwords(preprocessed_name))
                abbreviations = extract_abbreviations(item_name)
                item_type = item["type"]["name"]
                if abbreviations:
                    abbv = ' '.join(abv for abv in filter_abbrv(abbreviations))
                    # add spaces to abbv in the if below
                    if abbv.lower() in preprocessed_name:
                        abbv = None
                else:
                    abbv = None

                extracted_data.append({"full": item_name, "pprocess": preprocessed_name, "lemma": lemmatized_name, 'abbv': abbv, 'type': item_type})

    # Write hierarchical data to a new CSV file
    pd.DataFrame(extracted_data).to_csv("skills.csv", header=True, index=False)

#Fetch_EMSISkills()
#hierarchical_data(input_file='raw_skills.json', output_file='updated_skills.json')
#print(skills_set(file_path='updated_skills.json'))
# skills_preparation()









# ------------------------------------------------------ MATCHERS PREPARATION --------------------------------------------------------- #

# updating matchers
def abbv_matcher(nlp, data):
    """
    Create a PhraseMatcher for abbreviations from a DataFrame.

    Parameters:
    nlp (spacy.lang.en.English): A loaded SpaCy language model.
    data (pd.DataFrame): A DataFrame with an 'abbv' column containing abbreviations.

    Returns:
    spacy.matcher.PhraseMatcher: A PhraseMatcher object with the abbreviations added.
    """
    
    # Initialize the PhraseMatcher with the given NLP model's vocabulary
    full_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    # Iterate through the DataFrame to get the abbreviations
    for abbv in data['abbv'].dropna().unique():
        pattern = nlp.make_doc(abbv)
        full_matcher.add("skill", [pattern])  
    
    return full_matcher


def full_matcher(nlp, data):
    """
    Create a PhraseMatcher for skill names from a DataFrame.

    Parameters:
    nlp (spacy.lang.en.English): A loaded SpaCy language model.
    data (pd.DataFrame): A DataFrame with an 'pprocess' column containing abbreviations.

    Returns:
    spacy.matcher.PhraseMatcher: A PhraseMatcher object with the abbreviations added.
    """
    
    # Initialize the PhraseMatcher with the given NLP model's vocabulary
    full_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    # Iterate through the DataFrame to get the abbreviations
    for abbv in data['pprocess'].dropna().unique():
        pattern = nlp.make_doc(abbv)
        full_matcher.add("skill", [pattern])  
    
    return full_matcher


def matchers_creation(nlp, data):
    # creating the full matcher one time will sufice 
    updated_abbv_matcher = abbv_matcher(nlp, data)
    with open("updated_abbv_matcher.pkl", "wb") as f:
        pickle.dump(updated_abbv_matcher, f)

    updated_full_matcher = full_matcher(nlp, data)
    with open("updated_full_matcher.pkl", "wb") as f:
        pickle.dump(updated_full_matcher, f)
