"""Relatório acadêmico com modelagem, identidade, consultas e JSON integral."""
import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]


def build_report(github_url=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image
    from achados.identity import BRAND_GUIDE_URL, LOGO_PATH, LOGO_URL, OFFICIAL_LOGOS_URL
    from achados.queries import report_definitions

    metadata_path = ROOT / "docs/entrega.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if github_url:
        if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/?", github_url):
            raise ValueError("Informe a URL completa do repositório GitHub.")
        metadata["github"] = github_url.rstrip("/")
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not (ROOT / "data/ocorrencias.json").exists():
        from manage import export_files
        export_files()
    documents = json.loads((ROOT / "data/ocorrencias.json").read_text(encoding="utf-8"))
    queries = json.loads((ROOT / "data/consultas.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "data/schema.json").read_text(encoding="utf-8"))
    font, bold = "Helvetica", "Helvetica-Bold"
    directory = ROOT / "achados/static/fonts"
    if (directory / "roboto-400.ttf").exists() and (directory / "roboto-700.ttf").exists():
        pdfmetrics.registerFont(TTFont("RobotoReport", str(directory / "roboto-400.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoReportBold", str(directory / "roboto-700.ttf")))
        pdfmetrics.registerFontFamily("RobotoReport", normal="RobotoReport", bold="RobotoReportBold", italic="RobotoReport", boldItalic="RobotoReportBold")
        font, bold = "RobotoReport", "RobotoReportBold"
    brand = colors.HexColor("#b20000")
    ink = colors.HexColor("#26313b")
    muted = colors.HexColor("#666666")
    styles = getSampleStyleSheet()
    for name, size, leading, face in [("Body",9,15,font),("Note",7.5,12,font),("Section",19,27,bold),("Sub",11,18,bold),("Cover",33,43,bold),("Cell",7.5,11,font)]:
        styles.add(ParagraphStyle(name="AP" + name, fontName=face, fontSize=size, leading=leading,
                                 textColor=brand if name in ("Section", "Cover") else ink,
                                 spaceAfter=12, spaceBefore=10 if name == "Sub" else 0))
    styles.add(ParagraphStyle(name="APCode", fontName="Courier", fontSize=6.5, leading=8.6, textColor=ink, spaceAfter=12))
    story = []

    def para(text, kind="Body"):
        story.append(Paragraph(text, styles["AP" + kind]))

    def section(title):
        story.append(PageBreak())
        para(title, "Section")

    def code(value):
        lines = []
        for line in value.splitlines():
            lines.extend(textwrap.wrap(line, width=108, replace_whitespace=False, drop_whitespace=False) or [""])
        story.append(Preformatted("\n".join(lines), styles["APCode"]))

    def table(rows):
        cells = [[Paragraph(escape(str(cell)), styles["APCell"]) for cell in row] for row in rows]
        element = Table(cells, colWidths=[4.0*cm,3.0*cm,10.0*cm], repeatRows=1, hAlign="LEFT")
        element.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#fff0f0")),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,-1),.3,colors.HexColor("#e5e7eb"))]))
        story.append(element)

    if LOGO_PATH.exists():
        from reportlab.lib.utils import ImageReader
        width, height = ImageReader(str(LOGO_PATH)).getSize()
        logo = Image(str(LOGO_PATH), width=7.7*cm, height=7.7*cm*height/width)
        logo.hAlign = "LEFT"
        story.append(logo)
        story.append(Spacer(1, .8*cm))
    else:
        para("Fatec Itapetininga", "Sub")
    story.append(Spacer(1, .6*cm))
    para("Achados<br/>e Perdidos", "Cover")
    para("Um lugar para cada reencontro.", "Sub")
    para("Sistema de gestão de ocorrências da comunidade acadêmica da Fatec Itapetininga.")
    story.append(Spacer(1, .9*cm))
    para("Autores", "Sub")
    for author in metadata["autores"]:
        para(escape(author))
    para(escape(metadata["disciplina"]) + " — " + escape(metadata["periodo"]), "Note")
    para("Repositório GitHub", "Sub")
    if metadata.get("github"):
        url = escape(metadata["github"])
        para(f'<link href="{url}" color="#b20000">{url}</link>')
    else:
        para("Link pendente de publicação.", "Note")
    para(f"Gerado em {datetime.now():%d/%m/%Y}. Projeto acadêmico; dados de demonstração fictícios.", "Note")

    section("Arquivos da entrega")
    para("Este PDF reúne os autores, a ideia do sistema, a modelagem, as quatro consultas, o validador e o JSON completo dos 36 documentos. O código e os arquivos importáveis estão no repositório abaixo.")
    if metadata.get("github"):
        repository = metadata["github"].rstrip("/")
        for label, path in [
            ("Código e instruções", ""),
            ("Coleção: ocorrencias.json", "/blob/main/data/ocorrencias.json"),
            ("Quatro consultas: consultas.json", "/blob/main/data/consultas.json"),
            ("Validador: schema.json", "/blob/main/data/schema.json"),
            ("Roteiro da apresentação", "/blob/main/docs/ROTEIRO_APRESENTACAO.md"),
        ]:
            para(f'<link href="{escape(repository + path)}" color="#b20000">{escape(label)}</link>')
    table([
        ("Requisito", "Entregue", "Onde verificar"),
        ("Flask + MongoDB e CRUD", "Completo", "Cadastro, mural e detalhes, edição e exclusão"),
        ("10 campos e tipos variados", "21 campos", "Seção 2 e validador do Anexo A; mais o _id do MongoDB"),
        ("30 documentos", str(len(documents)), "JSON completo no Anexo B e arquivo importável no GitHub"),
        ("4 consultas avançadas", str(len(queries)), "Seções 4.1 a 4.4: operadores, agregações e projeções"),
    ])
    para("O JSON da coleção usa Extended JSON para preservar datas BSON. O arquivo data/consultas.json contém pipelines de consulta; data/schema.json contém o validador. A aplicação utiliza uma coleção de ocorrências.", "Note")

    section("1. Ideia e finalidade")
    para("O sistema organiza os registros de objetos perdidos e encontrados na Fatec Itapetininga. Centraliza a descrição dos itens, a data e o local da ocorrência, o contato do relator, as características de identificação, o ponto de guarda e o histórico de devolução.")
    para("A finalidade é facilitar o reconhecimento dos objetos e reduzir a perda de informações durante o acompanhamento. Tanto quem encontra um item quanto quem procura algo pode registrar uma ocorrência. O mural permite cruzar informações por palavras, categorias, locais e características.")
    para("Fluxo de uso", "Sub")
    para("1. Registrar se o item foi perdido ou encontrado.<br/>2. Descrever o objeto, suas características, a data e o local.<br/>3. Consultar o mural e os filtros para reconhecer possíveis correspondências.<br/>4. Confirmar a propriedade antes da entrega e registrar nome, data e comprovação.<br/>5. Acompanhar pendências e devoluções nas consultas e relatórios.")
    para("Arquitetura", "Sub")
    para("Navegador com HTML, CSS e JavaScript; Flask recebe e valida as requisições; PyMongo conecta ao MongoDB Community Server. O Compass é utilizado para inspecionar o banco, importar o Extended JSON e reproduzir agregações.")
    para("O banco padrão é fatec_achados_perdidos, com a coleção ocorrencias. A preparação configura índices e validador. Os 36 exemplos são inseridos somente quando a coleção está vazia; registros existentes são preservados.")

    section("2. Modelagem da coleção")
    para("Cada documento representa uma ocorrência. Local, relator e retirante são objetos incorporados; as características de identificação formam um array. São 21 campos próprios, além do _id ObjectId criado pelo MongoDB.")
    fields = [
        ("codigo","string","Protocolo único AP-..."),("titulo","string","Nome do item"),("descricao","string","Descrição detalhada do objeto"),
        ("categoria","string","Uma das sete categorias"),("tipo","string","perdido ou encontrado"),("status","string","aguardando, devolvido ou encerrado"),
        ("data_ocorrencia","date BSON","Data em que o item foi perdido ou encontrado"),("local","object","nome, bloco e referencia"),
        ("relator","object","nome, email e vinculo"),("caracteristicas","array","Cor, material e detalhes reconhecíveis"),("quantidade","int","Número de unidades, de 1 a 100"),
        ("cor","string","Cor predominante"),("marca","string","Marca, se conhecida"),("local_guarda","string","Onde o item encontrado está guardado"),
        ("prioridade","bool","Marcação manual de itens que exigem atenção"),("contato_autorizado","bool","Permite exibir o e-mail nos detalhes"),
        ("data_devolucao","date / null","Data efetiva da devolução"),("retirante","object","nome e comprovacao da propriedade"),
        ("observacoes","string","Informações adicionais"),("criado_em","date BSON","Criação do registro"),("atualizado_em","date BSON","Última alteração"),
    ]
    table([("Campo","Tipo BSON","Finalidade")] + fields)
    story.append(Spacer(1,12))
    para("O arquivo data/schema.json define o validador $jsonSchema. Há índices para o protocolo único, situação/data, categoria e tipo/local. Datas no arquivo JSON usam {\"$date\": \"...Z\"} e são datas BSON no banco, não strings.", "Note")

    section("3. Identidade visual e design system")
    para("A identidade foi pesquisada nos canais oficiais do Centro Paula Souza e da Fatec Itapetininga. O manual apresenta o vermelho RGB 178/0/0 (#B20000), branco, preto, cinza RGB 102/102/102 (#666666) e a família Verdana.")
    para("A interface segue a referência web da Fatec: Roboto no corpo, Roboto Slab nos títulos, cabeçalho com Governo de SP, marca Fatec/CPS, menu vermelho, busca, trilha cinza, notícias recentes e rodapé institucional. As fontes e imagens são locais, com referências e licenças incluídas. O logotipo original mantém suas proporções e cores.")
    para("O design system está documentado em docs/DESIGN_SYSTEM.md e na página /design-system. Inclui tokens de cor, escala de espaçamento, tipografia, botões, rótulos de situação, campos, avisos, cartões de itens e comportamento responsivo.")
    para("A navegação oferece foco visível, rótulos e erros associados aos campos, texto além de cores nos estados, controles de fonte e contraste, perfis de daltonismo e retorno ao topo. O botão de Libras carrega o serviço externo VLibras após ativação explícita. Esses recursos apoiam a acessibilidade, sem representar certificação de conformidade.")
    para("Os cartões têm prévias quadradas (1:1). Onze fotos do Wikimedia Commons ilustram 33 ocorrências fictícias, com autoria e licenças na aplicação e no repositório. As três carteirinhas e novos cadastros sem imagem própria aparecem sem foto. As notícias recentes são uma cópia datada de cinco publicações oficiais, não um feed em tempo real.")
    for label, url in [("Manual oficial CPS",BRAND_GUIDE_URL),("Logotipos oficiais",OFFICIAL_LOGOS_URL),("PNG da unidade",LOGO_URL)]:
        para(f'<b>{label}:</b> <link href="{escape(url)}" color="#b20000">{escape(url)}</link>', "Note")

    for i, report in enumerate(report_definitions(),1):
        section(f"4.{i} {report['title']}")
        para(escape(report["description"]))
        para("Operadores: " + escape(report["operators"]), "Note")
        code(json.dumps(queries[report["slug"]],ensure_ascii=False,indent=2))
        para("A aplicação usa a data atual em cada execução. O arquivo exportado mantém a data de sua geração. Os resultados são calculados pelo MongoDB.", "Note")

    section("5. Execução e apresentação")
    para("No Windows", "Sub")
    para("Inicie o serviço MongoDB e conecte o Compass em mongodb://localhost:27017. Execute iniciar.bat e abra http://127.0.0.1:5057. Na primeira preparação, o atalho instala as bibliotecas, configura a coleção, insere 36 registros fictícios e executa as quatro consultas.")
    para("No Linux / WSL", "Sub")
    code("python3 -m venv .venv\n.venv/bin/python -m pip install -r requirements.txt\n.venv/bin/python manage.py init\n.venv/bin/python app.py")
    para("Requer Python 3.10 ou superior e MongoDB Server acessível em localhost:27017. O Compass é a interface de inspeção e não substitui o servidor. A variável MONGO_URI permite configurar outra conexão.", "Note")
    para("Roteiro da demonstração", "Sub")
    para("Mostre a Home, a busca e o mural. Registre uma ocorrência de item encontrado, preencha suas características e o ponto de guarda. Faça uma busca pelo protocolo ou por uma característica. Edite o registro e confira a alteração no Compass. Tente uma devolução sem comprovação, depois preencha corretamente e confirme a mudança de situação. Exiba as quatro consultas e a exportação JSON. Exclua apenas o registro criado durante a apresentação.")
    para("Validações e testes", "Sub")
    para("Os formulários validam dados obrigatórios, e-mail, quantidades, limites de texto, datas e a comprovação da devolução. Itens encontrados precisam de local de guarda. Datas futuras ou devoluções anteriores à ocorrência são recusadas. Os formulários de alteração usam token de sessão e o HTML escapa textos cadastrados.")
    para("Execute testar.bat para a suíte de testes. O teste opcional com MONGO_TEST_URI cria e remove somente um banco de teste temporário. A aplicação é um projeto acadêmico para execução local e não possui autenticação de usuários.", "Note")

    section("Anexo A. Validador da coleção")
    code(json.dumps(schema,ensure_ascii=False,indent=2))
    section("Anexo B. JSON completo das ocorrências")
    para(f"Os {len(documents)} documentos abaixo são fictícios. Locais de guarda e pessoas não representam atendimentos reais. O mesmo conteúdo está em data/ocorrencias.json.", "Note")
    code("[")
    for index, doc in enumerate(documents):
        lines=["  {"]
        for n,(key,value) in enumerate(doc.items()):
            lines.append("    "+json.dumps(key,ensure_ascii=False)+": "+json.dumps(value,ensure_ascii=False)+("," if n<len(doc)-1 else ""))
        lines.append("  }"+("," if index<len(documents)-1 else ""))
        code("\n".join(lines))
    code("]")

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
        canvas.line(1.8*cm,1.5*cm,A4[0]-1.8*cm,1.5*cm)
        canvas.setFont(font,6.5)
        canvas.setFillColor(muted)
        canvas.drawString(1.8*cm,1.1*cm,"Achados e Perdidos | Fatec Itapetininga | Gustavo Cuba de Oliveira e Lauren Gabriel de Campos")
        canvas.drawRightString(A4[0]-1.8*cm,1.1*cm,str(document.page))
        canvas.restoreState()

    target=ROOT/"docs/relatorio_achados_perdidos_fatec.pdf"
    document=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=1.8*cm,leftMargin=1.8*cm,topMargin=1.8*cm,bottomMargin=2*cm,title=metadata["titulo"],author="; ".join(metadata["autores"]))
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    print(f"PDF gerado: {target}")
    return target


if __name__ == "__main__":
    build_report()
