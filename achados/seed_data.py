"""36 ocorrências fictícias para demonstração acadêmica."""
from datetime import datetime, timedelta, timezone

ITEMS = [
    ("Garrafa térmica azul", "Garrafas e recipientes", "Azul", "Sem marca", ["azul", "térmica", "adesivo"], "Garrafa térmica com tampa de rosquear e um adesivo de estrela na lateral."),
    ("Fone de ouvido sem fio", "Eletrônicos", "Branco", "Sem marca", ["branco", "sem fio", "estojo"], "Par de fones dentro de um estojo branco com pequeno risco na tampa."),
    ("Chaveiro com três chaves", "Chaves", "Prata", "Sem marca", ["prata", "chaveiro", "três chaves"], "Chaveiro com três chaves e uma pequena etiqueta de tecido vermelho."),
    ("Caderno de capa preta", "Materiais de estudo", "Preto", "Tilibra", ["preto", "espiral", "anotações"], "Caderno universitário com anotações de programação e capa preta sem nome."),
    ("Carteirinha de estudante", "Documentos", "Branco", "Fatec", ["carteirinha", "estudante", "identificação"], "Carteirinha de estudante sem outros documentos. Dados pessoais omitidos."),
    ("Jaqueta jeans", "Roupas e acessórios", "Azul", "Sem marca", ["azul", "jeans", "tamanho m"], "Jaqueta jeans de tamanho médio com um pequeno bordado na manga esquerda."),
    ("Estojo vermelho", "Materiais de estudo", "Vermelho", "Sem marca", ["vermelho", "zíper", "canetas"], "Estojo vermelho com duas canetas azuis, uma lapiseira e uma borracha."),
    ("Carregador USB-C", "Eletrônicos", "Preto", "Samsung", ["preto", "usb-c", "cabo"], "Carregador com cabo USB-C e fita de identificação na extremidade."),
    ("Óculos de grau", "Roupas e acessórios", "Marrom", "Sem marca", ["marrom", "óculos", "armação"], "Óculos de grau com armação marrom retangular e estojo de tecido."),
    ("Guarda-chuva compacto", "Outros", "Preto", "Sem marca", ["preto", "dobrável", "alça"], "Guarda-chuva preto dobrável com alça de mão e capa protetora."),
    ("Pote de alimentação", "Garrafas e recipientes", "Verde", "Sem marca", ["verde", "tampa", "recipiente"], "Pote para alimentos com tampa verde e uma pequena bolsa térmica cinza."),
    ("Pen drive de 32 GB", "Eletrônicos", "Prata", "Kingston", ["prata", "usb", "32 gb"], "Pen drive metálico com argola e capacidade de 32 GB indicada no corpo."),
]
LOCATIONS = ("Biblioteca", "Laboratórios", "Salas de aula", "Cantina", "Pátio", "Estacionamento")
NAMES = ("Ana Martins", "Bruno Almeida", "Carla Santos", "Diego Ferreira", "Elisa Costa", "Felipe Lima", "Giovana Ribeiro", "Henrique Souza", "Isabela Rocha", "João Mendes", "Letícia Alves", "Miguel Barbosa")


def generate_documents(now=None):
    today = (now or datetime.now(timezone.utc)).replace(hour=0, minute=0, second=0, microsecond=0)
    docs = []
    for i in range(36):
        title, category, color, brand, tags, description = ITEMS[i % len(ITEMS)]
        occurred = today - timedelta(days=(i * 3) % 25)
        kind = "perdido" if i % 4 == 0 else "encontrado"
        status = "encerrado" if i in (11, 23, 35) else ("devolvido" if i % 5 == 0 else "aguardando")
        returned = min(today, occurred + timedelta(days=2)) if status == "devolvido" else None
        docs.append({
            "codigo": f"AP-{i+1:04d}", "titulo": title, "descricao": description,
            "categoria": category, "tipo": kind, "status": status, "data_ocorrencia": occurred,
            "local": {"nome": LOCATIONS[(i // 2) % 6], "bloco": "Principal" if i % 2 else "Anexo", "referencia": "Local fictício utilizado na demonstração acadêmica."},
            "relator": {"nome": NAMES[i % 12], "email": f"pessoa{i+1:02d}@example.com", "vinculo": "Docente" if i % 7 == 0 else "Aluno"},
            "caracteristicas": tags.copy(), "quantidade": 2 if i % 13 == 0 else 1,
            "cor": color, "marca": brand, "local_guarda": "Ponto de atendimento — exemplo" if kind == "encontrado" else "",
            "prioridade": category == "Documentos", "contato_autorizado": i % 3 != 0,
            "data_devolucao": returned,
            "retirante": {"nome": NAMES[(i+3) % 12] if returned else "", "comprovacao": "Proprietário descreveu detalhes do item antes da entrega." if returned else ""},
            "observacoes": "Registro fictício. Não representa uma ocorrência real da Fatec.",
            "criado_em": occurred, "atualizado_em": returned or occurred,
        })
    return docs
