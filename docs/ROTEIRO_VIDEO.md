# Vídeo de demonstração · 2 a 5 minutos

Meta sugerida: 3min30s. Grave a tela com narração simples. Substitua os campos de identificação; use as falas como guia e descreva apenas o que estiver efetivamente aparecendo na sua gravação.

## Prepare a tela

- Abra terminal na pasta do projeto, Wokwi salvo, API em `http://localhost:5000/dados` e dashboard em `http://localhost:5001`.
- Use janelas lado a lado para facilitar mostrar DHT22, LEDs, JSON e dashboard.
- Confira se firmware e API usam o mesmo tópico. Pare publicadores de teste.
- Comece com Wokwi parado e API recém-iniciada, sem leituras anteriores.
- Não mostre informações pessoais além da identificação acadêmica necessária.

## 0:00–0:25 · Apresentação e dois serviços

Tela: `docker compose ps`, mostrando api e dashboard em execução e portas 5000/5001.

Fala sugerida: “Somos a equipe [nome], da turma [turma]. Esta é a CP06 Smart Factory. Usamos ESP32 com DHT22 no Wokwi, MQTT pelo HiveMQ e dois serviços Flask em contêineres separados: API e dashboard.”

## 0:25–0:45 · Antes da primeira leitura

Tela: resposta HTTP 503 da API e dashboard com “Aguardando dados”, sem medidas. Para evidenciar o status HTTP, use DevTools → Network ou `curl -i http://localhost:5000/dados` (no PowerShell, `curl.exe -i ...`).

Fala: “Antes da primeira leitura, a API responde 503 e o dashboard aguarda dados. O sistema não cria medições.”

## 0:45–1:15 · 30 °C, NORMAL

Inicie Wokwi. Defina DHT22 em **30 °C e 60%**. Aguarde conexão e próximo envio MQTT (5 segundos de simulação). Mostre LED verde aceso/vermelho apagado; consulte `/dados`; clique em Atualizar.

Fala: “A 30 graus, o ESP32 decide NORMAL e acende o LED verde. A mesma temperatura, umidade e estado chegam à API e aparecem no dashboard.”

## 1:15–1:45 · 35 °C, ainda NORMAL

Altere o sensor para **35 °C**, aguarde próximo envio, atualize API e dashboard. Mostre os dois LEDs.

Fala: “Exatamente 35 graus continua NORMAL. O alerta só acontece acima de 35.”

## 1:45–2:15 · 36 °C, ALERTA

Altere para **36 °C**, aguarde envio MQTT, atualize API e clique Atualizar. Mostre LED vermelho aceso/verde apagado, JSON ALERTA e faixa de alerta no dashboard.

Fala: “A 36 graus, o ESP32 muda localmente para ALERTA e acende o vermelho. O HiveMQ transporta o JSON. A API guarda a última leitura e o dashboard apresenta o estado recebido.”

## 2:15–2:45 · Volta a 30 °C, NORMAL

Volte para **30 °C**, aguarde envio, atualize API e dashboard. Mostre a volta do LED verde e do estado NORMAL. Mostre o campo de umidade.

Fala: “Ao voltar para 30 graus, o estado retorna a NORMAL. A umidade é exibida, mas não altera a regra dos LEDs.”

## 2:45–3:20 · Arquitetura e dificuldade

Tela: README, trecho local `isAlert`/`digitalWrite` e endereço `http://api:5000/dados` no Compose ou backend.

Fala: “O processamento na borda ocorre no ESP32. Não recebemos comandos da API para mudar os LEDs. O backend do dashboard consulta a API pela rede interna do Compose. Um cuidado da implementação foi separar as tentativas de conexão da leitura do sensor, para manter a decisão local mesmo quando a rede demora.”

## 3:20–3:40 · Encerramento

Tela: dois contêineres ativos e README com identificação e links reais.

Fala: “O repositório reúne firmware, circuito Wokwi, API, dashboard, Dockerfiles, Compose e testes. Os links da simulação e do vídeo estão no README.”

Só use a fala final após os links estarem realmente preenchidos. Publique o vídeo no YouTube como **Não listado**, copie o link real e valide em janela anônima. Não é necessário gravar este roteiro como se fosse uma demonstração já executada; a evidência deve vir da sua execução integrada.
