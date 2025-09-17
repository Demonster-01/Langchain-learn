#!/usr/bin/env python3
"""
PDF Documentation Generator for LangChain GPT-Basic Files
=========================================================

This script analyzes all files in the src/gpt-basic directory and generates
comprehensive PDF documentation with detailed explanations and reasoning.
"""

import os
import json
import nbformat
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green, orange
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime

class LangChainDocGenerator:
    def __init__(self, source_dir, output_file):
        self.source_dir = source_dir
        self.output_file = output_file
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the documentation"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=blue,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=red,
            leftIndent=0
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=orange,
            leftIndent=20
        ))
        
        # Code style
        self.styles.add(ParagraphStyle(
            name='CodeStyle',
            parent=self.styles['Code'],
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            backColor='#f0f0f0'
        ))
        
        # Analysis style
        self.styles.add(ParagraphStyle(
            name='AnalysisStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=15,
            rightIndent=15,
            spaceAfter=10,
            textColor=green,
            alignment=TA_JUSTIFY
        ))

    def analyze_python_file(self, filepath):
        """Analyze a Python file and extract key information"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'type': 'Python Script',
            'imports': [],
            'functions': [],
            'classes': [],
            'key_concepts': [],
            'purpose': '',
            'complexity': 'Medium'
        }
        
        lines = content.split('\n')
        
        # Extract imports
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                analysis['imports'].append(line.strip())
        
        # Extract functions and classes
        for line in lines:
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                analysis['functions'].append(func_name)
            elif line.strip().startswith('class '):
                class_name = line.strip().split('(')[0].replace('class ', '').replace(':', '')
                analysis['classes'].append(class_name)
        
        # Determine purpose based on filename and content
        filename = os.path.basename(filepath)
        if 'basic' in filename.lower():
            analysis['purpose'] = 'Demonstrates basic LangChain concepts and components'
            analysis['key_concepts'] = ['LLMs', 'Prompt Templates', 'Chains', 'Memory', 'Agents']
        elif 'tools' in filename.lower():
            analysis['purpose'] = 'Implements custom tools and multi-agent workflows'
            analysis['key_concepts'] = ['Custom Tools', 'Multi-Agent Systems', 'LangGraph', 'State Management']
        
        return analysis, content

    def analyze_notebook_file(self, filepath):
        """Analyze a Jupyter notebook file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        analysis = {
            'type': 'Jupyter Notebook',
            'cells': len(nb.cells),
            'code_cells': 0,
            'markdown_cells': 0,
            'key_concepts': [],
            'purpose': '',
            'complexity': 'Medium'
        }
        
        code_content = []
        markdown_content = []
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                analysis['code_cells'] += 1
                if cell.source.strip():
                    code_content.append(cell.source)
            elif cell.cell_type == 'markdown':
                analysis['markdown_cells'] += 1
                if cell.source.strip():
                    markdown_content.append(cell.source)
        
        # Determine purpose based on filename and content
        filename = os.path.basename(filepath)
        if 'basic' in filename.lower():
            analysis['purpose'] = 'Interactive tutorial covering LangChain fundamentals'
            analysis['key_concepts'] = ['LLMs', 'Prompt Templates', 'Chains', 'Memory', 'Vector Stores', 'Agents']
        elif 'agent' in filename.lower():
            analysis['purpose'] = 'Demonstrates agent creation and tool integration'
            analysis['key_concepts'] = ['Agents', 'Tools', 'ReAct Pattern', 'Multi-Agent Systems']
        elif 'lang_graph' in filename.lower() or 'langgraph' in filename.lower():
            analysis['purpose'] = 'Explores LangGraph for building complex agent workflows'
            analysis['key_concepts'] = ['LangGraph', 'State Management', 'Multi-Agent Workflows', 'Conditional Logic']
        
        return analysis, code_content, markdown_content

    def generate_file_analysis(self, filepath):
        """Generate detailed analysis for a single file"""
        filename = os.path.basename(filepath)
        file_ext = os.path.splitext(filename)[1]
        
        content = []
        
        # File header
        content.append(Paragraph(f"📄 {filename}", self.styles['SectionHeader']))
        content.append(Spacer(1, 12))
        
        if file_ext == '.py':
            analysis, code = self.analyze_python_file(filepath)
            
            # File type and purpose
            content.append(Paragraph(f"<b>Type:</b> {analysis['type']}", self.styles['Normal']))
            content.append(Paragraph(f"<b>Purpose:</b> {analysis['purpose']}", self.styles['Normal']))
            content.append(Spacer(1, 10))
            
            # Key concepts
            if analysis['key_concepts']:
                content.append(Paragraph("<b>Key Concepts:</b>", self.styles['Normal']))
                for concept in analysis['key_concepts']:
                    content.append(Paragraph(f"• {concept}", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            # Imports analysis
            if analysis['imports']:
                content.append(Paragraph("🔧 <b>Dependencies & Imports</b>", self.styles['SubsectionHeader']))
                for imp in analysis['imports']:
                    content.append(Paragraph(f"<font name='Courier'>{imp}</font>", self.styles['CodeStyle']))
                content.append(Spacer(1, 10))
            
            # Functions and classes
            if analysis['functions']:
                content.append(Paragraph("⚙️ <b>Functions</b>", self.styles['SubsectionHeader']))
                for func in analysis['functions']:
                    content.append(Paragraph(f"• {func}()", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            if analysis['classes']:
                content.append(Paragraph("🏗️ <b>Classes</b>", self.styles['SubsectionHeader']))
                for cls in analysis['classes']:
                    content.append(Paragraph(f"• {cls}", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            # Code analysis
            content.append(Paragraph("💻 <b>Code Analysis</b>", self.styles['SubsectionHeader']))
            
            if 'tools_langraph.py' in filename:
                content.append(Paragraph(
                    "This file demonstrates a complete multi-agent system using LangGraph with custom tools. "
                    "It showcases the integration of stock price fetching tools with a collaborative workflow "
                    "involving researcher, writer, and critic agents. The system uses conditional logic to "
                    "iterate until the critic approves the final draft.",
                    self.styles['AnalysisStyle']
                ))
            elif 'basic1.py' in filename:
                content.append(Paragraph(
                    "A minimal example demonstrating the most basic LangChain usage - creating an LLM instance "
                    "and generating a simple response. This serves as the entry point for understanding "
                    "LangChain's core functionality.",
                    self.styles['AnalysisStyle']
                ))
            
        elif file_ext == '.ipynb':
            analysis, code_content, markdown_content = self.analyze_notebook_file(filepath)
            
            # File type and purpose
            content.append(Paragraph(f"<b>Type:</b> {analysis['type']}", self.styles['Normal']))
            content.append(Paragraph(f"<b>Purpose:</b> {analysis['purpose']}", self.styles['Normal']))
            content.append(Paragraph(f"<b>Total Cells:</b> {analysis['cells']} (Code: {analysis['code_cells']}, Markdown: {analysis['markdown_cells']})", self.styles['Normal']))
            content.append(Spacer(1, 10))
            
            # Key concepts
            if analysis['key_concepts']:
                content.append(Paragraph("<b>Key Concepts Covered:</b>", self.styles['Normal']))
                for concept in analysis['key_concepts']:
                    content.append(Paragraph(f"• {concept}", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            # Notebook-specific analysis
            content.append(Paragraph("📊 <b>Notebook Analysis</b>", self.styles['SubsectionHeader']))
            
            if 'basic_1.ipynb' in filename:
                content.append(Paragraph(
                    "This comprehensive notebook covers all fundamental LangChain components. It starts with "
                    "basic LLM usage, progresses through prompt templates and chains, explores memory systems "
                    "for conversation, demonstrates vector stores for retrieval, and concludes with agent "
                    "creation. Each concept is illustrated with practical examples and clear explanations.",
                    self.styles['AnalysisStyle']
                ))
            elif 'agent_tools.ipynb' in filename:
                content.append(Paragraph(
                    "An advanced notebook focusing on agent systems and tool integration. It demonstrates "
                    "how to create custom tools, integrate them with agents, and build sophisticated "
                    "multi-agent workflows. The notebook includes examples of stock price fetching, "
                    "calculator tools, and collaborative agent systems with researcher, writer, and critic roles.",
                    self.styles['AnalysisStyle']
                ))
            elif 'lang_grapgh.ipynb' in filename:
                content.append(Paragraph(
                    "This notebook explores LangGraph, a powerful framework for building complex agent workflows. "
                    "It covers state management, multi-agent conversations, conditional logic, and advanced "
                    "patterns like debate systems and collaborative writing workflows. The examples progress "
                    "from simple agent interactions to sophisticated multi-round debates and approval workflows.",
                    self.styles['AnalysisStyle']
                ))
            elif 'agent_tol.ipynb' in filename:
                content.append(Paragraph(
                    "Focuses on tool integration within agent systems. Demonstrates various approaches to "
                    "creating and using tools, from simple calculators to complex stock price fetchers. "
                    "Shows how tools can be integrated into LangGraph workflows and used in multi-agent scenarios.",
                    self.styles['AnalysisStyle']
                ))
        
        return content

    def generate_overview_section(self):
        """Generate the overview section of the documentation"""
        content = []
        
        content.append(Paragraph("📋 Project Overview", self.styles['SectionHeader']))
        content.append(Spacer(1, 12))
        
        overview_text = """
        This documentation covers a comprehensive collection of LangChain examples and tutorials 
        located in the src/gpt-basic directory. The files demonstrate various aspects of LangChain 
        development, from basic concepts to advanced multi-agent systems.
        
        The collection includes both Python scripts and Jupyter notebooks, each focusing on specific 
        aspects of LangChain development. The examples progress from simple LLM usage to complex 
        multi-agent workflows using LangGraph.
        """
        
        content.append(Paragraph(overview_text, self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        # File summary table
        files = [f for f in os.listdir(self.source_dir) if f.endswith(('.py', '.ipynb'))]
        
        content.append(Paragraph("📁 File Summary", self.styles['SubsectionHeader']))
        
        table_data = [['File', 'Type', 'Primary Focus']]
        
        file_descriptions = {
            'basic1.py': ('Python Script', 'Basic LLM usage'),
            'basic_1.ipynb': ('Jupyter Notebook', 'Comprehensive LangChain fundamentals'),
            'agent_tools.ipynb': ('Jupyter Notebook', 'Agent systems and tool integration'),
            'agent_tol.ipynb': ('Jupyter Notebook', 'Tool creation and integration'),
            'lang_grapgh.ipynb': ('Jupyter Notebook', 'LangGraph workflows and multi-agent systems'),
            'tools_langraph.py': ('Python Script', 'Complete multi-agent workflow implementation')
        }
        
        for file in sorted(files):
            if file in file_descriptions:
                file_type, focus = file_descriptions[file]
                table_data.append([file, file_type, focus])
        
        table = Table(table_data, colWidths=[2.5*inch, 1.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4472C4'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#F2F2F2'),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        return content

    def generate_learning_path_section(self):
        """Generate a recommended learning path section"""
        content = []
        
        content.append(Paragraph("🎯 Recommended Learning Path", self.styles['SectionHeader']))
        content.append(Spacer(1, 12))
        
        learning_steps = [
            ("1. Start with Basics", "basic1.py", "Understand basic LLM instantiation and usage"),
            ("2. Explore Fundamentals", "basic_1.ipynb", "Learn core LangChain components: LLMs, prompts, chains, memory"),
            ("3. Understand Tools", "agent_tol.ipynb", "Learn how to create and integrate custom tools"),
            ("4. Build Agents", "agent_tools.ipynb", "Explore agent systems and tool integration patterns"),
            ("5. Master LangGraph", "lang_grapgh.ipynb", "Build complex multi-agent workflows with state management"),
            ("6. Complete Implementation", "tools_langraph.py", "Study a complete multi-agent system implementation")
        ]
        
        for step, file, description in learning_steps:
            content.append(Paragraph(f"<b>{step}</b>", self.styles['SubsectionHeader']))
            content.append(Paragraph(f"File: <font name='Courier'>{file}</font>", self.styles['Normal']))
            content.append(Paragraph(description, self.styles['Normal']))
            content.append(Spacer(1, 10))
        
        return content

    def generate_key_concepts_section(self):
        """Generate a section explaining key concepts"""
        content = []
        
        content.append(Paragraph("🧠 Key Concepts Explained", self.styles['SectionHeader']))
        content.append(Spacer(1, 12))
        
        concepts = [
            ("LLMs (Large Language Models)", 
             "The foundation of LangChain applications. These are AI models that can understand and generate human-like text."),
            ("Prompt Templates", 
             "Reusable templates for structuring inputs to LLMs, allowing for dynamic content insertion and consistent formatting."),
            ("Chains", 
             "Sequences of operations that can be linked together to create complex workflows, from simple LLM calls to multi-step processes."),
            ("Memory", 
             "Systems for maintaining conversation context and history, enabling more coherent multi-turn interactions."),
            ("Agents", 
             "Autonomous systems that can make decisions about which tools to use and how to respond to different situations."),
            ("Tools", 
             "External functions or APIs that agents can call to perform specific tasks like calculations, web searches, or data retrieval."),
            ("LangGraph", 
             "A framework for building complex, stateful multi-agent workflows with conditional logic and sophisticated control flow."),
            ("Multi-Agent Systems", 
             "Architectures where multiple specialized agents collaborate to solve complex problems, each with specific roles and capabilities.")
        ]
        
        for concept, explanation in concepts:
            content.append(Paragraph(f"<b>{concept}</b>", self.styles['SubsectionHeader']))
            content.append(Paragraph(explanation, self.styles['AnalysisStyle']))
            content.append(Spacer(1, 10))
        
        return content

    def generate_pdf(self):
        """Generate the complete PDF documentation"""
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title page
        story.append(Paragraph("LangChain GPT-Basic Files", self.styles['CustomTitle']))
        story.append(Paragraph("Comprehensive Documentation & Analysis", self.styles['Title']))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("This document provides detailed analysis and documentation for all files in the src/gpt-basic directory, including their purpose, key concepts, and implementation details.", self.styles['Normal']))
        story.append(PageBreak())
        
        # Overview section
        story.extend(self.generate_overview_section())
        story.append(PageBreak())
        
        # Learning path section
        story.extend(self.generate_learning_path_section())
        story.append(PageBreak())
        
        # Key concepts section
        story.extend(self.generate_key_concepts_section())
        story.append(PageBreak())
        
        # Individual file analysis
        story.append(Paragraph("📚 Detailed File Analysis", self.styles['SectionHeader']))
        story.append(Spacer(1, 20))
        
        files = [f for f in os.listdir(self.source_dir) if f.endswith(('.py', '.ipynb'))]
        
        # Sort files in logical order
        file_order = ['basic1.py', 'basic_1.ipynb', 'agent_tol.ipynb', 'agent_tools.ipynb', 'lang_grapgh.ipynb', 'tools_langraph.py']
        sorted_files = []
        for file in file_order:
            if file in files:
                sorted_files.append(file)
        
        # Add any remaining files
        for file in files:
            if file not in sorted_files:
                sorted_files.append(file)
        
        for i, filename in enumerate(sorted_files):
            filepath = os.path.join(self.source_dir, filename)
            if os.path.exists(filepath):
                file_content = self.generate_file_analysis(filepath)
                story.extend(file_content)
                
                if i < len(sorted_files) - 1:  # Don't add page break after last file
                    story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        print(f"✅ PDF documentation generated: {self.output_file}")

def main():
    """Main function to generate the documentation"""
    source_directory = "/home/suresh/Desktop/Learning/Langchain-learn/src/gpt-basic"
    output_file = "/home/suresh/Desktop/Learning/Langchain-learn/LangChain_GPT_Basic_Documentation.pdf"
    
    if not os.path.exists(source_directory):
        print(f"❌ Source directory not found: {source_directory}")
        return
    
    try:
        generator = LangChainDocGenerator(source_directory, output_file)
        generator.generate_pdf()
        print(f"📄 Documentation successfully generated!")
        print(f"📍 Location: {output_file}")
        
    except Exception as e:
        print(f"❌ Error generating documentation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()