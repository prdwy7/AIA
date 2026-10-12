# Keycloak realm — AI Kiosk (S23)
#
# Identity for all central services. Import with:
#   Keycloak Admin → realm → import `ai-kiosk-realm.json` (or mount in
#   dev-central.yml, which binds infra/keycloak to /opt/keycloak/data/import).
#
# Roles: farmer (pseudonymous, no account at kiosk — case-scoped tokens),
# operator, scientist, admin, auditor. Device identity is mTLS client certs
# (not OIDC) for kiosk sync. Invariants (docs/02 §S23): MFA (TOTP) for all
# privileged roles; farmer never stores a name — pseudonymous `farmer_ref` only;
# quarterly RBAC access review.
