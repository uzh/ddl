from mozilla_django_oidc.auth import OIDCAuthenticationBackend

import logging

logger = logging.getLogger(__name__)

class DDLOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        verified = super().verify_claims(claims)
        logger.info(f'User Claims: {claims}')
        return verified
