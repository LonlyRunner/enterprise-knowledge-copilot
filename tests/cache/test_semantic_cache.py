from app.cache.semantic import SemanticCache


def test_semantic_cache_key_is_tenant_scoped():
    key_a = SemanticCache.make_key("kb-1", "合同审批", 3, tenant_id="tenant-a")
    key_b = SemanticCache.make_key("kb-1", "合同审批", 3, tenant_id="tenant-b")
    assert key_a != key_b
    assert "tenant-a" in key_a
    assert "tenant-b" in key_b
