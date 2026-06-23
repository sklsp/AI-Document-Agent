from agent import run_agent

def import_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

document = import_document('data/company_document.txt')

while True:
    question = input('\nAsk something: ')

    if question.lower() == 'exit':
        break

    print(run_agent(question, document))

answer = run_agent(question, document)
print({answer})

