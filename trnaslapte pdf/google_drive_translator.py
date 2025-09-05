import pytesseract
import pdf2image
from PIL import Image, ImageEnhance, ImageFilter
import concurrent.futures
import os
from tqdm import tqdm
import time

def preprocess_image(image):
    """Preprocess image to improve OCR accuracy"""
    # Convert to grayscale
    image = image.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    # Apply slight blur to reduce noise
    image = image.filter(ImageFilter.MedianFilter(1))
    
    return image

def process_single_page(page_data):
    """Process a single page image with OCR"""
    page_num, image = page_data
    try:
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Perform OCR on the image with Nepali language
        # Try different language configurations
        try:
            # First try with Nepali specifically
            text = pytesseract.image_to_string(processed_image, lang='nep')
        except:
            try:
                # Fallback to Devanagari script
                text = pytesseract.image_to_string(processed_image, lang='dev')
            except:
                # Final fallback to English
                text = pytesseract.image_to_string(processed_image, lang='eng')
        
        return page_num, text
    except Exception as e:
        print(f"Error processing page {page_num}: {str(e)}")
        return page_num, f"ERROR PROCESSING PAGE: {str(e)}"

def extract_text_from_image_pdf_parallel(pdf_path, max_workers=None, dpi=300):
    """Extract text from image-based PDF using parallel processing"""
    # Convert PDF to images
    print("Converting PDF to images...")
    images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
    
    print(f"Processing {len(images)} pages with {max_workers or os.cpu_count()} workers...")
    
    # Prepare page data with page numbers
    page_data = [(i+1, image) for i, image in enumerate(images)]
    
    extracted_text = [None] * len(images)  # Pre-allocate list for results
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Process pages in parallel with progress bar
        futures = {executor.submit(process_single_page, data): data[0] for data in page_data}
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(images), desc="OCR Processing"):
            page_num, text = future.result()
            extracted_text[page_num-1] = f"\n--- Page {page_num} ---\n{text}"
    
    # Combine all text in page order
    return "".join(extracted_text)

if __name__ == "__main__":
    pdf_path = "/home/suresh/Desktop/Learning/Langchain-learn/सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ्ग) निवारण नियमावली, २०८१ (36).pdf"
    
    # Test parallel processing
    print("Starting parallel processing with Nepali language...")
    start_time = time.time()
    text_parallel = extract_text_from_image_pdf_parallel(pdf_path, max_workers=6)
    parallel_time = time.time() - start_time
    
    # Save parallel results
    with open("extracted_text_nepali.txt", "w", encoding="utf-8") as f:
        f.write(text_parallel)
    
    print(f"Parallel processing completed in {parallel_time:.2f} seconds")