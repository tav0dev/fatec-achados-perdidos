# Arquivos do tema Governo de SP / CPS

Copiados sem alterações do tema publicado no site da Fatec Itapetininga, inspecionado com REA e Chromium em 15/11/2026.

- Origem das imagens: https://fatecitapetininga.cps.sp.gov.br/wp-content/themes/tema-cps/images/sao-paulo/
- Origem do SVG de filtros: https://fatecitapetininga.cps.sp.gov.br/wp-content/themes/tema-cps/presets/filters/filters.svg
- Referência da disposição: https://fatecitapetininga.cps.sp.gov.br/wp-content/themes/tema-cps/css/sao-paulo/topo-padrao-govsp.min.css
- Referência dos perfis: https://fatecitapetininga.cps.sp.gov.br/wp-content/themes/tema-cps/presets/deuteranopia.css e os demais presets do mesmo diretório.

`color-filters.svg` é a cópia original `filters.svg`, com nome de arquivo local descritivo. Seus elementos foram inspecionados: somente svg, defs, filter e feColorMatrix. Os nomes internos das matrizes são preservados, incluindo `Protonomalia`, que o preset `protanomalia.css` usa no site original.

Os ícones de fonte e contraste acionam os controles locais da aplicação. O ícone de comunicar erros é um link externo para o portal do Governo de SP, identificado como tal. Não envia dados do cadastro. O código JavaScript do portal e seus rastreadores não são incorporados.

As marcas pertencem aos respectivos titulares. O projeto continua identificado como acadêmico no rodapé.

As oito matrizes também são incluídas diretamente no HTML por `achados/templates/color_filters.html`, com as definições originais preservadas. Isso permite aplicar cada perfil sem depender de requisições SVG durante a navegação.
