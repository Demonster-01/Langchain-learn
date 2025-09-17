#!/usr/bin/env python3
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, blue, red, green
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from datetime import datetime

class EnhancedDocGenerator:
    def __init__(self, source_dir, output_file):
        self.source_dir = source_dir
        self.output_file = output_file
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
    def setup_styles(self):
        self.styles.add(ParagraphStyle(
            name='CodeSnippet',
            parent=self.styles['Code'],
            fontSize=8,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=8,
            backColor='#f8f8f8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Explanation',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=5,
            spaceAfter=8,
            textColor=green,
            alignment=TA_JUSTIFY
        ))

    def extract_code_examples(self, filepath):
        """Extract key code examples from files"""
        examples = []
        
        if filepath.endswith('.py'):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract function definitions
            lines = content.split('\n')
            current_func = []
            in_function = False
            
            for line in lines:
                if line.strip().startswith('def '):
                    if current_func:
                        examples.append('\n'.join(current_func))
                    current_func = [line]
                    in_function = True
                elif in_function and (line.startswith('    ') or line.strip() == ''):
                    current_func.append(line)
                elif in_function and not line.startswith('    '):
                    examples.append('\n'.join(current_func))
                    current_func = []
                    in_function = False
            
            if current_func:
                examples.append('\n'.join(current_func))
                
        elif filepath.endswith('.ipynb'):
            try:
                with open(filepath, 'r') as f:
                    nb = json.load(f)
                
                for cell in nb.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        source = cell.get('source', [])
                        if isinstance(source, list):
                            code = ''.join(source)
                        else:
                            code = source
                        
                        if code.strip() and len(code) < 500:  # Reasonable size
                            examples.append(code.strip())
            except:
                pass
        
        return examples[:3]  # Return first 3 examples

    def generate_file_docs(self, filepath):
        """Generate documentation for a single file"""
        filename = os.path.basename(filepath)
        content = []
        
        # File header
        content.append(Paragraph(f"📄 {filename}", self.styles['Heading1']))
        content.append(Spacer(1, 12))
        
        # Get code examples
        examples = self.extract_code_examples(filepath)
        
        # File-specific explanations
        if 'basic1.py' in filename:
            content.append(Paragraph("🎯 Purpose: Basic LLM Usage", self.styles['Heading2']))
            content.append(Paragraph(
                "This file demonstrates the simplest way to use LangChain - creating an LLM and generating text.",
                self.styles['Explanation']
            ))
            
        elif 'tools_langraph.py' in filename:
            content.append(Paragraph("🎯 Purpose: Multi-Agent System with Tools", self.styles['Heading2']))
            content.append(Paragraph(
                "Complete implementation of a multi-agent workflow using LangGraph with custom tools for stock analysis.",
                self.styles['Explanation']
            ))
            
        elif 'agent_tools.ipynb' in filename:
            content.append(Paragraph("🎯 Purpose: Agent and Tool Integration", self.styles['Heading2']))
            content.append(Paragraph(
                "Interactive notebook showing how to create agents, integrate tools, and build collaborative workflows.",
                self.styles['Explanation']
            ))
        
        # Code examples section
        if examples:
            content.append(Paragraph("💻 Key Code Examples", self.styles['Heading2']))
            
            for i, example in enumerate(examples, 1):
                content.append(Paragraph(f"Example {i}:", self.styles['Heading3']))
                
                # Clean and format code
                clean_code = example.replace('<', '&lt;').replace('>', '&gt;')
                content.append(Paragraph(f"<font name='Courier'>{clean_code}</font>", self.styles['CodeSnippet']))
                
                # Add explanation based on code content
                if 'def get_stock_price' in example:
                    content.append(Paragraph(
                        "This function creates a mock stock price tool that returns predefined prices for specific tickers.",
                        self.styles['Explanation']
                    ))
                elif 'ChatOpenAI' in example:
                    content.append(Paragraph(
                        "Creates an OpenAI LLM instance using the GPT-4o-mini model for text generation.",
                        self.styles['Explanation']
                    ))
                elif 'StateGraph' in example:
                    content.append(Paragraph(
                        "Sets up a LangGraph workflow with nodes and edges for multi-agent collaboration.",
                        self.styles['Explanation']
                    ))
                
                content.append(Spacer(1, 10))
        
        return content

    def generate_pdf(self):
        """Generate the enhanced PDF with code examples"""
        doc = SimpleDocTemplate(self.output_file, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        # Title
        story.append(Paragraph("LangChain Code Examples & Explanations", self.styles['Title']))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", self.styles['Normal']))
        story.append(PageBreak())
        
        # Process each file
        files = [f for f in os.listdir(self.source_dir) if f.endswith(('.py', '.ipynb'))]
        
        for filename in sorted(files):
            filepath = os.path.join(self.source_dir, filename)
            file_content = self.generate_file_docs(filepath)
            story.extend(file_content)
            story.append(PageBreak())
        
        doc.build(story)
        print(f"✅ Enhanced PDF generated: {self.output_file}")

def main():
    source_dir = "/home/suresh/Desktop/Learning/Langchain-learn/src/gpt-basic"
    output_file = "/home/suresh/Desktop/Learning/Langchain-learn/LangChain_Code_Examples.pdf"
    
    generator = EnhancedDocGenerator(source_dir, output_file)
    generator.generate_pdf()

if __name__ == "__main__":
    main()