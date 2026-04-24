from trapspringer.layers.layer1_authority.service import AuthorityService

class AuthorityRouter:
    def __init__(self, authority_service: AuthorityService) -> None:
        self.authority_service = authority_service

    def query(self, canon_query):
        return self.authority_service.query_authority(canon_query)
