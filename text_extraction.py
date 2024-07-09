from tika import parser
import unicodedata

def extract_text_from_pdf(file_path):
    """
    Extracts and normalizes text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.
        
    Returns:
        str: Normalized text extracted from the PDF.
    """
    # Using Tika to extract text from the PDF file
    file_data = parser.from_file(file_path)
    text = file_data['content']
    
    # Remove non-ASCII characters and normalize accents
    normalized_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    
    return normalized_text
# def extract_text_from_resume_from_bytesio(uploaded_file):
#     # Convert BytesIO to bytes
#     file_bytes = uploaded_file.getvalue()
    
#     # Convert PDF bytes to images
#     images = convert_from_bytes(file_bytes)

#     # Apply OCR to each image and extract text
#     text = ""
#     for image in images:
#         # Apply OCR with language set to French (ISO 639-1 code 'fra')
#         text += pytesseract.image_to_string(image, lang='fra')

#     return text