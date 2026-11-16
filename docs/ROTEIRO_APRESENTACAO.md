# Apresentação — Achados e Perdidos da Fatec Itapetininga

**Dupla:** Gustavo Cuba de Oliveira e Lauren Gabriel de Campos.

1. Explique a ideia: reunir registros de objetos perdidos e encontrados e acompanhar cada devolução.
2. Execute `iniciar.bat` e abra **http://127.0.0.1:5057**. Mostre a Home, a busca e o mural.
3. No Compass, abra **fatec_achados_perdidos.ocorrencias**. Mostre 36 documentos e os tipos: string, objeto `local`, objeto `relator`, array `caracteristicas`, inteiro `quantidade`, booleano `prioridade` e data BSON. São 21 campos próprios, além do `_id`.
4. Demonstre o **Create**: registre uma ocorrência de item encontrado com descrição, local e ponto de guarda. Tente uma data futura, corrija e salve.
5. Demonstre o **Read**: busque pelo protocolo ou por uma característica, use filtros e abra os detalhes.
6. Demonstre o **Update**: edite a descrição ou quantidade e confira a alteração no Compass.
7. Tente devolver sem comprovação. Depois preencha nome, data e comprovação e mostre a situação “Devolvido”.
8. Abra **Relatórios** e explique os quatro pipelines abaixo. Mostre seus operadores e projeções; reproduza uma consulta em **Aggregations** no Compass.
9. Exporte a coleção em Extended JSON e explique que `$date` preserva o tipo de data no MongoDB.
10. Mostre os recursos de acesso: fonte, contraste, daltonismo, navegação por teclado e retorno ao topo. O botão de Libras solicita ativação do serviço externo.
11. Demonstre o **Delete**: exclua somente a ocorrência criada nesta apresentação e confira no Compass. A carga inicial continua com 36 documentos.
12. Abra o PDF entregue, confira os dois autores e mostre os links do repositório, do JSON e o anexo com a coleção completa.

## Como explicar as consultas

- **Pendentes há pelo menos 7 dias:** `$match` com `$and`, `$in` e `$lte` seleciona registros aguardando resolução; `$project` escolhe os campos e calcula os dias com `$subtract`, `$divide` e `$floor`.
- **Categorias:** `$nin` exclui encerrados; `$group`, `$sum`, `$cond` e `$eq` contam registros, unidades, pendências e devoluções; `$project` organiza a saída.
- **Locais:** `$exists` e `$ne` filtram; `$group` usa `local.nome`; `$min` e `$max` encontram as datas extremas; `$project` define o resultado.
- **Características:** `$unwind` abre o array; `$group` conta cada característica; `$addToSet` reúne categorias distintas e `$size` mede essa diversidade; `$project` seleciona a saída.

## Respostas úteis

- **Quem guarda os dados?** MongoDB Server. Flask é a aplicação, PyMongo é o driver e Compass é a interface de inspeção.
- **Por que objetos incorporados?** Local, contato e comprovação pertencem à ocorrência e podem ser consultados no mesmo documento.
- **Como a devolução é validada?** Exige nome, comprovação e data que não seja futura nem anterior à ocorrência.
- **O que significa “Prioritários”?** É uma marcação manual para destacar itens que exigem atenção, não uma classificação automática.
- **O e-mail aparece sempre?** Nos detalhes, apenas se a autorização estiver marcada.
- **Por que as fotos são 1:1?** O quadro uniforme facilita comparar cartões; a imagem inteira é preservada com `object-fit: contain`.
- **As fotos são dos objetos reais?** São referências ilustrativas da carga fictícia, com créditos e licenças. Novos registros sem imagem própria aparecem sem foto.
- **A interface é oficial?** É um projeto acadêmico inspirado no site da Fatec. Marcas originais mantidas; corpo em Roboto e títulos em Roboto Slab.
- **Precisa de Drive?** Não. O PDF contém o JSON completo e links para os arquivos no GitHub.
