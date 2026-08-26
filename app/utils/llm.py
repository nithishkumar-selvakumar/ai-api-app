from langchain_ollama import ChatOllama


OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2"


_llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
)


def generate_answer(
    question: str,
    context: str,
) -> str:

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided
document context.

Rules:
1. Do not use external knowledge.
2. Do not invent information.
3. Do not make assumptions.
4. Do not combine unrelated statements.
5. Preserve the meaning of the source documents.
6. If multiple parts of the context are relevant,
   combine them only when they clearly describe
   the same topic.
7. If the answer is not present in the context,
   say:
   "The information is not available in the
   uploaded documents."
8. Give a concise, direct answer.
9. Use bullet points when explaining multiple items.

DOCUMENT CONTEXT:
====================
{context}
====================

USER QUESTION:
{question}

ANSWER:
"""

    response = _llm.invoke(prompt)

    return response.content