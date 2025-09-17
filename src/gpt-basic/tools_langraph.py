from langchain_openai import ChatOpenAI
from langchain.agents import Tool
from langgraph.graph import StateGraph, END

# ------------------------------
# 1. LLM Setup
# ------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ------------------------------
# 2. Custom Tool
# ------------------------------
def get_stock_price(ticker: str) -> str:
    # Mock stock prices
    prices = {"AAPL": 178.23, "GOOGL": 135.45, "TSLA": 254.78}
    price = prices.get(ticker.upper(), "Ticker not found")
    return f"The current price of {ticker.upper()} is {price}"

stock_tool = Tool(
    name="StockPriceFetcher",
    func=get_stock_price,
    description="Get the current stock price for a given ticker."
)

# ------------------------------
# 3. Multi-Agent Nodes
# ------------------------------
class StockState(dict):
    pass

# Researcher node: calls the tool
def researcher_node(state: StockState):
    ticker = state.get("user_input", "AAPL")
    stock_info = stock_tool.run(ticker)
    # LLM summarizes the stock info
    summary = llm.invoke(f"You are Researcher. Summarize this stock info: {stock_info}").content
    state["research"] = summary
    print("\n[Researcher 📊]", summary)
    return state

# Writer node: drafts report
def writer_node(state: StockState):
    research = state["research"]
    feedback = state.get("feedback", "")
    prompt = f"You are Writer. Write a short stock report:\n{research}"
    if feedback:
        prompt += f"\nRevise based on feedback: {feedback}"
    draft = llm.invoke(prompt).content
    state["draft"] = draft
    print("\n[Writer ✍️]", draft)
    return state

# Critic node: reviews draft
def critic_node(state: StockState):
    draft = state["draft"]
    feedback = llm.invoke(
        f"You are Critic. Review this draft:\n{draft}\n"
        f"Give constructive feedback. If it is good, reply 'APPROVED'."
    ).content
    state["feedback"] = feedback
    print("\n[Critic 🧐]", feedback)
    return state

# Conditional edge: loop until approved
def should_continue(state: StockState):
    feedback = state.get("feedback", "")
    if "APPROVED" in feedback.upper():
        return END
    return "writer"

# ------------------------------
# 4. LangGraph Workflow
# ------------------------------
workflow = StateGraph(StockState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "critic")
workflow.add_conditional_edges("critic", should_continue)
app = workflow.compile()

# ------------------------------
# 5. Run Example
# ------------------------------
initial_state = StockState(user_input="TSLA")
final_state = app.invoke(initial_state)

print("\n=== Final Draft ===")
print(final_state["draft"])
print("\n=== Critic Feedback ===")
print(final_state["feedback"])
