# Vídeo simples de funcionamento

Arquivo: `video/CP06_Smart_Factory_Simples.mp4`. Duração: **2 minutos**. H.264, 1280×960, 24 fps no arquivo final, sem áudio.

Versão simplificada solicitada: apenas as telas reais do Docker Desktop, API, dashboard e Wokwi, com cortes simples. Sem apresentação, narração, legendas, títulos ou molduras adicionados.

A captura das páginas foi feita a 2 quadros por segundo em 16/10/2026. O arquivo final repete os quadros para reprodução a 24 fps. O Docker aparece em uma captura estática de 10 segundos. As demais cenas preservam o tempo das capturas; há cortes entre as etapas.

Ordem: contêineres em execução; API e dashboard aguardando dados; início do Wokwi; 30 → 35 → 36 → 30 °C. Em cada temperatura, aparecem circuito e LEDs, JSON da API e atualização do dashboard. A umidade permanece em 60%. Os valores são da simulação real do ESP32, enviados pelo HiveMQ e recebidos pelos contêineres.

A API foi reiniciada com o Wokwi parado antes da captura. O status 503 foi verificado por requisição real; a tela gravada mostra o JSON de espera. Esta versão concentra-se no funcionamento e não inclui explicação oral da arquitetura, dificuldade de implementação ou teste de desconexão de rede.

O arquivo foi decodificado integralmente sem erros. Metadados e quadros extraídos estão em `docs/evidencias/video/`.

O vídeo foi publicado como Não listado: https://www.youtube.com/watch?v=rveELE02XiQ. O link foi inserido no README. O projeto está no GitHub público e mantém uma cópia MP4 em video/. O acesso ao vídeo e o status Não listado foram conferidos no navegador; o endpoint público oEmbed respondeu sem autenticação.
