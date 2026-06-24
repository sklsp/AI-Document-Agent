from ollama_client import ask_llm


def summarize(document: str) -> str:
    """Return a short summary of `document` using the LLM."""
    prompt = f"Provide a concise summary (3-5 sentences) of the following document:\n\n{document}"
    return ask_llm(prompt)


def find_keywords(document: str, max_keywords: int = 10) -> str:
    """Return a comma-separated list of up to `max_keywords` keywords for `document`."""
    prompt = (
        f"Extract up to {max_keywords} important keywords or keyphrases from the following document. "
        f"Return them as a comma-separated list.\n\n{document}"
    )
    return ask_llm(prompt)


def answer_questions(question: str, document: str) -> str:
    """Answer `question` using the provided `document` as context via the LLM."""
    prompt = (
        "You are a helpful assistant. Use ONLY the information in the provided document to answer the question when possible. "
        "If the document contains the answer, reply concisely and indicate the answer is supported by the document. "
        "If the document does NOT contain the answer, provide a best-effort speculative answer prefixed with 'Hypothetical:' and clearly state that it is speculative. "
        "Do not invent citations or pretend the document contained the information.\n\n"
        f"Document:\n{document}\n\nQuestion: {question}\nAnswer:"
    )
    return ask_llm(prompt)