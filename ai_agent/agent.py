from .tools import summarize, find_keywords, answer_questions


def run_agent(question: str, document: str) -> str:
    question = question.lower().strip()

    if 'summary' in question:
        return summarize(document)
    if 'keyword' in question:
        return find_keywords(document)

    return answer_questions(question, document)
