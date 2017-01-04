import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated, Allow
from pyramid.session import SignedCookieSessionFactory
from passlib.apps import custom_app_context as pwd_context



class MyRoot(object):

    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, Authenticated, "add"),
    ]


def check_credentials(username, password):
    """Check user credentials to determine access; returns a boolean."""
    if username and password:
        if username == os.environ["AUTH_USERNAME"]:
            if pwd_context.verify(password, os.environ["AUTH_PASSWORD"]):
                return True
    return False


def includeme(config):
    """Establish Pyramid security configuration."""
    auth_secret = os.environ["AUTH_SECRET"]
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg="sha512"
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(MyRoot)

    # Session stuff for CSRF Protection
    session_secret = os.environ.get("SESSION_SECRET", "itsasecret")
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)
