import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from achados.seed_data import generate_documents
from achados.validation import ValidationError, form_from_document, today_utc, validate_item, validate_return
from tests.factories import valid_form, valid_return


class DomainTests(unittest.TestCase):
    def test_form_creates_typed_objects_dates_array_integer_and_booleans(self):
        doc = validate_item(valid_form())
        self.assertIsInstance(doc["data_ocorrencia"], datetime)
        self.assertIsInstance(doc["quantidade"], int)
        self.assertIsInstance(doc["prioridade"], bool)
        self.assertEqual(doc["local"]["nome"], "Biblioteca")
        self.assertEqual(doc["relator"]["vinculo"], "Aluno")
        self.assertEqual(doc["caracteristicas"], ["azul", "térmica", "adesivo"])
        self.assertIsNone(doc["data_devolucao"])

    def test_found_item_requires_custody_lost_item_does_not(self):
        with self.assertRaises(ValidationError) as caught:
            validate_item({**valid_form(), "local_guarda": ""})
        self.assertIn("local_guarda", caught.exception.errors)
        doc = validate_item({**valid_form(), "tipo": "perdido", "local_guarda": ""})
        self.assertEqual(doc["tipo"], "perdido")

    def test_invalid_dates_quantities_and_email_are_rejected(self):
        for changes, field in [({"data_ocorrencia": "2026-02-30"}, "data_ocorrencia"), ({"data_ocorrencia": (today_utc()+timedelta(days=1)).strftime("%Y-%m-%d")}, "data_ocorrencia"), ({"quantidade": "1.5"}, "quantidade"), ({"quantidade": "0"}, "quantidade"), ({"quantidade": "101"}, "quantidade"), ({"email": "email-invalido"}, "email"), ({"tipo": "outro"}, "tipo"), ({"categoria": "fora-da-lista"}, "categoria")]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError) as caught:
                validate_item({**valid_form(), **changes})
            self.assertIn(field, caught.exception.errors)

    def test_tags_normalize_and_deduplicate_and_limit_lengths(self):
        doc = validate_item({**valid_form(), "caracteristicas": "Azul, azul, , TÉRMICA"})
        self.assertEqual(doc["caracteristicas"], ["azul", "térmica"])
        for text in [",".join(str(i) for i in range(13)), "a"*41]:
            with self.assertRaises(ValidationError):
                validate_item({**valid_form(), "caracteristicas": text})

    def test_return_requires_proof_and_owner_and_correct_chronology(self):
        occurred = today_utc()-timedelta(days=3)
        result = validate_return(valid_return(), occurred)
        self.assertEqual(result["retirante"]["nome"], "Proprietário Exemplo")
        for changes, field in [({"comprovacao": ""}, "comprovacao"), ({"retirante_nome": ""}, "retirante_nome"), ({"data_devolucao": (occurred-timedelta(days=1)).strftime("%Y-%m-%d")}, "data_devolucao"), ({"data_devolucao": (today_utc()+timedelta(days=1)).strftime("%Y-%m-%d")}, "data_devolucao")]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError) as caught:
                validate_return({**valid_return(), **changes},occurred)
            self.assertIn(field,caught.exception.errors)

    def test_closed_record_cannot_keep_hidden_return_data(self):
        with self.assertRaises(ValidationError):
            validate_item({**valid_form(), **valid_return()})
        doc=validate_item({**valid_form(), **valid_return(), "status":"devolvido"})
        self.assertIsInstance(doc["data_devolucao"],datetime)

    def test_edit_round_trip_preserves_fields_and_contact_consent(self):
        doc=validate_item({**valid_form(),"contato_autorizado":""})
        self.assertFalse(doc["contato_autorizado"])
        self.assertEqual(validate_item(form_from_document(doc)),doc)

    def test_dataset_has_36_unique_valid_records_with_21_fields(self):
        docs=generate_documents()
        self.assertEqual(len(docs),36)
        self.assertEqual(len({d["codigo"] for d in docs}),36)
        self.assertEqual(len(docs[0]),21)
        self.assertEqual({d["tipo"] for d in docs},{"perdido","encontrado"})
        self.assertEqual({d["status"] for d in docs},{"aguardando","devolvido","encerrado"})
        for doc in docs:
            self.assertEqual(validate_item(form_from_document(doc)),{k:v for k,v in doc.items() if k not in ("codigo","criado_em","atualizado_em")})

    def test_json_export_preserves_bson_dates_and_matches_schema(self):
        root=Path(__file__).resolve().parents[1]
        docs=json.loads((root/'data/ocorrencias.json').read_text(encoding='utf-8'))
        schema=json.loads((root/'data/schema.json').read_text(encoding='utf-8'))['$jsonSchema']
        self.assertEqual(len(docs),36)
        self.assertEqual(len(schema['required']),21)
        for doc in docs:
            self.assertEqual(set(doc),set(schema['required']))
            self.assertIn('$date',doc['data_ocorrencia'])


if __name__=='__main__':
    unittest.main()
