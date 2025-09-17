#!/usr/bin/env python3
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black, blue, red, green, orange
from datetime import datetime

class CompleteCodeDocGenerator:
    def __init__(self, source_dir, output_file):
        self.source_dir = source_dir
        self.output_file = output_file
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
    def setup_styles(self):
        self.styles.add(ParagraphStyle(name='CodeBlock', parent=self.styles['Code'], 
                                     fontSize=8, leftIndent=15, backColor='#f5f5f5', spaceAfter=10))
        self.styles.add(ParagraphStyle(name='CodeExplanation', parent=self.styles['Normal'], 
                                     fontSize=10, textColor=green, leftIndent=10, spaceAfter=8))

    def get_key_examples(self, filepath):
        """Extract and explain key code examples"""
        examples = []
        filename = os.path.basename(filepath)
        
        if filename == 'basic1.py':
            examples = [
                {
                    'title': 'Basic LLM Setup',
                    'code': '''from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Write a haiku about autumn leaves")
print(response.content)''',
                    'explanation': 'Creates an OpenAI LLM instance and generates a simple text response. This is the foundation of all LangChain applications.'
                }
            ]
            
        elif filename == 'tools_langraph.py':
            examples = [
                {
                    'title': 'Custom Tool Creation',
                    'code': '''def get_stock_price(ticker: str) -> str:
    prices = {"AAPL": 178.23, "GOOGL": 135.45, "TSLA": 254.78}
    price = prices.get(ticker.upper(), "Ticker not found")
    return f"The current price of {ticker.upper()} is {price}"

stock_tool = Tool(
    name="StockPriceFetcher",
    func=get_stock_price,
    description="Get the current stock price for a given ticker."
)''',
                    'explanation': 'Creates a custom tool that agents can use to fetch stock prices. Tools extend agent capabilities beyond text generation.'
                },
                {
                    'title': 'Multi-Agent Workflow',
                    'code': '''def researcher_node(state):
    ticker = state.get("user_input", "AAPL")
    stock_info = stock_tool.run(ticker)
    summary = llm.invoke(f"Summarize: {stock_info}").content
    state["research"] = summary
    return state

workflow = StateGraph(StockState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_edge("researcher", "writer")''',
                    'explanation': 'Defines agent nodes and connects them in a workflow. Each node processes state and passes it to the next node.'
                }
            ]
            
        elif 'agent_tools.ipynb' in filename:
            examples = [
                {
                    'title': 'Agent with Tools',
                    'code': '''from langchain.agents import initialize_agent

tools = [calculator_tool]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

agent.invoke("What is 23 * 47?")''',
                    'explanation': 'Creates an agent that can use tools to solve problems. The ReAct pattern allows reasoning and acting in cycles.'
                }
            ]
            
        elif 'basic_1.ipynb' in filename:
            examples = [
                {
                    'title': 'Prompt Templates',
                    'code': '''from langchain.prompts import PromptTemplate

template = "Translate the following text into French: {text}"
prompt = PromptTemplate.from_template(template)
formatted = prompt.format(text="Hello, how are you?")''',
                    'explanation': 'Templates make prompts reusable and dynamic. Essential for building scalable applications.'
                },
                {
                    'title': 'Memory for Conversations',
                    'code': '''from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

conversation.invoke("Hi, my name is Alex")
conversation.invoke("What's my name?")''',
                    'explanation': 'Memory enables stateful conversations by storing chat history. Critical for chatbot applications.'
                }
            ]
            
        return examples

    def generate_file_section(self, filepath):
        """Generate complete documentation section for a file"""
        filename = os.path.basename(filepath)
        content = []
        
        # File header
        content.append(Paragraph(f"📁 {filename}", self.styles['Heading1']))
        content.append(Spacer(1, 15))
        
        # Purpose and overview
        purposes = {
            'basic1.py': 'Minimal LangChain example showing basic LLM usage',
            'basic_1.ipynb': 'Comprehensive tutorial covering all LangChain fundamentals',
            'agent_tools.ipynb': 'Advanced agent systems with tool integration',
            'tools_langraph.py': 'Production-ready multi-agent workflow implementation',
            'lang_grapgh.ipynb': 'LangGraph framework for complex agent workflows',
            'agent_tol.ipynb': 'Tool creation and integration patterns'
        }
        
        content.append(Paragraph("🎯 Purpose", self.styles['Heading2']))
        content.append(Paragraph(purposes.get(filename, 'LangChain implementation example'), self.styles['Normal']))
        content.append(Spacer(1, 10))
        
        # Code examples
        examples = self.get_key_examples(filepath)
        
        if examples:
            content.append(Paragraph("💻 Key Code Examples", self.styles['Heading2']))
            
            for example in examples:
                content.append(Paragraph(f"🔧 {example['title']}", self.styles['Heading3']))
                
                # Format code
                clean_code = example['code'].replace('<', '&lt;').replace('>', '&gt;')
                content.append(Paragraph(f"<font name='Courier'>{clean_code}</font>", self.styles['CodeBlock']))
                
                # Add explanation
                content.append(Paragraph(f"💡 Explanation: {example['explanation']}", self.styles['CodeExplanation']))
                content.append(Spacer(1, 15))
        
        return content

    def generate_pdf(self):
        """Generate the complete PDF documentation"""
        doc = SimpleDocTemplate(self.output_file, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        # Title page
        story.append(Paragraph("LangChain Complete Code Documentation", self.styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Detailed Code Examples with Explanations", self.styles['Heading2']))
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        story.append(PageBreak())
        
        # File order for logical learning progression
        file_order = ['basic1.py', 'basic_1.ipynb', 'agent_tol.ipynb', 'agent_tools.ipynb', 'lang_grapgh.ipynb', 'tools_langraph.py']
        
        for filename in file_order:
            filepath = os.path.join(self.source_dir, filename)
            if os.path.exists(filepath):
                file_content = self.generate_file_section(filepath)
                story.extend(file_content)
                story.append(PageBreak())
        
        doc.build(story)
        print(f"✅ Complete code documentation generated: {self.output_file}")

def main():
    source_dir = "/home/suresh/Desktop/Learning/Langchain-learn/src/gpt-basic"
    output_file = "/home/suresh/Desktop/Learning/Langchain-learn/LangChain_Complete_Code_Docs.pdf"
    
    generator = CompleteCodeDocGenerator(source_dir, output_file)
    generator.generate_pdf()

if __name__ == "__main__":
    main()