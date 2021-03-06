"""Adding routes for the configuration to find."""


def includeme(config):
    """Add routes for the configuration to find."""
    config.add_static_view(name='static', path='learning_journal:static', cache_max_age=3600)
    config.add_route("list", "/")
    config.add_route("create", "/journal/new-entry")
    config.add_route("detail", "/journal/{id:\d+}")
    config.add_route("edit", "/journal/{id:\d+}/edit-entry")
    config.add_route("about", "/about")
    config.add_route("portfolio", "/portfolio")
    config.add_route("login", "/login")
    config.add_route("logout", "/logout")
    config.add_route('delete', '/journal/delete/{id:\d+}')
    config.add_route('api_list', '/api/list')
