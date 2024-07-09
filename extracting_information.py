import spacy
import re

nlp = spacy.load("en_core_web_sm")


def extract_resp(sentences, min_length=3):
    # Initialize a set to store unique sentences starting with a verb
    unique_sentences_with_verb = set()

    # Process each sentence in the list
    for text in sentences:
        # Process the sentence using spaCy
        doc = nlp(text)
        
        # Check if the sentence is at least min_length words long
        if len(doc) >= min_length:
            # Check if the first token in the sentence is a verb
            if doc and doc[0].pos_ == "VERB" and doc[0].tag_ in ["VB", "VBZ", "VBG"]:
                unique_sentences_with_verb.add(text)

    # Convert the set back to a list before returning
    return list(unique_sentences_with_verb)


def extract_education(text):
    education = []

    # Use regex pattern to find education information
    # pattern = r"(?i)\b(?:B(?:accalaureate)?|Bachelor(?:'s)?|M(?:aster)?(?:'s)?|Ph(?:\.|d)?\.?\s*D(?:octor)?(?:'s)?|Doctor(?:ate)?)\b\s*(?:\w+\s*)+"
    pattern = r"(?i)\b(?:B(?:accalaureate|ac)?|Bachelor(?:'s)?|M(?:aster)?(?:'s)?|Ph(?:\.|d)?\.?\s*D(?:octor)?(?:'s)?|Doctor(?:ate)?)\b\s*(?:\w+\s*)+"

    matches = re.findall(pattern, text)

    # Define the specific starting words to filter matches
    starting_words = ["Master", "master", "Ph.D", "ph.d", "Ph D ", "Bachelor", "bachelor", "Baccalaureate", "baccalaureate", "Doctor", "doctor", "Doctorate", "doctorate", "Bac"]

    for match in matches:
        # Check if the match starts with any of the specific words
        if any(match.strip().startswith(word) for word in starting_words):
            # Remove newline characters and extra spaces
            cleaned_match = ' '.join(match.split())
            education.append(cleaned_match)

    return education

