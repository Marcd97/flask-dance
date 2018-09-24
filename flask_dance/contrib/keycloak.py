from functools import partial
from flask.globals import LocalProxy, _lookup_app_object
from flask_dance.consumer import OAuth2ConsumerBlueprint

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


def make_keycloak_blueprint(
        base_url, authorization_url, token_url,
        client_id=None, client_secret=None, scope=None, redirect_url=None,
        redirect_to=None, login_url=None, authorized_url=None,
        session_class=None, backend=None):
    """
    Make a blueprint for authenticating with KeyCloak using OAuth 2. This requires
    a client ID and client secret from KeyCloak. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables KEYCLOAK_OAUTH_CLIENT_ID and KEYCLOAK_OAUTH_CLIENT_SECRET.

    Args:
        client_id (str): The client ID for your application on KeyCloak.
        client_secret (str): The client secret for your application on KeyCloak
        scope (str, optional): comma-separated list of scopes for the OAuth token
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/keycloak``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/keycloak/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth2Session`.
        backend: A storage backend class, or an instance of a storage
                backend class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.backend.session.SessionBackend`.

    :rtype: :class:`~flask_dance.consumer.OAuth2ConsumerBlueprint`
    :returns: A :ref:`blueprint <flask:blueprints>` to attach to your Flask app.
    """
    keycloak_bp = OAuth2ConsumerBlueprint("keycloak", __name__,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        base_url=base_url,
        authorization_url=authorization_url,
        token_url=token_url,
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        backend=backend,
    )
    keycloak_bp.from_config["client_id"] = "KEYCLOAK_OAUTH_CLIENT_ID"
    keycloak_bp.from_config["client_secret"] = "KEYCLOAK_OAUTH_CLIENT_SECRET"

    @keycloak_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.keycloak_oauth = keycloak_bp.session

    return keycloak_bp


keycloak = LocalProxy(partial(_lookup_app_object, "keycloak_oauth"))
