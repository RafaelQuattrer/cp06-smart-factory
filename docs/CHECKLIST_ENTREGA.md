# Checklist final

## Identificação e configuração

- [x] Integrantes e RMs informados no README; sem campos de turma/nome da equipe, conforme solicitado.
- [ ] Se personalizar o tópico, sincronizar todos os componentes e o Wokwi.
- [ ] Confirmar cliente MQTT do ESP32 diferente do cliente da API.
- [ ] Confirmar que somente dados simulados são publicados no broker público.

## Execução na máquina de apresentação

- [ ] `docker compose config` sem erros.
- [ ] `docker compose up --build` concluído.
- [ ] `docker compose ps`: api e dashboard ativos, portas 5000/5001.
- [ ] Com API reiniciada e Wokwi parado, GET /dados retorna 503 e JSON exigido.
- [ ] Dashboard mostra Aguardando dados, sem temperatura/umidade inventadas.
- [ ] Wokwi compila e inicia com ESP32, DHT22, resistores e LEDs corretos.
- [ ] Serial registra leitura local e publicação a cada 5 s de simulação com rede disponível.
- [ ] 30 °C → NORMAL: verde aceso, vermelho apagado, JSON e dashboard correspondentes.
- [ ] 35 °C → NORMAL: verde aceso, vermelho apagado, JSON e dashboard correspondentes.
- [ ] 36 °C → ALERTA: verde apagado, vermelho aceso, JSON e dashboard correspondentes.
- [ ] 30 °C → NORMAL: verde aceso, vermelho apagado, JSON e dashboard correspondentes.
- [ ] Em cada etapa, aguardar envio, consultar API e clicar Atualizar no dashboard.
- [ ] Alterar umidade e confirmar que ela não determina o estado.
- [ ] Sem rede, confirmar que LEDs ainda respondem às próximas leituras locais.
- [ ] Rodar testes automatizados e guardar o resultado da execução final.

## Publicação e entrega

- [ ] Repositório GitHub público, README na raiz e todos os arquivos incluídos.
- [ ] Projeto Wokwi salvo e link real inserido no README.
- [ ] Vídeo com 2 a 5 minutos e a sequência obrigatória completa.
- [ ] Vídeo publicado no YouTube como Não listado e link real no README.
- [ ] Abrir GitHub, Wokwi e YouTube em janela anônima, sem login/convite.
- [ ] Verificar que não restou link obrigatório ausente.
- [ ] Enviar uma única vez por equipe o link público do GitHub no canal do professor.
- [ ] Manter os três links acessíveis até o término da avaliação.

As caixas começam vazias propositalmente. Marque somente depois de verificar na execução da equipe.
