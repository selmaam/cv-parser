import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from word_forms.lemmatizer import lemmatize


def normalize_spaced_text(text):

    # Use regular expressions to find sequences of single characters separated by spaces
    pattern = re.compile(r'\b(\w\s)+\w\b')
    
    # Function to replace spaced out characters with normal words
    def replace_spaced(match):
        return match.group(0).replace(' ', '')
    
    # Apply the replacement function to the text
    normalized_text = re.sub(pattern, replace_spaced, text)
    
    return normalized_text

def remove_multi_linebreaks(text):
    # Replace multiple line breaks with a single line break
    cleaned_text = re.sub(r'\n+', '\n', text)
    return cleaned_text

def remove_uppercase(texte):
  
  return(texte.lower())

def remove_punctuation(texte):

    # parenthesis
    texte = re.sub(r'\([^)]*\)', '', texte)

    # ponctuation
    texte = re.sub(r"[!\".'()*,:;<=>?^_`{|}~]", " ", texte)

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

def remove_special_characters(text, special_chars):
    for char in special_chars:
        text = text.replace(char, "")
    return text

special_chars_to_remove = ["•", "!", "@", "#", "$", "%", '-']  # Add more special characters as needed



def preprocessing(texte):
    return remove_punctuation(remove_multi_linebreaks(normalize_spaced_text(remove_uppercase(texte))))

def lemmatization(doc):
    # Lemmatize each word based on its POS tag, keep the word the same if an issue arises
    lemmatized_tokens = []
    for token in doc.split():
        try:
            lemmatized_tokens.append(lemmatize(token))
        except ValueError:
            lemmatized_tokens.append(token)
    normalized_text = ' '.join(lemmatized_tokens)

    return normalized_text

def extract_abbreviations(text):
    # Pattern to match words with only uppercase letters or at least two uppercase letters anywhere
    pattern = re.compile(r'\b[A-Z/!@#$%^&*()-_=+\[\]{};:\'",.<>?~]{2,}\b|\b(?:\S*[A-Z]\S*[/!@#$%^&*()-_=+\[\]{};:\'",.<>?~]*){2,}\b')

    # Find all matches in the given text
    matches = pattern.findall(text)
    
    return matches

def special_char(text):
    return remove_special_characters(text,special_chars_to_remove)


def remove_newlines(text):
    # Replace "\n" with a space
    cleaned_text = text.replace("\n", " ")
    return cleaned_text


def preprocessing_job(text):
    return remove_newlines(remove_punctuation(remove_uppercase(text)))


def tokenize_sentences(text):

    #text = text.strip().replace("\r\n", "\n")
    lines = text.split("\n")

    # Initialize variables to store parsed sentences
    sentences = []
    mini_sentences = []

    # Iterate over tokens in the document
    for line in lines:
        
        # Define the regular expression pattern
        pattern = r'(?<!\b[A-Z]\.)\.(?!\s*[A-Z]\.)'

        # Split the text using the pattern
        mini_sentences = re.split(pattern, line)
        mini_sentences = [sentence.strip() for sentence in mini_sentences if sentence.strip()]
        
        # Remove '\t' characters at the beginning of mini-sentences
        mini_sentences = [sentence.lstrip('\t') for sentence in mini_sentences]

        if not mini_sentences:
            sentences.extend(line)
        else:
            sentences.extend(mini_sentences)
        mini_sentences = []

    sentences = [sentence.lstrip("\t") for sentence in sentences if len(sentence) > 2]
    
    return sentences