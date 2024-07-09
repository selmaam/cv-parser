import matchers
import preprocessing
import translation 
#import OCR_extraction


# Load matchers and data
full_matcher, abbv_matcher, data, nlp = matchers.load_matchers_and_data()





def processing_resume(pdf_path):
    resume_text = OCR_extraction.extract_text_from_resume(pdf_path)
    desc = translation.translation(resume_text)
    pre = preprocessing.preprocessing_job(desc)
    
    return pre

def get_skills(text):
    
    skills= matchers.skills_extraction_pipeline(data, text, full_matcher, abbv_matcher, nlp)
    
    return skills



def processing_job(job):
    desc = translation.translation(job)
    pre = preprocessing.preprocessing_job(desc)
    
    return pre


