# Registro de validação

Data: **16/10/2026**. Este documento registra verificações realmente executadas durante a preparação do pacote. Diferencia testes com fixtures, transporte externo real e etapas que dependem da execução final da equipe.

## Resultados executados

| Verificação | Resultado | Limite da evidência |
|---|---|---|
| Python / pytest | **55 testes aprovados**, 1,00 s | Inclui verificação dos nomes de GPIOs do modelo ESP32 do diagrama |
| HiveMQ público real | **Aprovado**, API inicialmente 503; sequência 30→35→36→30 refletida na API e dashboard | Publicador sintético, tópico aleatório isolado; aplicações locais, sem ESP32 e sem Docker |
| Wokwi → HiveMQ → API → dashboard | **Aprovado**, sequência 30→35→36→30, com LEDs e valores correspondentes | ESP32 efetivamente simulado no Wokwi; API e dashboard executados com Python local, sem Docker |
| Interface em Chromium | **6 cenários aprovados**: espera, NORMAL e ALERTA em 1440×1100 e 390×844 | Fixtures locais; não são leituras capturadas do Wokwi |
| Botão Atualizar | **Aprovado**: mudou de ALERTA para NORMAL com nova leitura e umidade | HTTP real entre aplicações locais de teste |
| Navegador acessando só dashboard | **Aprovado** no teste visual, sem acesso direto à API | A API é consultada pelo backend |
| Erros JavaScript / largura | **Nenhum erro**; sem overflow horizontal nos seis cenários | Inspeção automatizada e revisão das capturas |
| Compilação ESP32 | **Aprovada** via PlatformIO / espressif32 6.12.0 | Compilação gera firmware; não executa circuito |
| Regra local em C++ | **6 asserções estáticas aprovadas** pelo compilador ESP32 | Verifica 30, 35, 35,01, 36, −40 e 80 °C na mesma função usada no firmware |
| Contrato Compose | **Aprovado** com Docker Compose oficial v2.39.4, `config --quiet`, exit 0 | Não constrói nem executa contêineres |
| Construção e execução Docker | **Aprovadas**, API e dashboard em contêineres distintos e saudáveis | Docker Desktop 4.95.0, Engine 29.8.2; imagem Python 3.12.12-slim |
| Espera inicial em Docker | **Aprovada**, API 503 com o JSON exato e dashboard sem medidas | Verificado também de dentro do contêiner dashboard, consultando http://api:5000/dados |
| Wokwi → HiveMQ → contêiner API → contêiner dashboard | **Aprovado**, 30→35→36→30 com NORMAL→NORMAL→ALERTA→NORMAL | ESP32 simulado como publicador real; LEDs conferidos, HTTP 200 e chamada interna verificada em cada etapa |
| Personalização do tópico | **Aprovada** em cópia temporária, com os cinco arquivos sincronizados | O tópico original do pacote foi preservado |

O validador Compose temporário foi obtido da distribuição oficial e teve o SHA-256 conferido. Posteriormente, o Docker Desktop 4.95.0 foi instalado, o recurso de virtualização foi ativado e o mecanismo iniciou com Engine 29.8.2. Foi executado `docker compose up --build -d` com sucesso. Os serviços `api` e `dashboard` ficaram `running` e `healthy`, com as portas 5000 e 5001 publicadas. A API retornou o 503 exigido antes da primeira leitura, e a consulta interna do dashboard foi confirmada no endereço `http://api:5000/dados`.

Na compilação do ESP32, a preparação do ambiente precisou instalar as ferramentas e o pip temporário. O caminho longo do projeto no Windows também causou `CreateProcess`; a compilação passou usando um mapeamento temporário de caminho curto, removido ao final. Em outra máquina Windows, prefira extrair o projeto em um caminho curto.

Na execução posterior do Wokwi, foi identificado e corrigido um erro nos nomes de conexão do diagrama: o modelo clássico `wokwi-esp32-devkit-v1` usa `D15`, `D18` e `D19`, e não `15`, `18` e `19`. O pacote e o projeto público foram atualizados. Depois da correção, o DHT22 passou a fornecer leituras válidas, os LEDs responderam e o JSON chegou ao dashboard pelo HiveMQ real. Um teste de regressão foi acrescentado. Projeto salvo: https://wokwi.com/projects/478070654175725569.

## Evidências incluídas

- `evidencias/testes-python.txt`: resultado do pytest.
- `evidencias/hivemq-integracao.json`: sequência e origem dos dados no teste externo real.
- `evidencias/compose-config.txt`: versão, checksum e resultado do validador Compose.
- `evidencias/firmware-compilacao.txt`: compilador, bibliotecas e resumo da compilação final.
- `evidencias/interface/resultado.json`: verificações da interface.
- `evidencias/interface/*.png`: capturas desktop e celular, **com dados sintéticos de teste**.
- `evidencias/wokwi-local/`: sequência JSON e capturas de **leituras efetivamente produzidas pelo ESP32 no Wokwi**, com aplicações locais. Essas imagens não comprovam contêineres Docker.
- `evidencias/docker/`: estado real dos contêineres, respostas HTTP e capturas do dashboard executado no Docker; o script de verificação apenas lê os dados atuais e não publica medições.

As evidências textuais são registros dos resultados observados, não declarações de execução do sistema inteiro. Os scripts e comandos estão no projeto para reprodução. Dependências de compilação e cache não são incluídos no ZIP.

## Pendências antes da entrega acadêmica

- A captura dos dois contêineres e de **30 °C → 35 °C → 36 °C → 30 °C** com o ESP32 como publicador foi concluída em 16/10/2026. Consulte [VIDEO_GERADO.md](VIDEO_GERADO.md).
- Conferir o comportamento local sem rede e o efeito da umidade na leitura, sem alterar o critério de estado.
- Vídeo simples de 2 minutos publicado como Não listado; link real inserido no README e conferido.
- GitHub público, integrantes/RMs e links reais de Wokwi e YouTube configurados e verificados.
- Conferir novamente os links antes de enviar o repositório público no canal do professor.

O teste MQTT sintético e as capturas em `interface/` usam fixtures. As capturas em `wokwi-local/` vêm da execução do firmware no simulador com aplicações Python locais. As evidências em `docker/` foram obtidas após iniciar os contêineres reais. O vídeo em `video/` usa capturas da execução com Docker e Wokwi. A demonstração está publicada como Não listado e os links estão preenchidos. Resta enviar o link do repositório no canal do professor.
