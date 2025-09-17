#!/usr/bin/env python3
"""
Simple PDF Documentation Generator for LangChain GPT-Basic Files
===============================================================

This script analyzes all files in the src/gpt-basic directory and generates
comprehensive PDF documentation with detailed explanations and reasoning.
"""

import os
import json
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
        """Analyze a Jupyter notebook file by reading it as JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                nb_data = json.load(f)
            
            analysis = {
                'type': 'Jupyter Notebook',
                'cells': len(nb_data.get('cells', [])),
                'code_cells': 0,
                'markdown_cells': 0,
                'key_concepts': [],
                'purpose': '',
                'complexity': 'Medium'
            }
            
            code_content = []
            markdown_content = []
            
            for cell in nb_data.get('cells', []):
                if cell.get('cell_type') == 'code':
                    analysis['code_cells'] += 1
                    source = cell.get('source', [])
                    if isinstance(source, list):
                        source = ''.join(source)
                    if source.strip():
                        code_content.append(source)
                elif cell.get('cell_type') == 'markdown':
                    analysis['markdown_cells'] += 1
                    source = cell.get('source', [])
                    if isinstance(source, list):
                        source = ''.join(source)
                    if source.strip():
                        markdown_content.append(source)
            
            # Determine purpose based on filename
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
            
        except Exception as e:
            print(f"Error reading notebook {filepath}: {e}")
            return {'type': 'Jupyter Notebook', 'cells': 0, 'code_cells': 0, 'markdown_cells': 0, 'key_concepts': [], 'purpose': 'Error reading file', 'complexity': 'Unknown'}, [], []

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
                for imp in analysis['imports'][:10]:  # Limit to first 10 imports
                    content.append(Paragraph(f"<font name='Courier'>{imp}</font>", self.styles['CodeStyle']))
                if len(analysis['imports']) > 10:
                    content.append(Paragraph(f"... and {len(analysis['imports']) - 10} more imports", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            # Functions and classes
            if analysis['functions']:
                content.append(Paragraph("⚙️ <b>Functions</b>", self.styles['SubsectionHeader']))
                for func in analysis['functions'][:15]:  # Limit to first 15 functions
                    content.append(Paragraph(f"• {func}()", self.styles['Normal']))
                if len(analysis['functions']) > 15:
                    content.append(Paragraph(f"... and {len(analysis['functions']) - 15} more functions", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            if analysis['classes']:
                content.append(Paragraph("🏗️ <b>Classes</b>", self.styles['SubsectionHeader']))
                for cls in analysis['classes']:
                    content.append(Paragraph(f"• {cls}", self.styles['Normal']))
                content.append(Spacer(1, 10))
            
            # Code analysis
            content.append(Paragraph("💻 <b>Code Analysis & Reasoning</b>", self.styles['SubsectionHeader']))
            
            if 'tools_langraph.py' in filename:
                content.append(Paragraph(
                    "This file demonstrates a complete multi-agent system using LangGraph with custom tools. "
                    "It showcases the integration of stock price fetching tools with a collaborative workflow "
                    "involving researcher, writer, and critic agents. The system uses conditional logic to "
                    "iterate until the critic approves the final draft. This represents an advanced pattern "
                    "for building production-ready multi-agent systems.",
                    self.styles['AnalysisStyle']
                ))
                content.append(Paragraph(
                    "<b>Key Implementation Details:</b> The file creates a StockState class for state management, "
                    "implements three specialized agent nodes (researcher, writer, critic), uses custom tools "
                    "for stock price fetching, and employs conditional edges for workflow control. The "
                    "researcher fetches data, the writer creates content, and the critic provides feedback "
                    "in an iterative loop until approval.",
                    self.styles['AnalysisStyle']
                ))
            elif 'basic1.py' in filename:
                content.append(Paragraph(
                    "A minimal example demonstrating the most basic LangChain usage - creating an LLM instance "
                    "and generating a simple response. This serves as the entry point for understanding "
                    "LangChain's core functionality. The simplicity makes it perfect for beginners to "
                    "understand the fundamental concept of LLM interaction.",
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
            content.append(Paragraph("📊 <b>Notebook Analysis & Reasoning</b>", self.styles['SubsectionHeader']))
            
            if 'basic_1.ipynb' in filename:
                content.append(Paragraph(
                    "This comprehensive notebook covers all fundamental LangChain components in a structured, "
                    "educational format. It starts with basic LLM usage, progresses through prompt templates "
                    "and chains, explores memory systems for conversation, demonstrates vector stores for "
                    "retrieval, and concludes with agent creation. Each concept is illustrated with practical "
                    "examples and clear explanations, making it an excellent learning resource.",
                    self.styles['AnalysisStyle']
                ))
                content.append(Paragraph(
                    "<b>Educational Value:</b> The notebook follows a logical progression from simple to complex "
                    "concepts, with each section building upon the previous one. The interactive nature allows "
                    "for experimentation and immediate feedback, making it ideal for hands-on learning.",
                    self.styles['AnalysisStyle']
                ))
            elif 'agent_tools.ipynb' in filename:
                content.append(Paragraph(
                    "An advanced notebook focusing on agent systems and tool integration. It demonstrates "
                    "how to create custom tools, integrate them with agents, and build sophisticated "
                    "multi-agent workflows. The notebook includes examples of stock price fetching, "
                    "calculator tools, and collaborative agent systems with researcher, writer, and critic roles. "
                    "This represents the cutting edge of LangChain development.",
                    self.styles['AnalysisStyle']
                ))
                content.append(Paragraph(
                    "<b>Advanced Patterns:</b> The notebook showcases complex patterns like multi-agent "
                    "collaboration, tool chaining, and conditional workflow execution. It demonstrates "
                    "how agents can work together to produce high-quality outputs through iterative "
                    "refinement and peer review processes.",
                    self.styles['AnalysisStyle']
                ))
            elif 'lang_grapgh.ipynb' in filename:
                content.append(Paragraph(
                    "This notebook explores LangGraph, a powerful framework for building complex agent workflows. "
                    "It covers state management, multi-agent conversations, conditional logic, and advanced "
                    "patterns like debate systems and collaborative writing workflows. The examples progress "
                    "from simple agent interactions to sophisticated multi-round debates and approval workflows. "
                    "This represents the future of agent orchestration.",
                    self.styles['AnalysisStyle']
                ))
                content.append(Paragraph(
                    "<b>LangGraph Innovation:</b> The notebook demonstrates LangGraph's superiority over "
                    "traditional agent frameworks by showing how it handles complex state management, "
                    "conditional branching, and multi-agent coordination. The debate system example "
                    "showcases how agents can engage in structured argumentation with multiple rounds.",
                    self.styles['AnalysisStyle']
                ))
            elif 'agent_tol.ipynb' in filename:
                content.append(Paragraph(
                    "Focuses on tool integration within agent systems. Demonstrates various approaches to "
                    "creating and using tools, from simple calculators to complex stock price fetchers. "
                    "Shows how tools can be integrated into LangGraph workflows and used in multi-agent scenarios. "
                    "This notebook bridges the gap between basic tool usage and advanced agent systems.",
                    self.styles['AnalysisStyle']
                ))
                content.append(Paragraph(
                    "<b>Tool Design Principles:</b> The notebook illustrates best practices for tool design, "
                    "including proper error handling, clear descriptions, and seamless integration with "
                    "agent workflows. It shows how tools can be composed and chained for complex operations.",
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
        development, from basic concepts to advanced multi-agent systems using cutting-edge frameworks 
        like LangGraph.
        
        The collection represents a complete learning journey, starting with fundamental concepts 
        and progressing to production-ready implementations. Each file serves a specific educational 
        purpose and builds upon previous concepts, creating a cohesive learning experience.
        
        The examples showcase real-world applications including stock analysis systems, collaborative 
        writing workflows, and sophisticated agent debates, demonstrating the practical power of 
        LangChain in solving complex problems.
        """
        
        content.append(Paragraph(overview_text, self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        # File summary table
        files = [f for f in os.listdir(self.source_dir) if f.endswith(('.py', '.ipynb'))]
        
        content.append(Paragraph("📁 File Summary", self.styles['SubsectionHeader']))
        
        table_data = [['File', 'Type', 'Primary Focus', 'Complexity']]
        
        file_descriptions = {
            'basic1.py': ('Python Script', 'Basic LLM usage', 'Beginner'),
            'basic_1.ipynb': ('Jupyter Notebook', 'Comprehensive LangChain fundamentals', 'Intermediate'),
            'agent_tools.ipynb': ('Jupyter Notebook', 'Agent systems and tool integration', 'Advanced'),
            'agent_tol.ipynb': ('Jupyter Notebook', 'Tool creation and integration', 'Intermediate'),
            'lang_grapgh.ipynb': ('Jupyter Notebook', 'LangGraph workflows and multi-agent systems', 'Advanced'),
            'tools_langraph.py': ('Python Script', 'Complete multi-agent workflow implementation', 'Expert')
        }
        
        for file in sorted(files):
            if file in file_descriptions:
                file_type, focus, complexity = file_descriptions[file]
                table_data.append([file, file_type, focus, complexity])
        
        table = Table(table_data, colWidths=[2*inch, 1.3*inch, 2.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#4472C4'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
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
        
        content.append(Paragraph(
            "Follow this structured path to master LangChain development, from basic concepts to "
            "advanced multi-agent systems. Each step builds upon the previous one, ensuring a "
            "solid foundation for complex implementations.",
            self.styles['Normal']
        ))
        content.append(Spacer(1, 15))
        
        learning_steps = [
            ("1. Foundation", "basic1.py", "Understand basic LLM instantiation and usage", "Start here to grasp the core concept"),
            ("2. Core Components", "basic_1.ipynb", "Learn LLMs, prompts, chains, memory, and retrieval", "Master the fundamental building blocks"),
            ("3. Tool Integration", "agent_tol.ipynb", "Learn how to create and integrate custom tools", "Understand how to extend agent capabilities"),
            ("4. Agent Systems", "agent_tools.ipynb", "Explore advanced agent patterns and tool integration", "Build sophisticated agent workflows"),
            ("5. LangGraph Mastery", "lang_grapgh.ipynb", "Master complex multi-agent workflows with state management", "Learn the future of agent orchestration"),
            ("6. Production Implementation", "tools_langraph.py", "Study a complete, production-ready multi-agent system", "See everything come together in practice")
        ]
        
        for step, file, description, reasoning in learning_steps:
            content.append(Paragraph(f"<b>{step}</b>", self.styles['SubsectionHeader']))
            content.append(Paragraph(f"📁 File: <font name='Courier'>{file}</font>", self.styles['Normal']))
            content.append(Paragraph(f"🎯 Objective: {description}", self.styles['Normal']))
            content.append(Paragraph(f"💡 Why: {reasoning}", self.styles['AnalysisStyle']))
            content.append(Spacer(1, 12))
        
        return content

    def generate_key_concepts_section(self):
        """Generate a section explaining key concepts with detailed reasoning"""
        content = []
        
        content.append(Paragraph("🧠 Key Concepts Explained", self.styles['SectionHeader']))
        content.append(Spacer(1, 12))
        
        concepts = [
            ("LLMs (Large Language Models)", 
             "The foundation of LangChain applications. These are AI models that can understand and generate human-like text.",
             "Understanding LLMs is crucial because they are the 'brain' of your applications. All other components work to enhance, direct, or manage LLM interactions."),
            ("Prompt Templates", 
             "Reusable templates for structuring inputs to LLMs, allowing for dynamic content insertion and consistent formatting.",
             "Templates ensure consistency and enable dynamic content generation. They're essential for building scalable applications that need to handle varying inputs."),
            ("Chains", 
             "Sequences of operations that can be linked together to create complex workflows, from simple LLM calls to multi-step processes.",
             "Chains enable complex reasoning by breaking down problems into manageable steps. They're the building blocks of sophisticated AI workflows."),
            ("Memory", 
             "Systems for maintaining conversation context and history, enabling more coherent multi-turn interactions.",
             "Memory transforms stateless LLM interactions into stateful conversations, enabling applications like chatbots and assistants that remember context."),
            ("Agents", 
             "Autonomous systems that can make decisions about which tools to use and how to respond to different situations.",
             "Agents represent the evolution from scripted workflows to intelligent, adaptive systems that can reason about their actions and choose appropriate tools."),
            ("Tools", 
             "External functions or APIs that agents can call to perform specific tasks like calculations, web searches, or data retrieval.",
             "Tools extend agent capabilities beyond text generation, enabling interaction with external systems and real-world data sources."),
            ("LangGraph", 
             "A framework for building complex, stateful multi-agent workflows with conditional logic and sophisticated control flow.",
             "LangGraph represents the cutting edge of agent orchestration, enabling complex workflows that traditional frameworks cannot handle efficiently."),
            ("Multi-Agent Systems", 
             "Architectures where multiple specialized agents collaborate to solve complex problems, each with specific roles and capabilities.",
             "Multi-agent systems mirror human team dynamics, where specialized roles collaborate to achieve outcomes beyond individual capabilities.")
        ]
        
        for concept, explanation, reasoning in concepts:
            content.append(Paragraph(f"<b>{concept}</b>", self.styles['SubsectionHeader']))
            content.append(Paragraph(f"📖 Definition: {explanation}", self.styles['Normal']))
            content.append(Paragraph(f"🤔 Why It Matters: {reasoning}", self.styles['AnalysisStyle']))
            content.append(Spacer(1, 12))
        
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
        story.append(Paragraph(
            "This document provides detailed analysis and documentation for all files in the src/gpt-basic "
            "directory, including their purpose, key concepts, implementation details, and educational reasoning. "
            "Each file is analyzed for its contribution to the overall learning journey and practical applications.",
            self.styles['Normal']
        ))
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
        
        # Sort files in logical learning order
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
        print(f"📊 Files analyzed: {len([f for f in os.listdir(source_directory) if f.endswith(('.py', '.ipynb'))])}")
        
    except Exception as e:
        print(f"❌ Error generating documentation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()