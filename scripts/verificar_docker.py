"""Confere os contêineres e as leituras atuais sem publicar dados de teste."""
import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def http(url):
    try:
        with urlopen(url, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as response:
        return response.code, response.read().decode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--espera", action="store_true")
    group.add_argument("--temperatura", type=float)
    parser.add_argument("--umidade", type=float, default=60)
    args = parser.parse_args()
    docker = shutil.which("docker")
    if not docker:
        candidate = Path(os.getenv("LOCALAPPDATA", ""))/"Programs/DockerDesktop/resources/bin/docker.exe"
        if not candidate.exists():
            raise SystemExit("Docker não encontrado. Abra um terminal após a instalação.")
        docker = str(candidate)

    def run(*command):
        return subprocess.run([docker, *command], cwd=ROOT, check=True,
                              capture_output=True, text=True, encoding="utf-8").stdout

    raw = run("compose", "ps", "--format", "json").strip()
    services = json.loads(raw) if raw.startswith("[") else [json.loads(line) for line in raw.splitlines()]
    assert {s["Service"] for s in services} == {"api", "dashboard"}, services
    assert all(s["State"] == "running" and s["Health"] == "healthy" for s in services), services
    api_status, api_body = http("http://127.0.0.1:5000/dados")
    api_data = json.loads(api_body)
    dashboard_status, html = http("http://127.0.0.1:5001/")
    assert dashboard_status == 200
    internal_script = (
        'import os,json,requests; u=os.environ["API_URL"]; '
        'r=requests.get(u,timeout=5); '
        'print(json.dumps({"url":u,"status":r.status_code,"dados":r.json()}))'
    )
    internal = json.loads(run("compose", "exec", "-T", "dashboard", "python", "-c", internal_script))
    assert internal["url"] == "http://api:5000/dados", internal
    if args.espera:
        expected = {"mensagem":"Aguardando dados do ESP32"}
        assert api_status == internal["status"] == 503
        assert api_data == internal["dados"] == expected
        assert "Aguardando dados" in html and 'class="state-waiting"' in html
        assert html.count('aria-label="Sem leitura"') == 2
    else:
        expected = dict(temperatura=args.temperatura, umidade=args.umidade,
                        estado="ALERTA" if args.temperatura > 35 else "NORMAL")
        assert api_status == internal["status"] == 200
        assert api_data == internal["dados"] == expected, (api_data, internal)
        assert f'state-{expected["estado"].lower()}' in html
        assert f"{args.temperatura:.1f}".replace(".", ",") in html
    report = {
        "consulta_em": datetime.now().astimezone().isoformat(),
        "origem": "Contêineres Docker reais; verificação somente de leitura; nenhum dado publicado pelo teste",
        "servicos": [{key:s[key] for key in ("Name","Service","State","Health")} for s in services],
        "api_http": api_status, "api_dados": api_data,
        "dashboard_http": dashboard_status, "consulta_interna_dashboard": internal,
        "resultado": "APROVADO",
    }
    output = ROOT/"docs/evidencias/docker"
    output.mkdir(parents=True, exist_ok=True)
    history_file = output/"verificacoes.json"
    history = json.loads(history_file.read_text(encoding="utf-8")) if history_file.exists() else []
    history.append(report)
    history_file.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
