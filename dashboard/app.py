"""O navegador recebe HTML. Somente este backend consulta a API interna."""
import math
import os
from datetime import datetime

import requests
from flask import Flask, jsonify, render_template


def valid_reading(data):
    if not isinstance(data, dict) or data.get("estado") not in ("NORMAL", "ALERTA"):
        return False
    return all(type(data.get(k)) in (int, float) and math.isfinite(data[k]) and low <= data[k] <= high
               for k, low, high in (("temperatura", -40, 80), ("umidade", 0, 100)))


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(API_URL=os.getenv("API_URL", "http://api:5000/dados"),
                            API_TIMEOUT=3)
    if config:
        app.config.update(config)

    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def index():
        reading, message, received_at = None, "Aguardando dados", None
        detail = "Inicie a simulação no Wokwi e aguarde a próxima publicação."
        try:
            response = requests.get(app.config["API_URL"], timeout=app.config["API_TIMEOUT"])
            if response.status_code == 200:
                data = response.json()
                if valid_reading(data):
                    reading = data
                    message = data["estado"]
                    detail = ("Temperatura dentro do limite de operação." if message == "NORMAL"
                              else "Temperatura acima de 35 °C. Verifique o ambiente.")
                    received_at = datetime.now().astimezone().strftime("%d/%m/%Y · %H:%M:%S %Z")
                else:
                    detail = "A API retornou uma leitura inválida. Tente atualizar novamente."
            elif response.status_code != 503:
                detail = "A API está temporariamente indisponível. Tente atualizar novamente."
        except (requests.RequestException, ValueError):
            detail = "Sem comunicação com a API. Tente atualizar em alguns instantes."
        return render_template("index.html", reading=reading, message=message,
                               detail=detail, consulted_at=received_at)

    @app.get("/health")
    def health():
        return jsonify(servico="dashboard", status="ok")

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5001, debug=False, use_reloader=False)
