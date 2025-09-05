import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
import concurrent.futures
import time
from typing import List, Tuple
import re

# Load environment variables
load_dotenv()

class FileTranslator:
    def __init__(self, api_key=None, max_workers=10):
        """
        Initialize translator for both PDF and text files
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.max_workers = max_workers
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract complete text from all pages of PDF
        """
        full_text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"📄 PDF has {total_pages} pages")
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    
                    if page_text.strip():
                        # Add page header and content
                        full_text += f"\n\n--- Page {page_num + 1} ---\n{page_text}"
                    
                    # Show progress every 10 pages
                    if (page_num + 1) % 10 == 0:
                        print(f"📖 Extracted text from page {page_num + 1}/{total_pages}")
                
                print(f"✅ Successfully extracted text from all {total_pages} pages")
                return full_text.strip()
                
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return None
    
    def extract_pdf_text_by_pages(self, pdf_path):
        """
        Extract text from each PDF page separately for parallel processing
        """
        page_texts = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"📄 PDF has {total_pages} pages")
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        page_texts.append((page_num + 1, text))
                    
                    # Show progress every 10 pages
                    if (page_num + 1) % 10 == 0:
                        print(f"📖 Extracted page {page_num + 1}/{total_pages}")
                
                print(f"✅ Extracted {len(page_texts)} pages with content")
                return page_texts
                
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return []
    
    def read_text_file(self, file_path):
        """
        Read the entire text file content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            print(f"✅ Successfully read text file: {len(content)} characters")
            return content
        except Exception as e:
            print(f"❌ Error reading text file: {e}")
            return None
    
    def split_text_file_by_pages(self, text_content):
        """
        Split text file content into pages based on page markers
        """
        # Look for page markers like "--- Page X ---"
        page_pattern = r'--- Page (\d+) ---\s*(.*?)(?=--- Page \d+ ---|$)'
        pages = re.findall(page_pattern, text_content, re.DOTALL)
        
        if pages:
            print(f"📑 Found {len(pages)} pages in text file")
            return [(int(page_num), content.strip()) for page_num, content in pages]
        else:
            # If no page markers found, split by approximate page size
            print("ℹ️ No page markers found, splitting by approximate page size")
            return self.split_text_into_pages(text_content)
    
    def split_text_into_pages(self, text, approx_page_size=2500):
        """
        Split text into approximate pages based on character count
        """
        pages = []
        lines = text.split('\n')
        current_page = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line)
            
            if current_size + line_size > approx_page_size and current_page:
                page_text = '\n'.join(current_page)
                pages.append((len(pages) + 1, page_text))
                current_page = [line]
                current_size = line_size
            else:
                current_page.append(line)
                current_size += line_size + 1  # +1 for newline
        
        if current_page:
            page_text = '\n'.join(current_page)
            pages.append((len(pages) + 1, page_text))
        
        print(f"📑 Split text into {len(pages)} approximate pages")
        return pages
    
    def smart_chunk_text(self, text, max_chunk_size=2500):
        """
        Split text into smart chunks that preserve context
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        # Try to split at paragraph boundaries first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            para_size = len(paragraph)
            
            if current_size + para_size > max_chunk_size and current_chunk:
                # Finish current chunk
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size + 2  # +2 for newlines
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def translate_text_chunk(self, chunk: str, chunk_id: int) -> Tuple[int, str, bool]:
        """
        Translate a single text chunk
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use GPT-4 for better translation quality
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate Nepali to English accurately. Preserve the original meaning, formatting, and context. Maintain paragraph structure and page markers if present."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this Nepali text to English:\n\n{chunk}"
                    }
                ],
                max_tokens=8000,
                temperature=0.1
            )
            
            translated = response.choices[0].message.content.strip()
            return (chunk_id, translated, True)
            
        except Exception as e:
            print(f"❌ Error translating chunk {chunk_id}: {e}")
            return (chunk_id, f"[Translation failed for this section: {str(e)}]", False)
    
    def translate_full_text(self, text: str) -> str:
        """
        Translate complete text by splitting into manageable chunks
        """
        if not text:
            return ""
        
        print("✂️  Splitting text into manageable chunks...")
        chunks = self.smart_chunk_text(text, max_chunk_size=3000)
        print(f"📦 Split into {len(chunks)} chunks for translation")
        
        # Prepare chunks for parallel processing
        chunk_data = [(chunk, i) for i, chunk in enumerate(chunks)]
        
        print("🚀 Starting parallel translation...")
        start_time = time.time()
        
        # Translate all chunks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(lambda x: self.translate_text_chunk(x[0], x[1]), chunk_data))
        
        # Sort results by chunk ID to maintain order
        results.sort(key=lambda x: x[0])
        
        # Combine all translated chunks
        translated_chunks = [result[1] for result in results]
        full_translation = "\n\n".join(translated_chunks)
        
        end_time = time.time()
        print(f"✅ Translation completed in {end_time - start_time:.2f} seconds")
        
        return full_translation
    
    def translate_page(self, page_data: Tuple[int, str]) -> Tuple[int, str, bool]:
        """
        Translate a single page
        """
        page_num, text = page_data
        try:
            print(f"🌐 Translating page {page_num}...")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are translating page {page_num} from a Nepali document to English. Translate accurately while preserving the meaning and formatting. Include 'Page {page_num}' marker in the translation."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this Nepali page to English:\n\n{text}"
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            translated = response.choices[0].message.content.strip()
            return (page_num, translated, True)
            
        except Exception as e:
            print(f"❌ Error translating page {page_num}: {e}")
            return (page_num, f"[Page {page_num} translation failed: {str(e)}]", False)
    
    def translate_by_pages_parallel(self, pages_data: List[Tuple[int, str]]) -> str:
        """
        Translate each page separately in parallel (FASTEST method)
        """
        if not pages_data:
            return ""
        
        print(f"🚀 Starting parallel page translation with {self.max_workers} workers...")
        start_time = time.time()
        
        # Translate all pages in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.translate_page, pages_data))
        
        # Sort by page number
        results.sort(key=lambda x: x[0])
        
        # Combine all translated pages
        translated_pages = [f"\n\n--- Page {result[0]} ---\n{result[1]}" for result in results]
        full_translation = "\n".join(translated_pages)
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"✅ All {len(pages_data)} pages translated in {total_time:.2f} seconds")
        print(f"⏱️  Average: {total_time/len(pages_data):.2f} seconds per page")
        
        return full_translation
    
    def save_translation(self, translated_text: str, output_path: str):
        """
        Save complete translation to file
        """
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(translated_text)
            
            print(f"💾 Translation saved to: {output_path}")
            print(f"📊 File size: {len(translated_text)} characters")
            
        except Exception as e:
            print(f"❌ Error saving translation: {e}")
    
    def detect_file_type(self, file_path):
        """
        Detect if file is PDF or text based on extension
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.txt', '.text']:
            return 'text'
        else:
            # Try to determine by reading first few bytes
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(5)
                    if header.startswith(b'%PDF-'):
                        return 'pdf'
                    else:
                        return 'text'
            except:
                return 'text'
    
    def translate_file(self, file_path: str, output_path: str = None, method: str = "pages"):
        """
        Main method to translate any file (PDF or text)
        """
        if not output_path:
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_ENGLISH_TRANSLATION.txt"
        
        file_type = self.detect_file_type(file_path)
        print(f"🎯 Starting translation of: {file_path}")
        print(f"📁 File type: {file_type.upper()}")
        print(f"⚡ Using method: {method}")
        
        if file_type == 'pdf':
            if method == "pages":
                # Fastest method: translate each page separately in parallel
                page_texts = self.extract_pdf_text_by_pages(file_path)
                translated_text = self.translate_by_pages_parallel(page_texts)
            else:
                # Alternative method: extract all text first, then chunk and translate
                print("📄 Extracting full text from PDF...")
                full_text = self.extract_text_from_pdf(file_path)
                translated_text = self.translate_full_text(full_text) if full_text else ""
        else:
            # Text file processing
            text_content = self.read_text_file(file_path)
            if not text_content:
                return None
                
            if method == "pages":
                # Try to split text into pages for parallel processing
                page_texts = self.split_text_file_by_pages(text_content)
                translated_text = self.translate_by_pages_parallel(page_texts)
            else:
                # Process as a single text
                translated_text = self.translate_full_text(text_content)
        
        if translated_text:
            self.save_translation(translated_text, output_path)
            
            # Show statistics
            print(f"📈 Translation statistics:")
            print(f"   - Total characters: {len(translated_text)}")
            print(f"   - Estimated pages: {len(translated_text) // 2500}")
            
            return translated_text
        else:
            print("❌ Translation failed - no text was translated")
            return None

# Example usage
if __name__ == "__main__":
    try:
        # Initialize translator with parallel workers
        translator = FileTranslator(max_workers=8)
        
        # Your file path (can be PDF or text)
        input_file = "/home/suresh/Desktop/Learning/Langchain-learn/extracted_text_nepali.txt"
        output_file = "मनी लाउन्डरिङ्ग_english_translation.txt"
        
        if os.path.exists(input_file):
            print("=" * 60)
            print("🚀 FILE TRANSLATION STARTED")
            print("=" * 60)
            
            # This will detect file type and translate accordingly
            complete_translation = translator.translate_file(
                file_path=input_file,
                output_path=output_file,
                method="pages"  # Use "pages" for fastest parallel processing
            )
            
            if complete_translation:
                print("=" * 60)
                print("🎉 TRANSLATION COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print(f"📄 Output file: {output_file}")
                print(f"📊 Complete translation: {len(complete_translation)} characters")
                
                # Show beginning and end to verify completeness
                print(f"\n📖 First 500 characters:")
                print(complete_translation[:500] + "...")
                
                print(f"\n📖 Last 500 characters:")
                if len(complete_translation) > 500:
                    print("..." + complete_translation[-500:])
                else:
                    print(complete_translation)
            else:
                print("❌ Translation failed")
                
        else:
            print(f"❌ Input file not found: {input_file}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()