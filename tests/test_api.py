import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from api.app import MQTTReceiver, ReadingStore, create_app, parse_reading


def payload(t=30, h=60, state="NORMAL"):
    return json.dumps(dict(temperatura=t, umidade=h, estado=state)).encode()


def test_before_first_reading_is_exact_503():
    response = create_app(start_mqtt=False).test_client().get("/dados")
    assert response.status_code == 503
    assert response.json == {"mensagem": "Aguardando dados do ESP32"}
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("temperature,state", [(30,"NORMAL"),(35,"NORMAL"),(36,"ALERTA"),(30,"NORMAL")])
def test_valid_reading(temperature, state):
    store = ReadingStore()
    store.update(parse_reading(payload(temperature, state=state)))
    response = create_app(start_mqtt=False, store=store).test_client().get("/dados")
    assert response.status_code == 200
    assert response.json == dict(temperatura=temperature, umidade=60, estado=state)


@pytest.mark.parametrize("invalid", [b"not json", b"\xff", b"[]", b"null", b"{}", b"x"*1025,
    payload(t=True),payload(t="30"),payload(t=float("nan")),payload(t=float("inf")),
    payload(t=-41),payload(t=81),payload(h=-1),payload(h=101),payload(state="normal"),
    payload(h=None),payload(state="ERRO")])
def test_reject_invalid_messages(invalid):
    with pytest.raises((ValueError, UnicodeError)):
        parse_reading(invalid)


def test_state_is_from_esp32_not_recalculated_by_api():
    assert parse_reading(payload(t=30, state="ALERTA"))["estado"] == "ALERTA"


def test_receiver_bad_retained_wrong_topic_do_not_replace_last():
    store = ReadingStore()
    receiver = MQTTReceiver(store,"edge/test/dados","broker.hivemq.com",1883,"cp06-unit-test")
    def send(topic="edge/test/dados", body=payload(), retain=False):
        receiver.on_message(None,None,SimpleNamespace(topic=topic,payload=body,retain=retain))
    send(retain=True)
    send(topic="other")
    send(body=b"bad")
    assert store.snapshot()[0] is None
    send()
    send(body=payload(h=999))
    assert store.snapshot()[0] == dict(temperatura=30,umidade=60,estado="NORMAL")


def test_reconnect_subscribes_and_disconnect_keeps_reading():
    store = ReadingStore()
    store.update(parse_reading(payload()))
    receiver = MQTTReceiver(store,"edge/test/dados","broker.hivemq.com",1883,"cp06-unit-test")
    client = Mock()
    client.subscribe.return_value = (0,1)
    receiver.on_connect(client,None,None,0,None)
    receiver.on_connect(client,None,None,0,None)
    assert client.subscribe.call_count == 2
    assert store.snapshot()[2] is True
    receiver.on_disconnect(client,None,None,1,None)
    assert store.snapshot()[2] is False
    assert store.snapshot()[0]["temperatura"] == 30


def test_failed_connect_and_health_without_reading():
    store = ReadingStore()
    receiver = MQTTReceiver(store,"edge/test/dados","broker.hivemq.com",1883,"cp06-unit-test")
    client = Mock()
    receiver.on_connect(client,None,None,5,None)
    client.subscribe.assert_not_called()
    response = create_app(start_mqtt=False,store=store).test_client().get("/health")
    assert response.status_code == 200
    assert response.json["mqtt_conectado"] is False
    assert response.json["ultima_leitura_em"] is None


def test_store_does_not_expose_mutable_reading():
    store = ReadingStore()
    data = parse_reading(payload())
    store.update(data)
    data["estado"] = "ALERTA"
    snapshot = store.snapshot()[0]
    snapshot["temperatura"] = 99
    assert store.snapshot()[0] == dict(temperatura=30,umidade=60,estado="NORMAL")


@pytest.mark.parametrize("topic",["", "edge/+/dados", "edge/#", "edge/[turma]/dados"])
def test_invalid_config_topic(topic):
    with pytest.raises(ValueError):
        create_app(start_mqtt=False,config={"MQTT_TOPIC":topic})
