from datetime import datetime, timezone


def valid_form():
    return {
        "titulo": "Garrafa azul de teste", "descricao": "Garrafa térmica azul com adesivo de estrela.",
        "categoria": "Garrafas e recipientes", "tipo": "encontrado", "status": "aguardando",
        "data_ocorrencia": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "local_nome": "Biblioteca", "bloco": "Principal", "referencia": "Mesa perto da janela",
        "relator_nome": "Pessoa Exemplo", "email": "pessoa@example.com", "vinculo": "Aluno",
        "caracteristicas": "Azul, térmica, adesivo", "quantidade": "1", "cor": "Azul", "marca": "Sem marca",
        "local_guarda": "Ponto de atendimento de teste", "prioridade": "", "contato_autorizado": "on",
        "data_devolucao": "", "retirante_nome": "", "comprovacao": "", "observacoes": "Registro de teste.",
    }


def valid_return():
    return {"retirante_nome": "Proprietário Exemplo", "comprovacao": "Descreveu o adesivo de estrela sem visualizar o item.", "data_devolucao": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
