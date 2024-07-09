import argostranslate.package
import argostranslate.translate
from langdetect import detect



# Function to translate text using a specific translation package
def translation(text):
    to_code = "en" 
    from_code = detect(text)
    
    if from_code == "en": 
        return text

    translated_text = argostranslate.translate.translate(text, from_code, to_code)
    return translated_text


