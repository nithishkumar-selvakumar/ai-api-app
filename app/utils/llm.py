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
    history: str = "",
) -> str:

    prompt = f"""
You are an AI assistant for a project document
question-answering system.

Answer the user's question using ONLY the
provided document context.

Rules:
1. Do not use external knowledge.
2. Do not invent information.
3. Do not make assumptions.
4. Use previous conversation only to understand
   references such as "it", "this", "that", etc.
5. The document context is the source of truth.
6. If the answer is not available in the documents,
   say:
   "The information is not available in the uploaded documents."
7. Give a clear and concise answer.
8. Use bullet points when appropriate.

PREVIOUS CONVERSATION:
======================
{history}

DOCUMENT CONTEXT:
======================
{context}

CURRENT QUESTION:
======================
{question}

ANSWER:
"""

    response = _llm.invoke(prompt)

    return response.content