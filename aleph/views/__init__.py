from aleph import signals
from aleph.assets import assets, compile_assets  # noqa
from aleph.views.base_api import blueprint as base_api
from aleph.views.cache import blueprint as cache_api
from aleph.views.documents_api import blueprint as documents_api
from aleph.views.search_api import blueprint as search_api
from aleph.views.graph_api import blueprint as graph_api
from aleph.views.sessions_api import blueprint as sessions_api
from aleph.views.roles_api import blueprint as roles_api
from aleph.views.collections_api import blueprint as collections_api
from aleph.views.entities_api import blueprint as entities_api
from aleph.views.exports_api import blueprint as exports_api
from aleph.views.sources_api import blueprint as sources_api
from aleph.views.alerts_api import blueprint as alerts_api
from aleph.views.crawlers_api import blueprint as crawlers_api
from aleph.views.openoil_api import blueprint as openoil_api
from aleph.views.clients import blueprint as clients_ui

def mount_app_blueprints(app):
    app.register_blueprint(base_api)
    app.register_blueprint(cache_api)
    app.register_blueprint(documents_api)
    app.register_blueprint(search_api)
    app.register_blueprint(graph_api)
    app.register_blueprint(sessions_api)
    app.register_blueprint(roles_api)
    app.register_blueprint(collections_api)
    app.register_blueprint(entities_api)
    app.register_blueprint(exports_api)
    app.register_blueprint(sources_api)
    app.register_blueprint(alerts_api)
    app.register_blueprint(crawlers_api)
    app.register_blueprint(openoil_api)
    app.register_blueprint(clients_ui) # XXX this should be moved away into using signals
    signals.register_blueprints.send(app=app)
    compile_assets(app)
