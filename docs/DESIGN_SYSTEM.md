# Design system — Achados e Perdidos

Revisão de 15/11/2026. Projeto acadêmico para a comunidade da Fatec Itapetininga.

## Referência visual

O [site oficial da Fatec Itapetininga](https://fatecitapetininga.cps.sp.gov.br/) foi inspecionado com REA e Chromium/Playwright. A interface adota seu cabeçalho branco, marcas originais, menu horizontal vermelho e as famílias Roboto e Roboto Slab. As fontes dos arquivos utilizados estão nos READMEs das pastas de imagens e fontes.

Esses elementos são referências do tema web observado. As regras de identidade do CPS permanecem distintas das decisões de interface deste projeto; não há indicação de homologação institucional.

## Marca

- PNG original Fatec + CPS: `achados/static/brand/fatec-itapetininga.png`.
- SVG original CPS: `achados/static/brand/cps.svg`, usado como ícone da aba.
- Imagem do Governo de SP e ícones originais do tema: `achados/static/brand/govsp/`.
- As marcas ficam sobre branco, com proporção original, sem recoloração ou efeitos, inclusive no modo de alto contraste.
- O nome da aplicação e a identificação de projeto acadêmico são elementos separados.
- Fontes e endereços dos arquivos em [brand/README.md](../achados/static/brand/README.md).

## Cores

| Token | Valor padrão | Uso |
| --- | --- | --- |
| `--brand` | `#B20000` | Vermelho institucional; menu e ações |
| `--heading` | `#005C6D` | Azul-petróleo observado no tema da Fatec; títulos |
| `--institutional-gray` | `#666666` | Referência institucional |
| `--ink` | `#26343A` | Texto principal |
| `--muted` | `#536168` | Texto auxiliar |
| `--background`, `--surface` | `#FFFFFF` | Fundo e superfícies |
| `--soft` | `#F3F6F7` | Busca, agrupamentos e rodapé |
| `--border` | `#D8DFE2` | Separação de superfícies |
| `--control-border` | `#7E8A90` | Limites dos campos |
| `--focus` | `#005FCC` | Foco de teclado |
| `--success` | `#126354` | Devolução e item encontrado |
| `--attention` | `#804600` | Item perdido e atenção |

Tons de apoio e estados são decisões de interface. As situações também são descritas por texto. O modo de alto contraste troca os tokens por preto, branco e amarelo. As marcas mantêm suas cores nesse modo; os perfis opcionais de daltonismo reproduzem a transformação de cores observada no site da Fatec em toda a interface.

## Tipografia e espaçamento

- Roboto Regular/Bold para leitura, ações e formulários; Roboto Slab Regular/Bold para títulos, conforme o site de referência.
- Corpo padrão de 16 px; metadados de 13 a 15 px; títulos de 24 a 46 px. Tamanhos em `rem`, compatíveis com as preferências do navegador e com os controles da aplicação.
- Ampliação própria a 125% e 150%, com anúncio de estado; contraste e tamanho persistem em `localStorage`. A− reduz o tamanho até o padrão; o botão de contraste alterna o modo. O seletor de daltonismo oferece Cores Padrão e oito perfis com os filtros SVG da referência.
- Arquivos locais e licenças em `achados/static/fonts/`.
- Escala de espaço: 4, 8, 12, 16, 24, 32 e 48 px; cantos de 5 a 10 px.

## Componentes

| Componente | Comportamento |
| --- | --- |
| Cabeçalho | Faixa do Governo de SP, redes institucionais, A+, A− e contraste; abaixo, marca Fatec + CPS e busca no mural |
| Menu horizontal | Vermelho, texto branco e página ativa com indicação visual e `aria-current` |
| Navegação | Home, Mural, Registrar ocorrência, Como funciona e Relatórios; links disponíveis com quebra de linha quando necessário |
| Trilha de localização | Faixa cinza abaixo do menu, com Home e página atual |
| Notícias recentes | Coluna lateral com cinco notícias e miniaturas locais; fonte e data da consulta indicadas |
| VLibras | Botão visível; o tradutor externo é carregado após ativação explícita |
| Retorno ao topo | Botão no canto inferior direito após rolagem, com retorno do foco ao cabeçalho |
| Rodapé | Contatos e redes em azul-petróleo, créditos acadêmicos, links públicos e marca do Governo de SP |
| Filtro de daltonismo | Seletor fixo no canto inferior esquerdo, perfis originais da referência e preferência persistente |
| Busca | Rótulo associado, campo de pesquisa e botão explícito; filtros enviados por GET |
| Cartão | Prévia 1:1 com foto ilustrativa local da carga fictícia ou ícone “Sem foto”; tipo, protocolo, data, título, descrição, local, situação e ação “Ver detalhes” |
| Campo | Rótulo, obrigatoriedade, erro associado e indicação `aria-invalid` |
| Resumo de erros | Recebe foco após validação e oferece links para os campos, preservando os dados |
| Devolução | Campos habilitados e obrigatórios somente quando a situação selecionada exige |
| Tabela | Cabeçalhos por coluna, legenda e região rolável pelo teclado |
| Exclusão | Confirmação do navegador e proteção CSRF |

## Responsividade e acesso

Conteúdo centralizado com largura máxima de 1200 px e coluna lateral de notícias no desktop. A lateral passa para baixo do conteúdo no celular. Mural de três colunas no desktop, duas em tamanhos intermediários e uma no celular. Formulários em duas colunas passam a uma nos menores tamanhos. Os elementos podem reordenar-se e quebrar linha quando o texto é ampliado.

Foco visível, atalho para o conteúdo, áreas de toque a partir de 44 px, suporte a movimento reduzido e cores forçadas. Ícones decorativos são ocultos de leitores de tela. Ajustes de acessibilidade são guardados somente no navegador.

A rota `/design-system` demonstra os mesmos componentes usados na aplicação. Auditorias automatizadas e testes de interação apoiam a revisão, sem representar certificação de conformidade.

## Fotos dos exemplos

A área da imagem tem proporção 1:1 na Home, no mural e nos detalhes. `object-fit: contain` exibe a foto inteira, sem recortar garrafas ou guarda-chuvas. Os originais mantêm suas proporções e cores. Créditos e licenças em `achados/static/items/README.md`, `photos.json` e na seção “Créditos das fotos” em `/sobre#photo-credits`.

Onze fotos locais representam 33 registros fictícios. As três carteirinhas permanecem sem foto, assim como novos cadastros sem imagem própria. O sistema não apresenta uma foto de referência como se fosse o registro fotográfico de um item real.
