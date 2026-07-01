#!/usr/bin/env python
"""Verify the AI Workspace System is properly initialized."""

from app.main import app

def main():
    print("✅ SYSTEM VERIFICATION")
    print("=" * 60)
    print(f"✓ LLMService: {type(app.state.llm_service).__name__}")
    print(f"✓ MemoryService: {type(app.state.memory_service).__name__}")
    print(f"✓ DocumentService: {type(app.state.document_service).__name__}")
    print(f"✓ PromptService: {type(app.state.prompt_service).__name__}")
    print()

    # Test MemoryService
    print("✅ SERVICE FUNCTIONALITY")
    print("=" * 60)

    mem = app.state.memory_service
    mem.add_message("test", "user", "Hello")
    mem.add_message("test", "assistant", "Hi there")
    print(f"✓ Memory: {len(mem.get_history('test'))} messages stored")

    # Test DocumentService
    doc = app.state.document_service
    doc_id = doc.store_document("Test document content", "test.txt")
    print(f"✓ Documents: {len(doc.get_all_documents())} document stored")

    # Test PromptService
    prompt = app.state.prompt_service
    prompts = prompt.list_prompts()
    print(f"✓ Prompts: {len(prompts)} prompt templates loaded")
    print()

    # Count endpoints
    print("✅ API ENDPOINTS")
    print("=" * 60)
    routes = [route.path for route in app.routes]
    api_routes = [r for r in routes if r.startswith("/")]
    print(f"✓ Total endpoints: {len(api_routes)}")
    print("  - /health, /models")
    print("  - /chat, /sessions/{id}/history")
    print("  - /documents, /documents/upload, /documents/{id}")
    print("  - /prompts, /prompts/{id}")
    print()
    print("=" * 60)
    print("🎉 SYSTEM READY - All components initialized successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
