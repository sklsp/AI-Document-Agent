from agent import run_agent
import os


def import_document(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def interactive():
    # Load default document if present
    default_path = 'data/company_document.txt'
    document = ''
    if os.path.exists(default_path):
        document = import_document(default_path)

    print('Simple interactive agent. Commands:')
    print(" - Type your question and press Enter to ask the agent.")
    print(" - load <path>  : load a document from disk and use it as context")
    print(" - summary      : show a short summary of the current document")
    print(" - keywords     : extract keywords from the current document")
    print(" - exit         : quit")

    while True:
        text = input('\nAsk something (or command): ').strip()

        if not text:
            continue

        cmd = text.split(maxsplit=1)
        op = cmd[0].lower()

        if op == 'exit':
            break

        if op == 'load' and len(cmd) > 1:
            path = cmd[1].strip()
            if not os.path.exists(path):
                print('File not found:', path)
                continue
            document = import_document(path)
            print(f'Loaded document from {path} ({len(document)} chars)')
            continue

        if op == 'summary':
            if not document:
                print('No document loaded.')
                continue
            print(run_agent('summary', document))
            continue

        if op == 'keywords':
            if not document:
                print('No document loaded.')
                continue
            print(run_agent('keyword', document))
            continue

        # Otherwise treat as a question
        if not document:
            print('No document loaded. Use "load <path>" to provide a document, or put one in data/company_document.txt')
            continue

        print(run_agent(text, document))


if __name__ == '__main__':
    interactive()

