from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")  # or "gpt-3.5-turbo"
response = llm.invoke("Write a haiku about autumn leaves")
print(response.content)
