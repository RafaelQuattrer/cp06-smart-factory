"""Atualiza os pontos de configuração e a documentação sem dependências externas."""
import argparse
import re
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def segment(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,39}",value):
        raise argparse.ArgumentTypeError("Use 1 a 40 letras minúsculas, números ou hífens; inicie com letra/número")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turma",required=True,type=segment)
    parser.add_argument("--equipe",required=True,type=segment)
    args = parser.parse_args()
    config = ROOT/"firmware/smart_factory/config.h"
    old = re.search(r'MQTT_TOPIC\[\] = "([^"]+)"',config.read_text(encoding="utf-8"))[1]
    new = f"edge/2ano/{args.turma}/{args.equipe}/cp06-{uuid4().hex[:16]}/dados"
    files = [config,ROOT/"api/app.py",ROOT/"compose.yaml",ROOT/".env.example",ROOT/"README.md"]
    # Confere tudo antes de começar a escrever.
    updates = []
    for path in files:
        source = path.read_text(encoding="utf-8")
        if old not in source:
            raise SystemExit(f"Tópico divergente em {path.name}; alinhe antes de executar")
        updates.append((path,source.replace(old,new)))
    env = ROOT/".env"
    if env.exists():
        source = env.read_text(encoding="utf-8")
        if re.search(r"^MQTT_TOPIC=",source,re.M):
            source = re.sub(r"^MQTT_TOPIC=.*$",f"MQTT_TOPIC={new}",source,flags=re.M)
        else:
            source += f"\nMQTT_TOPIC={new}\n"
        updates.append((env,source))
    for path,source in updates:
        path.write_text(source,encoding="utf-8")
    print(new)
    print("Recopie config.h para o Wokwi e execute docker compose up --build --force-recreate.")


if __name__ == "__main__":
    main()
