from ollama_client import ask_ollama

def answer_question(question, document):

    prompt = f"""
    Answer the question using only the document below.

    DOCUMENT:
    {document}

    QUESTION:
    {question}
    """

    return ask_ollama(prompt)