from unittest.mock import Mock, patch
import pytest
import requests
from dashboard.app import create_app


@pytest.mark.parametrize("temperature,state", [(30,"NORMAL"),(35,"NORMAL"),(36,"ALERTA"),(30,"NORMAL")])
def test_dashboard_shows_reading_and_queries_backend(temperature,state):
    response = Mock(status_code=200)
    response.json.return_value = dict(temperatura=temperature,umidade=60,estado=state)
    with patch("dashboard.app.requests.get",return_value=response) as get:
        html = create_app().test_client().get("/").get_data(as_text=True)
    get.assert_called_once_with("http://api:5000/dados",timeout=3)
    assert f"state-{state.lower()}" in html
    assert f"{temperature},0" in html and "60,0" in html
    assert "Atualizar" in html and 'method="get"' in html
    # Não existe URL interna vazada para o navegador nem acesso HTTP por JavaScript.
    assert "http://api:" not in html
    assert "fetch(" not in html
    assert "Última consulta" in html


@pytest.mark.parametrize("status",[503,500,404])
def test_waiting_on_api_failure(status):
    with patch("dashboard.app.requests.get",return_value=Mock(status_code=status)):
        html = create_app().test_client().get("/").get_data(as_text=True)
    assert "Aguardando dados" in html and 'class="state-waiting"' in html
    assert "60,0" not in html and "30,0" not in html
    assert html.count('aria-label="Sem leitura"') == 2


@pytest.mark.parametrize("error",[requests.Timeout(),requests.ConnectionError(),ValueError("bad JSON")])
def test_waiting_on_network_or_json_error(error):
    with patch("dashboard.app.requests.get",side_effect=error):
        html = create_app().test_client().get("/").get_data(as_text=True)
    assert "Aguardando dados" in html
    assert 'class="state-waiting"' in html


@pytest.mark.parametrize("data",[{},[],None,
    dict(temperatura=30,umidade=True,estado="NORMAL"),
    dict(temperatura="30",umidade=60,estado="NORMAL"),
    dict(temperatura=30,umidade=120,estado="NORMAL"),
    dict(temperatura=30,umidade=60,estado="ERRO"),
    dict(temperatura=float("inf"),umidade=60,estado="NORMAL")])
def test_no_fake_values_on_invalid_contract(data):
    response = Mock(status_code=200)
    response.json.return_value = data
    with patch("dashboard.app.requests.get",return_value=response):
        html = create_app().test_client().get("/").get_data(as_text=True)
    assert "Aguardando dados" in html
    assert "60,0" not in html


def test_refresh_makes_new_server_request_and_does_not_keep_stale_values():
    good = Mock(status_code=200)
    good.json.return_value = dict(temperatura=36,umidade=60,estado="ALERTA")
    client = create_app().test_client()
    with patch("dashboard.app.requests.get",side_effect=[good,Mock(status_code=503)]) as get:
        first = client.get("/")
        second = client.get("/")
    assert get.call_count == 2
    assert "36,0" in first.get_data(as_text=True)
    assert "36,0" not in second.get_data(as_text=True)
    assert second.headers["Cache-Control"] == "no-store"


def test_static_and_health():
    client = create_app().test_client()
    for path in ("/health","/static/style.css","/static/factory.svg"):
        assert client.get(path).status_code == 200
