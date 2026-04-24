from trapspringer.layers.layer1_authority.models import CanonQuery
from trapspringer.layers.layer1_authority.service import AuthorityService

def test_authority_service_returns_answer():
    svc = AuthorityService()
    result = svc.query_authority(CanonQuery(query_id="Q1", question="What is in area 44f?", domain="module_content"))
    assert result.query_id == "Q1"
