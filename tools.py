def summarize(document):
    return document[:300] + '...'

def find_keywords(document):
    words = document.split()
    return list(set(words[:15]))  # Return the first 15 unique words as keywords

def answer_questions(question, document):
    # Placeholder for question-answering logic
    return f'i dont have AI yet but your question was: "{question}" '