# Rastreabilidade do enunciado

Base: PDF fornecido *CP06 - Smart Factory*, 4 páginas. A tabela indica implementação e como conferir; presença de código não significa demonstração integrada executada. Resultados efetivos ficam em `VALIDACAO.md`.

| Exigência | Implementação | Conferência |
|---|---|---|
| ESP32, DHT22, 2 LEDs com resistores | firmware/smart_factory/diagram.json | Inspeção estrutural; simulação manual |
| Decisão local >35 e exatamente 35 normal | edge_logic.h, smart_factory.ino | Teste C++; sequência Wokwi |
| Umidade não decide estado | isAlert recebe somente temperatura | Fonte e teste manual |
| Wi-Fi e publicação a cada 5 segundos | config.h e tarefa de rede | Compilação e serial no Wokwi |
| HiveMQ público 1883, sem broker próprio | Firmware, API e Compose | Dois serviços; logs MQTT |
| Tópico exclusivo igual e documentado | config.h, API, Compose, README | Teste de consistência |
| Clientes ESP32 e API distintos | Prefixos e IDs aleatórios diferentes | Fonte e logs |
| JSON com números e estado | Firmware e parse_reading | Testes de contrato |
| API Flask porta 5000 e memória | api/app.py e Dockerfile | Testes HTTP e Compose |
| /dados 503 antes da primeira leitura | create_app → dados | Teste automatizado exato |
| Dashboard Flask porta 5001 | dashboard/app.py e Dockerfile | Testes HTTP e Compose |
| Backend consulta http://api:5000/dados | requests.get no backend | Teste de chamada; Compose |
| Botão Atualizar e estados/medidas | Template HTML e formulário GET | Teste de interface |
| Espera sem valores fictícios | Ramo de erro do dashboard | Testes 503/rede/JSON |
| Dois contêineres e portas/publicação | compose.yaml e Dockerfiles | Validação estrutural; Docker executado e integração verificada |
| README com equipe/links/arquitetura/dificuldade | README.md | Preenchimento final da equipe |
| Vídeo 2–5 min, 30→35→36→30 | ROTEIRO_VIDEO.md | Vídeo simples real de 2 minutos incluído |
| GitHub público, Wokwi e YouTube acessíveis | Campos do README e checklist | Publicar e testar anonimamente |

Pesos informados no PDF: borda/LEDs 2,5; MQTT 1,5; API 2,0; dashboard 1,5; Compose 1,5; documentação/links/vídeo 1,0. Extras visuais e testes não substituem funcionamento e links reais.
