import os
import subprocess
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class mPDFTranslator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        self.client = OpenAI(api_key=self.api_key)
    
    def extract_text_advanced(self, pdf_path):
        """
        Specialized extraction for mPDF-generated PDFs
        """
        print("🔄 Using advanced extraction for mPDF PDF...")
        
        # Method 1: Try pdftotext with different encodings
        text = self.try_pdftotext_variations(pdf_path)
        if text:
            return text
        
        # Method 2: Try OCR as last resort
        print("💡 mPDF PDFs often need special handling. Trying OCR...")
        text = self.try_ocr_extraction(pdf_path)
        if text:
            return text
        
        print("❌ All extraction methods failed")
        print("💡 This mPDF-generated PDF may require manual processing")
        return None
    
    def try_pdftotext_variations(self, pdf_path):
        """Try pdftotext with different parameters"""
        encodings = ['UTF-8', 'ISO-8859-1', 'Windows-1252']
        layouts = ['-layout', '-raw', '']
        
        for encoding in encodings:
            for layout in layouts:
                try:
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                        output_file = f.name
                    
                    cmd = ['pdftotext']
                    if layout:
                        cmd.append(layout)
                    cmd.extend(['-enc', encoding, pdf_path, output_file])
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=120)
                    
                    if result.returncode == 0:
                        with open(output_file, 'r', encoding='utf-8', errors='ignore') as f:
                            text = f.read()
                        if text and len(text.strip()) > 100:
                            print(f"✅ Success with encoding: {encoding}, layout: {layout}")
                            return text
                    
                    os.unlink(output_file)
                    
                except Exception as e:
                    if 'output_file' in locals() and os.path.exists(output_file):
                        os.unlink(output_file)
                    continue
        
        return None
    
    def try_ocr_extraction(self, pdf_path):
        """Use OCR to extract text from problematic PDF"""
        try:
            print("🔍 Attempting OCR extraction...")
            
            # Convert PDF to images and use tesseract
            with tempfile.TemporaryDirectory() as temp_dir:
                # First convert PDF to images
                image_files = []
                for page_num in range(1, 124):  # All 124 pages
                    output_image = os.path.join(temp_dir, f"page_{page_num:03d}.png")
                    cmd = [
                        'pdftoppm', '-png', '-f', str(page_num), '-l', str(page_num),
                        pdf_path, os.path.join(temp_dir, f"page_{page_num:03d}")
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        image_files.append(output_image)
                    
                    if page_num % 10 == 0:
                        print(f"📷 Converted {page_num}/124 pages to images")
                
                # OCR each image
                all_text = ""
                for i, image_file in enumerate(image_files):
                    if os.path.exists(image_file):
                        text = self.ocr_image(image_file)
                        if text:
                            all_text += f"\n\n--- Page {i+1} ---\n{text}"
                        
                        if (i + 1) % 10 == 0:
                            print(f"📖 OCR'd {i+1}/{len(image_files)} pages")
                
                if all_text.strip():
                    print("✅ OCR extraction successful")
                    return all_text
                    
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
        
        return None
    
    def ocr_image(self, image_path):
        """OCR a single image using tesseract"""
        try:
            result = subprocess.run([
                'tesseract', image_path, 'stdout', '-l', 'nep+eng'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            return None
        return None
    
    def translate_in_chunks(self, text, chunk_size=1500):
        """Translate text in manageable chunks"""
        if not text:
            return None
        
        # Split into chunks
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        print(f"📦 Split into {len(chunks)} translation chunks")
        
        # Translate chunks
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"🌐 Translating chunk {i+1}/{len(chunks)}...")
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a professional legal translator. 
                            Translate Nepali text to English accurately. 
                            This document is about property purification and money laundering prevention rules.
                            Preserve legal terminology and formatting."""
                        },
                        {
                            "role": "user",
                            "content": f"Translate this Nepali legal text to English:\n\n{chunk}"
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                
                translated = response.choices[0].message.content.strip()
                translated_chunks.append(translated)
                
                # Avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error translating chunk {i+1}: {e}")
                translated_chunks.append(f"[Translation failed for this section]")
        
        return "\n\n".join(translated_chunks)
    
    def save_translation(self, text, output_path):
        """Save translation to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"💾 Translation saved to: {output_path}")
            print(f"📊 Size: {len(text)} characters")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def translate_pdf(self, pdf_path, output_path=None):
        """Main translation method"""
        if not output_path:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = f"{base_name}_TRANSLATION.txt"
        
        print("=" * 60)
        print("🚀 TRANSLATING mPDF-GENERATED PDF")
        print("=" * 60)
        
        # Extract text
        nepali_text = self.extract_text_advanced(pdf_path)
        
        if not nepali_text:
            print("❌ Could not extract text from PDF")
            print("💡 Alternative solutions:")
            print("   1. Use Adobe Acrobat to extract text")
            print("   2. Convert PDF to Word first")
            print("   3. Use online PDF to text converters")
            return None
        
        print(f"✅ Extracted {len(nepali_text)} characters")
        print("🎯 Starting translation...")
        
        # Translate
        start_time = time.time()
        english_text = self.translate_in_chunks(nepali_text)
        end_time = time.time()
        
        if english_text:
            print(f"✅ Translation completed in {end_time - start_time:.2f} seconds")
            self.save_translation(english_text, output_path)
            return english_text
        else:
            print("❌ Translation failed")
            return None

# Alternative: Online OCR approach
def suggest_online_tools():
    """Suggest online tools for difficult PDFs"""
    print("""
💡 RECOMMENDED ALTERNATIVE APPROACH:

Since this is an mPDF-generated PDF that's resisting local extraction,
try these online tools first:

1. 🔗 Google Drive OCR:
   - Upload PDF to Google Drive
   - Right-click → Open with → Google Docs
   - Google will OCR the text automatically

2. 🔗 Adobe Acrobat Online:
   - https://www.adobe.com/acrobat/online/pdf-to-word.html
   - Convert PDF to Word, then extract text

3. 🔗 OnlineOCR.net:
   - https://www.onlineocr.net/
   - Supports Nepali language OCR

4. 🔗 SmallPDF:
   - https://smallpdf.com/pdf-to-word
   - Good for difficult PDFs

After converting, save as text file and use the translation code.
""")

if __name__ == "__main__":
    pdf_file = "/home/suresh/Desktop/Learning/Langchain-learn/सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ्ग) निवारण नियमावली, २०८१ (36).pdf"
    
    if os.path.exists(pdf_file):
        # First try advanced extraction
        translator = mPDFTranslator()
        
        print("🧪 Testing advanced extraction...")
        test_text = translator.extract_text_advanced(pdf_file)
        
        if test_text:
            print(f"✅ Extraction successful! Sample: {test_text[:200]}...")
            print("\n🎯 Proceeding with full translation...")
            translator.translate_pdf(pdf_file)
        else:
            print("❌ Advanced extraction failed")
            suggest_online_tools()
    else:
        print(f"❌ PDF file not found: {pdf_file}")