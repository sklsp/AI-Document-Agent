from agent import run_agent

with open('sample_document.txt', 'r') as f:
    document = f.read()

while True: 
    question = input('\nAsk something: ')

    if question == 'exit':
        break

    print(run_agent(question, document))