import re

from .llm import ask_llm


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


def should_use_document(question: str, document: str) -> bool:
    """Return True when the question should be answered from the provided document."""
    if not question:
        return bool(document)

    normalized_question = question.lower().strip()

    document_reference_patterns = [
        r"\bdocument\b",
        r"\bprovided document\b",
        r"\buploaded document\b",
        r"\bthis document\b",
        r"\baccording to\b",
        r"\bbased on\b",
        r"\bfrom the document\b",
        r"\bin the document\b",
        r"\bthe text\b",
        r"\bpassage\b",
        r"\bexcerpt\b",
        r"\bsection\b",
        r"\bcontent\b",
    ]
    if any(re.search(pattern, normalized_question) for pattern in document_reference_patterns):
        return True

    if re.search(r"\bkpn\b", normalized_question):
        return False

    company_context_keywords = [
        "company",
        "mission",
        "customers",
        "customer",
        "employee",
        "employees",
        "product",
        "products",
        "service",
        "services",
        "strategy",
        "vision",
        "values",
        "policy",
        "report",
        "goal",
        "goals",
        "plan",
        "plans",
        "revenue",
        "budget",
        "organization",
        "culture",
        "market",
        "partner",
        "partners",
    ]
    if any(keyword in normalized_question for keyword in company_context_keywords):
        return True

    return bool(document)


def answer_questions(question: str, document: str) -> str:
    """Answer `question` using the uploaded document only when the question is document-related."""
    use_document = should_use_document(question, document)

    if use_document:
        prompt = (
            "You are a helpful assistant. Answer the question using the provided document as the primary source. "
            "If the document contains the answer, reply concisely and cite that it is supported by the document. "
            "If the document does not contain the answer, say that clearly instead of guessing.\n\n"
            f"Document:\n{document}\n\nQuestion: {question}\nAnswer:"
        )
    else:
        prompt = (
            "You are a helpful assistant. Answer the question about KPN using general knowledge. "
            "Do not rely on the provided document unless the user explicitly asks about the document itself.\n\n"
            f"Question: {question}\nAnswer:"
        )

    return ask_llm(prompt)
