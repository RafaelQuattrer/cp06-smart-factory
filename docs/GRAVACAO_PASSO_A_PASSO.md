# Passo a passo para gravar a tela

## Antes de apertar Gravar

1. Use o projeto preparado: https://wokwi.com/projects/478070654175725569.
2. Em um computador com Docker Desktop instalado e iniciado, abra PowerShell na pasta do projeto e execute `docker compose up --build -d`.
3. Execute `docker compose ps`. Devem aparecer **api** e **dashboard** ativos, portas 5000 e 5001.
4. Abra a API em http://localhost:5000/dados e o dashboard em http://localhost:5001.
5. No Wokwi, o triângulo verde inicia a simulação. O quadrado cinza para; o botão de pausa congela a execução. Clique no DHT22 branco para abrir os controles de temperatura e umidade.
6. Antes de gravar a espera inicial, pare Wokwi e execute `docker compose restart api`. Sem nova leitura, a API deve mostrar 503 e a página deve mostrar Aguardando dados.

Se as aplicações já estiverem rodando diretamente com Python, encerre esses dois processos antes de iniciar o Docker, para liberar as portas 5000/5001. A execução Python foi usada para teste; a gravação solicitada pelo professor deve mostrar os serviços Docker.

## Durante a gravação (aproximadamente 3 minutos)

| Momento | Ação na tela | Fala curta sugerida |
|---|---|---|
| Início | Mostrar `docker compose ps` | “Esta é a Smart Factory. API e dashboard estão em contêineres separados.” |
| Espera | Mostrar API sem dados e dashboard aguardando | “Antes da primeira leitura, a API responde 503. Não mostramos medições inventadas.” |
| 30 °C | Iniciar Wokwi. Clicar no sensor, deixar 30 °C e umidade 60%. Esperar o próximo `[MQTT ENVIADO]`. Mostrar LED verde, atualizar a aba da API e clicar Atualizar no dashboard. | “A 30 graus, o estado é NORMAL e o LED verde acende.” |
| 35 °C | Clicar no controle de temperatura. Usar as setas do teclado para chegar a exatamente 35,0 °C, se for mais fácil que arrastar. Esperar envio, atualizar API e dashboard. | “Exatamente 35 graus ainda é NORMAL.” |
| 36 °C | Mudar para 36,0 °C; esperar envio; mostrar vermelho aceso/verde apagado; atualizar API e dashboard. | “Acima de 35 graus, o ESP32 decide ALERTA localmente.” |
| Volta a 30 °C | Mudar para 30,0 °C; esperar envio; mostrar verde aceso; atualizar API e dashboard. | “Ao voltar a 30 graus, o sistema retorna a NORMAL.” |
| Encerramento | Mostrar README ou fluxo de arquitetura | “O ESP32 controla os LEDs. O HiveMQ transporta os dados, a API recebe e o dashboard apresenta. A umidade é exibida e não altera o estado.” |

Espere **uma publicação nova em cada etapa**, em geral 5 segundos de simulação. Não troque de temperatura antes de mostrar os três pontos: LED, JSON da API e dashboard. Mantenha o total entre 2 e 5 minutos. Você não precisa aparecer na câmera; use gravação de tela com uma breve explicação.

Depois publique no YouTube como **Não listado**, coloque o link real no README e confira em janela anônima.
