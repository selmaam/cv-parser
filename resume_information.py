import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import time
import spacy
import preprocessing

def extract_essential_infos(doc, doc2):

    #for doc in docs:
        # Create an empty dictionary with specified keys
        empty_dict = {
            "name": None,
            "email address": None,
            "number": None,
            "education": None
        }

        # Iterate over entities in the document
        #for ent in doc.ents:
            # Check if the entity is a person
         #   if ent.label_ == "PERSON":
        empty_dict["name"] = extract_name_from_resume(doc2)
        
        empty_dict["email address"] = extract_email_addresses(doc)
        empty_dict["number"] = extract_contact_number_from_resume(doc)
        empty_dict["education"] = extract_education_from_resume(doc)
        
        # If no person entity is found, return None
        return empty_dict
    

def extract_email_addresses(text):
    # Regular expression to match email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}(?:\.[A-Z|a-z]{2,})?\b'
    
    # Find the first email address in the text
    match = re.search(email_pattern, text)
    
    # If a match is found, return the email address; otherwise, return None
    if match:
        return match.group(0)
    else:
        return None
    
import string

def extract_name_from_resume(text):
    # Remove punctuation from the text
    text_space_punct = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))

    # Convert the text to lowercase for case-insensitive matching
    text_lower = text_space_punct.lower()

    # Remove specific words like 'cv' and 'pdf'
    words_to_remove = ['cv',  'pdf', 'docx', 'txt', 'png', 'jpg']
    for word in words_to_remove:
        text_lower = text_lower.replace(word, '')

    # Capitalize the first letter of each word in the cleaned text
    cleaned_text = ' '.join(word.capitalize() for word in text_lower.split())

    # Find the potential name based on the cleaned text
    name_words = cleaned_text.split()
    print(name_words)
    # if len(name_words) >= 3:
    name = ' '.join(''.join(word) for word in name_words)
    return name
    



def extract_contact_number_from_resume(text):
    contact_number = None

    # Use regex pattern to find a potential contact number
    # Original pattern to detect phone numbers
#     pattern = r"\b(?:\+\d{1,3}\s)?\d{3,4}\s\d{3}\s\d{3}\b"  # Phone number pattern
#     additional_pattern = r"\b\d{10}\b"
#     new_pattern = r"\+\d{3}\s\d{3}\s\d{2}\s\d{2}\s\d{2}"
#     add = pattern = r"\+\d{1,3}\s\d{3}\s\d{3}\s\d{3}\s\d{5}"

# # Combine both patterns using |
#     combined_pattern = f"{pattern}|{additional_pattern}|{add}|{new_pattern}"

    patterns = [
        r"\b(?:\+\d{1,3}\s)?\d{3,4}\s\d{3}\s\d{3}\b",  # Phone number pattern
        r"\b\d{10}\b",                                 # 10-digit phone number pattern
        r"\+\d{3}\s\d{3}\s\d{2}\s\d{2}\s\d{2}",        # +123 123 12 12 12 pattern
        r"\+\d{1,3}\s\d{3}\s\d{3}\s\d{3}\s\d{5}",      # +123 123 123 123 12345 pattern
        r"\(\+\d{3}\)\s\d{3}\s\d{3}\s\d{3}"            # (+213) 799 771 062 pattern
    ]

    # Compile the patterns into one regex
    combined_pattern = re.compile("|".join(patterns))


    phone_numbers = re.findall(combined_pattern, text)
    if phone_numbers:
        contact_number = phone_numbers[0]

    return contact_number


def extract_education_from_resume(text):
    education = []

    # Use regex pattern to find education information
    pattern = r"(?i)\b(?:B(?:accalaureate|ac)?|Bachelor(?:'s)?|M(?:aster)?(?:'s)?|Ph(?:\.|d)?\.?\s*D(?:octor)?(?:'s)?|Doctor(?:ate)?)\b\s*(?:\w+\s*)+"

    matches = re.findall(pattern, text)

    # Define the specific starting words to filter matches
    starting_words = ["Master", "master", "Ph.D", "ph.d", "Ph D ", "Bachelor", "bachelor", "Baccalaureate", "baccalaureate", "Doctor", "doctor", "Doctorate", "doctorate"]

    for match in matches:
        # Check if the match starts with any of the specific words
        if any(match.strip().startswith(word) for word in starting_words):
            # Remove newline characters and extra spaces
            cleaned_match = ' '.join(match.split())
            education.append(cleaned_match)

    return education

def del_line_jumps(text):
    # \t & \n
    text = re.sub(r"[\t\n]", " ", text)

    # espace
    text = re.sub(r"\s\s+", " ", text)

    return text

def remove_uselessWords (texte):
  
    return re.sub(r"^\s*(skills|certifications|qualifications|requirements|student|objective|enthusiast|content\W(.*?):)", "", texte)

def remove_uppercase(texte):
  
  return(texte.lower())

def remove_punctuation(texte):

    # ponctuation
    texte = re.sub(r"[!\".'()*,/:;<=>?[\]^_`{|}~]", " ", texte)

    # \t & \n
    texte = re.sub(r"[\t\n]", " ", texte)

    # espace
    texte = re.sub(r"\s{2,}", " ", texte)
    
    # les espaces inutiles
    texte = texte.strip()
    
    return texte

def remove_stopwords(text):

    # Tokenize the text
    tokens = word_tokenize(text)

    # Get the list of English stopwords
    stop_words = set(stopwords.words('english'))

    # Remove stopwords
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

    # Reconstruct the text without stopwords
    filtered_text = ' '.join(filtered_tokens)

    return filtered_text




