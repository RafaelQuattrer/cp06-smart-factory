"""API HTTP e consumidor MQTT. Nenhuma medição é criada pelo servidor."""
import atexit
import json
import logging
import math
import os
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

import paho.mqtt.client as mqtt
from flask import Flask, jsonify

LOG = logging.getLogger(__name__)
DEFAULT_TOPIC = "edge/2ano/turma-pendente/equipe-pendente/cp06-4f8ab7c291e64396/dados"


def parse_reading(payload):
    """Valida sem recalcular ou substituir o estado recebido da borda."""
    if len(payload) > 1024:
        raise ValueError("Mensagem maior que 1024 bytes")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Esperado objeto JSON")
    for key, low, high in (("temperatura", -40, 80), ("umidade", 0, 100)):
        value = data.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"Campo inválido: {key}")
    if data.get("estado") not in ("NORMAL", "ALERTA"):
        raise ValueError("Estado inválido")
    # Só os três campos do contrato são armazenados e publicados em /dados.
    return {key: data[key] for key in ("temperatura", "umidade", "estado")}


class ReadingStore:
    def __init__(self):
        self._lock = Lock()
        self._reading = None
        self._received_at = None
        self._connected = False

    def update(self, reading):
        with self._lock:
            self._reading = dict(reading)
            self._received_at = datetime.now(timezone.utc).isoformat()

    def connected(self, value):
        with self._lock:
            self._connected = value

    def snapshot(self):
        with self._lock:
            return (
                dict(self._reading) if self._reading is not None else None,
                self._received_at, self._connected,
            )


class MQTTReceiver:
    def __init__(self, store, topic, host, port, client_id):
        self.store, self.topic = store, topic
        self.host, self.port = host, port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.enable_logger(LOG)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            result, _ = client.subscribe(self.topic, qos=0)
            self.store.connected(result == mqtt.MQTT_ERR_SUCCESS)
            LOG.info("MQTT conectado; assinatura solicitada: %s", self.topic)
        else:
            self.store.connected(False)
            LOG.warning("Conexão MQTT recusada: %s", reason_code)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.store.connected(False)
        LOG.warning("MQTT desconectado: %s; reconexão automática", reason_code)

    def on_message(self, client, userdata, message):
        if message.topic != self.topic or message.retain:
            # Ignora valores antigos retidos no broker público.
            return
        try:
            reading = parse_reading(message.payload)
        except (ValueError, TypeError, UnicodeError):
            LOG.warning("Mensagem inválida descartada no tópico configurado")
            return
        self.store.update(reading)
        LOG.info("Leitura recebida: %s", reading)

    def start(self):
        self.client.connect_async(self.host, self.port, keepalive=30)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()


def create_app(start_mqtt=True, store=None, config=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config.from_mapping(
        MQTT_HOST=os.getenv("MQTT_HOST", "broker.hivemq.com"),
        MQTT_PORT=int(os.getenv("MQTT_PORT", "1883")),
        MQTT_TOPIC=os.getenv("MQTT_TOPIC", DEFAULT_TOPIC),
        MQTT_CLIENT_ID=os.getenv("MQTT_CLIENT_ID", "cp06-api-" + uuid4().hex[:10]),
    )
    if config:
        app.config.update(config)
    topic = app.config["MQTT_TOPIC"]
    if not topic or any(c in topic for c in "+#[]\x00"):
        raise ValueError("Use um tópico MQTT exclusivo, sem curingas ou colchetes")
    store = store if store is not None else ReadingStore()
    app.extensions["readings"] = store

    @app.after_request
    def no_cache(response):
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/dados")
    def dados():
        reading, _, _ = store.snapshot()
        if reading is None:
            return jsonify(mensagem="Aguardando dados do ESP32"), 503
        return jsonify(reading)

    @app.get("/health")
    def health():
        # Liveness: não depende da primeira medição nem do broker externo.
        _, received_at, connected = store.snapshot()
        return jsonify(servico="api", status="ok", mqtt_conectado=connected,
                       ultima_leitura_em=received_at)

    if start_mqtt:
        receiver = MQTTReceiver(store, topic, app.config["MQTT_HOST"],
                                app.config["MQTT_PORT"], app.config["MQTT_CLIENT_ID"])
        app.extensions["mqtt"] = receiver
        receiver.start()
        atexit.register(receiver.stop)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    create_app().run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
