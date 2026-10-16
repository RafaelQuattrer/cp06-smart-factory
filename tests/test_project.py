"""Verificações estruturais complementares; não substituem execução Docker/Wokwi."""
import json
import re
from pathlib import Path
import yaml
from api.app import DEFAULT_TOPIC

ROOT = Path(__file__).resolve().parents[1]


def test_compose_contract():
    services = yaml.safe_load((ROOT/"compose.yaml").read_text())["services"]
    assert set(services) == {"api","dashboard"}
    assert services["api"]["ports"] == ["5000:5000"]
    assert services["dashboard"]["ports"] == ["5001:5001"]
    assert services["dashboard"]["environment"]["API_URL"] == "http://api:5000/dados"
    assert services["api"]["healthcheck"]["test"][-1].find("/health") > 0


def test_topic_matches_every_component_and_documentation():
    config = (ROOT/"firmware/smart_factory/config.h").read_text(encoding="utf-8")
    topic = re.search(r'MQTT_TOPIC\[\] = "([^"]+)"',config)[1]
    assert topic == DEFAULT_TOPIC
    for file in ("compose.yaml",".env.example","README.md"):
        assert topic in (ROOT/file).read_text(encoding="utf-8")
    assert not any(c in topic for c in "[]+#")
    assert "SAMPLE_INTERVAL_MS = 5000" in config


def test_circuit_connections():
    diagram = json.loads((ROOT/"firmware/smart_factory/diagram.json").read_text())
    types = [part["type"] for part in diagram["parts"]]
    assert types.count("wokwi-led") == 2
    assert types.count("wokwi-resistor") == 3
    wires = {(wire[0],wire[1]) for wire in diagram["connections"]}
    assert ("esp:D15","dht:SDA") in wires
    assert ("esp:D18","rg:1") in wires and ("rg:2","green:A") in wires
    assert ("esp:D19","rr:1") in wires and ("rr:2","red:A") in wires
    assert ("green:C","esp:GND.1") in wires and ("red:C","esp:GND.1") in wires


def test_gpio_names_match_the_classic_devkit_v1_board():
    diagram = json.loads((ROOT/"firmware/smart_factory/diagram.json").read_text())
    board = next(part for part in diagram["parts"] if part["id"] == "esp")
    assert board["type"] == "wokwi-esp32-devkit-v1"
    # Nesta placa, os pinos são D15/D18/D19; nomes só numéricos pertencem a outro modelo.
    allowed = {"3V3", "GND.1", "D15", "D18", "D19"}
    for wire in diagram["connections"]:
        for endpoint in wire[:2]:
            if endpoint.startswith("esp:"):
                assert endpoint.split(":",1)[1] in allowed
