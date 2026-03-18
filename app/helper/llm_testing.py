from app.llm import get_llm



prompt = "Tell me about langchain"
llm = get_llm()
answer = llm.invoke(input=prompt)

print(answer.content)