import unittest

from ai_agent.tools import should_use_document


class AnswerModeTests(unittest.TestCase):
    def test_general_kpn_question_uses_general_knowledge(self):
        self.assertFalse(should_use_document('What is KPN?', 'some document content'))

    def test_document_reference_uses_document(self):
        self.assertTrue(should_use_document('What does the document say about the mission?', 'some document content'))

    def test_explicit_document_request_uses_document(self):
        self.assertTrue(should_use_document('According to the provided document, who are the main customers?', 'some document content'))


if __name__ == '__main__':
    unittest.main()
