"""Teste externo opcional. Publica APENAS dados sintéticos em tópico aleatório.

Executa API e dashboard locais em portas efêmeras e usa o HiveMQ real.
Não executa broker e não comprova o funcionamento do ESP32/Wokwi/Docker.
"""
import json
import sys
import threading
import time
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paho.mqtt.client as mqtt
import requests
from werkzeug.serving import make_server
from api.app import create_app as create_api
from dashboard.app import create_app as create_dashboard


def wait_for(predicate, seconds=25):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(.2)
    raise TimeoutError("HiveMQ não respondeu no prazo do teste")


def main():
    topic = "edge/2ano/teste-automatizado/cp06/" + uuid4().hex + "/dados"
    api = create_api(config={"MQTT_TOPIC":topic})
    api_server = make_server("127.0.0.1",0,api,threaded=True)
    api_url = f"http://127.0.0.1:{api_server.server_port}/dados"
    dashboard = create_dashboard({"API_URL":api_url})
    dashboard_server = make_server("127.0.0.1",0,dashboard,threaded=True)
    servers = [api_server,dashboard_server]
    publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id="cp06-test-"+uuid4().hex[:10])
    for server in servers:
        threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        assert requests.get(api_url,timeout=3).status_code == 503
        wait_for(api.extensions["mqtt"].client.is_connected)
        # Confirma assinatura antes de iniciar a sequência (sonda isolada do teste).
        publisher.connect("broker.hivemq.com",1883,30)
        publisher.loop_start()
        wait_for(publisher.is_connected)
        def ready():
            publisher.publish(topic,json.dumps(dict(temperatura=20,umidade=50,estado="NORMAL")))
            return requests.get(api_url,timeout=3).status_code == 200
        wait_for(ready)
        results = []
        for temperature,state in [(30,"NORMAL"),(35,"NORMAL"),(36,"ALERTA"),(30,"NORMAL")]:
            reading = dict(temperatura=temperature,umidade=60,estado=state)
            publisher.publish(topic,json.dumps(reading),qos=1).wait_for_publish(timeout=5)
            wait_for(lambda: requests.get(api_url,timeout=3).json() == reading)
            response = requests.get(f"http://127.0.0.1:{dashboard_server.server_port}/",timeout=5)
            assert response.status_code == 200
            assert f'state-{state.lower()}' in response.text
            assert f"{temperature},0" in response.text
            results.append(reading)
        print(json.dumps({"resultado":"APROVADO","origem":"publicador sintético de teste, não ESP32",
                          "broker":"broker.hivemq.com:1883","topico":topic,"sequencia":results},ensure_ascii=False,indent=2))
    finally:
        publisher.disconnect()
        publisher.loop_stop()
        api.extensions["mqtt"].stop()
        for server in servers:
            server.shutdown()


if __name__ == "__main__":
    main()
