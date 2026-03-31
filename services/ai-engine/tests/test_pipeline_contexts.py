from app.services.rag.pipeline import RAGPipeline


def test_build_context_blocks_includes_all_sections() -> None:
    pipeline = RAGPipeline()
    blocks = pipeline._build_context_blocks(
        knowledge_contexts=["knowledge 1"],
        recent_chat=[{"role": "user", "content": "xin chao"}],
        long_term_facts=["khach thich mau xanh"],
    )
    assert any("[CustomerFacts]" in block for block in blocks)
    assert any("[RecentChat]" in block for block in blocks)
    assert any("[KnowledgeBase]" in block for block in blocks)
