from mozilla_django_oidc.auth import OIDCAuthenticationBackend

import logging

logger = logging.getLogger(__name__)

class DDLOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        verified = super().verify_claims(claims)
        affiliated = False

        linked_affiliation_mails = claims.get('swissEduIDLinkedAffiliationMail')
        if linked_affiliation_mails:
            # Ensure that allowed affiliation is in mails.
            if any(a.endswith('uzh.ch') for a in linked_affiliation_mails):
                affiliated = True

        logger.info(f'claims: {claims}')
        logger.info(f'is affiliated: {affiliated}')

        return verified and affiliated
