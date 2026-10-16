"""QA com dados sintéticos de teste, sem MQTT, Wokwi ou Docker."""
import argparse
import json
import sys
import threading
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server
from api.app import ReadingStore, create_app as create_api
from dashboard.app import create_app as create_dashboard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser",help="Caminho opcional para chrome/chromium já instalado")
    parser.add_argument("--output",default="test-results/interface")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True,exist_ok=True)
    store = ReadingStore()
    api = make_server("127.0.0.1",0,create_api(start_mqtt=False,store=store),threaded=True)
    dashboard = make_server("127.0.0.1",0,create_dashboard({"API_URL":f"http://127.0.0.1:{api.server_port}/dados"}),threaded=True)
    for server in [api,dashboard]:
        threading.Thread(target=server.serve_forever,daemon=True).start()
    checks = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,executable_path=args.browser)
            page = browser.new_page(viewport={"width":1440,"height":1100},device_scale_factor=1)
            errors, requests = [], []
            page.on("pageerror",lambda error: errors.append(str(error)))
            page.on("request",lambda request: requests.append(request.url))
            url = f"http://127.0.0.1:{dashboard.server_port}/"
            for state,reading in [
                ("espera",None),
                ("normal",dict(temperatura=35,umidade=60,estado="NORMAL")),
                ("alerta",dict(temperatura=36,umidade=60,estado="ALERTA"))]:
                if reading:
                    store.update(reading)
                for width,height,label in [(1440,1100,"desktop"),(390,844,"mobile")]:
                    page.set_viewport_size({"width":width,"height":height})
                    page.goto(url,wait_until="networkidle")
                    assert page.locator("h2").first.inner_text() == (reading["estado"] if reading else "Aguardando dados")
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), "Overflow horizontal"
                    assert page.get_by_role("button",name="Atualizar").is_visible()
                    page.screenshot(path=str(output/f"{state}-{label}.png"),full_page=True)
                    checks.append(f"{state}-{label}: renderização e ausência de overflow OK")
            # O botão deve obter a próxima leitura, sem reiniciar a página manualmente.
            store.update(dict(temperatura=30,umidade=55,estado="NORMAL"))
            page.get_by_role("button",name="Atualizar").click()
            page.wait_for_load_state("networkidle")
            assert page.locator("h2").first.inner_text() == "NORMAL"
            assert "30,0" in page.locator(".temperature .value").inner_text()
            assert "55,0" in page.locator(".humidity .value").inner_text()
            assert all(request.startswith(url) for request in requests),requests
            assert not errors,errors
            checks.append("Atualizar: nova consulta, novos valores e estado OK; sem acesso do navegador à API")
            browser.close()
        report = {"origem":"fixtures sintéticas; não comprova ESP32, MQTT ou Docker","checks":checks,"erros":errors}
        (output/"resultado.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        api.shutdown()
        dashboard.shutdown()


if __name__ == "__main__":
    main()
