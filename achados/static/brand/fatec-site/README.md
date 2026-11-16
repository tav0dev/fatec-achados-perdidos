# Referências do site da Fatec

Fonte: https://fatecitapetininga.cps.sp.gov.br/requerimento/, conferida em 15/11/2026 com REA e Chromium/Playwright, em conjunto com a imagem `Screenshot 2026-11-15 151152.png` fornecida no projeto.

- `news-1.jpg` a `news-5.jpg`: miniaturas dos cinco primeiros links do widget Notícias Recentes. Títulos e endereços estão em `data/fatec_news.json`, com data da consulta. A aplicação não consulta o portal durante o cadastro.
- `top-button.png`: https://bkpsitecpsnew.blob.core.windows.net/uploadsitecps/sites/1/2022/04/top-button.png
- `footer-background.png`: https://bkpsitecpsnew.blob.core.windows.net/uploadsitecps/sites/1/2022/07/bg-footer-ed-azul-base.png
- `government-footer.png`: https://fatecitapetininga.cps.sp.gov.br/wp-content/themes/tema-cps/images/sao-paulo/logo-rodape-governo-do-estado-sp.png
- `vlibras-access.svg`: https://vlibras.gov.br/app/assets/images/vlibras-access.svg

O botão de Libras exibe o ícone original local e explica a ativação do serviço externo. Após a ativação, carrega https://vlibras.gov.br/app/vlibras-plugin.js conforme https://vlibras.gov.br/doc/widget/installation/webpageintegration.html. Não há carregamento externo antes dessa escolha. A revisão automática de segurança rejeitou o carregamento do tradutor em páginas contendo registros; o fluxo de integração foi validado com carregador simulado e não com envio do conteúdo ao serviço real.

O rodapé reproduz a estrutura visual de contatos, redes e serviços públicos. Os créditos continuam identificando os autores do projeto acadêmico. Selos de certificação do portal oficial não foram aplicados ao projeto.
