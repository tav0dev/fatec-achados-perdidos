import os
import secrets

def create_app(test_config=None):
    from flask import Flask, render_template
    from pymongo.errors import PyMongoError

    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
        MONGO_DB=os.environ.get("MONGO_DB", "fatec_achados_perdidos"),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if test_config:
        app.config.update(test_config)
    from .database import connect_database
    if app.config.get("TEST_COLLECTION") is not None:
        app.extensions["achados_collection"] = app.config["TEST_COLLECTION"]
    else:
        connect_database(app)
    from .views import bp
    app.register_blueprint(bp)

    @app.template_filter("datebr")
    def datebr(value):
        return value.strftime("%d/%m/%Y") if value else "—"

    @app.errorhandler(PyMongoError)
    def database_error(error):
        app.logger.error("Falha de acesso ao MongoDB: %s", type(error).__name__)
        return render_template("error.html", title="Conecte seu MongoDB", message="Não foi possível acessar o banco de dados. Inicie o serviço MongoDB no Windows e confira a conexão localhost:27017 no Compass.", database_error=True), 503

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", title="Registro não encontrado", message="Este endereço ou item não existe. Volte para o mural e tente novamente."), 404

    @app.errorhandler(400)
    def invalid_form(error):
        return render_template("error.html", title="Recarregue o formulário", message=error.description), 400

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    return app
