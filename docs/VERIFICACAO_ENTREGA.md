# Verificação da entrega

**Autores:** Gustavo Cuba de Oliveira e Lauren Gabriel de Campos.

Validação realizada em 15/11/2026 com Python 3.14, Flask 3.1 e MongoDB Community Server 8.0.

| Requisito | Evidência |
| --- | --- |
| Flask conectado ao MongoDB | Aplicação em `achados/`, driver PyMongo e inicialização com `manage.py init` |
| CRUD completo | Rotas de cadastro, mural/detalhes, edição e exclusão; testes de rotas e persistência |
| Pelo menos 10 campos com tipos distintos | 21 campos próprios, mais `_id`; string, date, object, array, int, bool e null |
| Pelo menos 30 documentos | 36 registros fictícios no MongoDB e em `data/ocorrencias.json` |
| Quatro consultas com agregações e projeções | Os quatro pipelines executados no servidor real, definidos em `achados/queries.py` e exportados em `data/consultas.json` |
| PDF com autores, ideia, JSON e GitHub | `docs/relatorio_achados_perdidos_fatec.pdf`, com a coleção completa no Anexo B e links clicáveis |

## Resultados da verificação

A suíte executou **21 testes com sucesso**, incluindo o teste opcional com MongoDB real. Esse teste usa banco temporário e verifica inserção, leitura, atualização, exclusão, rejeição de documento inválido pelo validador e execução dos quatro pipelines.

Comando utilizado:

```bash
MONGO_TEST_URI=mongodb://localhost:27017 python -m unittest discover -s tests -v
```

Resultados das consultas na carga de demonstração em 15/11/2026:

| Consulta | Linhas resultantes |
| --- | --- |
| Pendentes há pelo menos 7 dias | 18 |
| Itens por categoria | 7 |
| Ocorrências por local | 6 |
| Características mais registradas | 30 |

Os resultados podem variar quando os dados ou as datas mudarem. A aplicação usa a data atual; os pipelines exportados preservam a data da geração.

O repositório contém os arquivos necessários para executar, testar e apresentar o projeto, com as fontes, imagens e seus créditos. Ambientes Python, dados físicos do MongoDB, arquivos de configuração privados e capturas de trabalho ficam fora da entrega.
