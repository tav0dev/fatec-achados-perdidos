# Achados e Perdidos — Fatec Itapetininga

Aplicação Flask conectada ao MongoDB para cadastrar objetos perdidos e encontrados, pesquisar no mural e acompanhar devoluções.

**Autores:** Gustavo Cuba de Oliveira e Lauren Gabriel de Campos.  
**Disciplina:** Tópicos Especiais — 2º bimestre do 2º semestre de 2026.

## Arquivos da entrega

- [Relatório PDF](docs/relatorio_achados_perdidos_fatec.pdf): autores, ideia, modelagem, consultas, JSON completo e links do GitHub.
- [Coleção em Extended JSON](data/ocorrencias.json): 36 ocorrências fictícias, pronta para importação no Compass.
- [Quatro consultas MongoDB](data/consultas.json) e [validador da coleção](data/schema.json).
- [Roteiro da apresentação](docs/ROTEIRO_APRESENTACAO.md) e [verificação da entrega](docs/VERIFICACAO_ENTREGA.md).

O JSON está incluído no PDF e disponível neste repositório. Não é necessário hospedá-lo no Drive.

## Requisitos da atividade

| Requisito | Implementação |
| --- | --- |
| Flask ou Tkinter conectado ao MongoDB | Flask + PyMongo + MongoDB Server |
| CRUD completo | Cadastro, mural/detalhes, edição e exclusão |
| Pelo menos 10 campos e tipos diferentes | **21 campos próprios**, além do `_id`; string, date, object, array, int, bool e null |
| Pelo menos 30 documentos | **36 documentos** na carga inicial e no JSON |
| Quatro consultas com operadores, agregações e projeções | Pendências antigas, categorias, locais e características |
| PDF com autores, ideia, JSON e GitHub | Relatório em `docs/` |

Banco padrão: **`fatec_achados_perdidos`**. Coleção: **`ocorrencias`**. O servidor valida o esquema e mantém um índice único de protocolo. A carga inicial só é inserida quando a coleção está vazia.

## Executar no Windows

Requer **Python 3.10+** e **MongoDB Community Server**. O MongoDB Compass é opcional para inspecionar os dados e demonstrar as consultas; ele não substitui o servidor.

1. Baixe o projeto em **Code → Download ZIP**, extraia a pasta ou clone este repositório.
2. Inicie o serviço MongoDB Server. No Compass, teste `mongodb://localhost:27017`.
3. Execute **`iniciar.bat`**. Na primeira execução, o atalho instala as bibliotecas e prepara o banco.
4. Abra **http://127.0.0.1:5057**. Para encerrar, pressione Ctrl+C na janela do servidor.

O ambiente Python fica em `%LOCALAPPDATA%\AchadosFatec\venv`.

## Executar no Linux / WSL

Com MongoDB Server acessível em `localhost:27017`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py init
.venv/bin/python app.py
```

Abra **http://127.0.0.1:5057**. No WSL, configure `MONGO_URI` se o MongoDB estiver em outro ambiente.

| Variável de ambiente | Padrão |
| --- | --- |
| `MONGO_URI` | `mongodb://localhost:27017` |
| `MONGO_DB` | `fatec_achados_perdidos` |
| `ACHADOS_PORT` | `5057` |
| `SECRET_KEY` | Chave aleatória a cada início |

O arquivo `.env.example` documenta a configuração. Defina as variáveis no ambiente do processo; arquivos `.env` não são carregados automaticamente.

## Funcionalidades e interface

- Registro de ocorrência de item perdido ou encontrado, com características, contato, data, local e ponto de guarda.
- Busca e filtros por tipo, categoria, situação, local e prioridade; paginação.
- Edição, exclusão com confirmação e devolução com data, retirante e comprovação de propriedade.
- Exibição do e-mail nos detalhes somente quando autorizada no cadastro.
- Relatórios calculados pelo MongoDB e exportação da coleção em Extended JSON.
- Cabeçalho, navegação, marcas e rodapé baseados no site oficial da Fatec; notícias oficiais armazenadas como cópia datada.
- Controles visíveis de fonte, contraste e daltonismo; foco por teclado, retorno ao topo e ativação explícita do VLibras.

As prévias dos itens são quadradas (1:1). As fotos ilustram somente a carga fictícia. Novos registros sem imagem própria aparecem sem foto. [Créditos e licenças das imagens](achados/static/items/README.md), [marcas](achados/static/brand/README.md), [fontes](achados/static/fonts/README.md) e [design system](docs/DESIGN_SYSTEM.md).

Projeto acadêmico para execução local, com dados fictícios e sem autenticação. As marcas institucionais e fotografias mantêm seus respectivos direitos e licenças.

## Importar o JSON no Compass

O comando `python manage.py init` é a forma recomendada de preparar o banco: aplica o validador, cria índices e cadastra os exemplos.

Para usar o arquivo entregue, crie uma coleção **vazia** chamada `ocorrencias` no banco `fatec_achados_perdidos`, escolha **Add Data → Import JSON or CSV file** e selecione `data/ocorrencias.json`. Depois execute `python manage.py init` para aplicar os índices e o validador sem reinserir os dados. Importe uma única vez. Os campos `{"$date":"...Z"}` devem aparecer como `Date`.

## Consultas

| Consulta | Operadores principais |
| --- | --- |
| Pendentes há pelo menos 7 dias | `$and`, `$in`, `$lte`, `$match`, `$project`, `$subtract`, `$divide`, `$floor` |
| Itens por categoria | `$nin`, `$group`, `$sum`, `$cond`, `$eq`, `$project`, `$sort` |
| Ocorrências por local | `$exists`, `$ne`, `$group`, `$sum`, `$min`, `$max`, `$project` |
| Características mais registradas | `$unwind`, `$group`, `$addToSet`, `$size`, `$project` |

Na aplicação, abra **Relatórios**. No Compass, abra **Aggregations** em modo texto e copie o array da consulta desejada de `data/consultas.json`. As consultas usam Extended JSON para as datas; o arquivo exportado fixa a data da geração, enquanto a aplicação usa o dia da execução.

## Testar e gerar novamente a entrega

No Windows, execute `testar.bat`. No Linux, com o ambiente ativado:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Para incluir a verificação com servidor real:

```bash
MONGO_TEST_URI=mongodb://localhost:27017 python -m unittest discover -s tests -v
```

No PowerShell, configure `$env:MONGO_TEST_URI = "mongodb://localhost:27017"` antes de executar a suíte. O teste real cria e remove apenas um banco temporário. Sem essa variável, esse teste é ignorado.

```bash
python manage.py export
python manage.py pdf --github https://github.com/tav0dev/fatec-achados-perdidos
```

`export` gera novamente os exemplos fictícios com datas relativas ao dia atual e os quatro pipelines. `pdf` gera o relatório a partir dos arquivos exportados. Esses comandos não substituem os documentos do banco em uso.
