"""Testes Flask com chamadas ao driver observadas por mocks."""
import json
import unittest
from importlib.util import find_spec
from unittest.mock import MagicMock,patch

from tests.factories import valid_form,valid_return

HAS_DRIVER=all(find_spec(m) is not None for m in ('flask','pymongo'))


@unittest.skipUnless(HAS_DRIVER,'Instale Flask e PyMongo para os testes de rotas.')
class RouteTests(unittest.TestCase):
    def setUp(self):
        from achados import create_app
        from achados.seed_data import generate_documents
        self.docs=generate_documents()
        self.coll=MagicMock()
        self.coll.aggregate.return_value=[]
        self.coll.count_documents.return_value=36
        self.coll.find_one.return_value=self.docs[1]
        self.coll.find.return_value.sort.return_value.limit.return_value=self.docs[:6]
        self.coll.find.return_value.sort.return_value.skip.return_value.limit.return_value=self.docs[:12]
        self.coll.update_one.return_value.matched_count=1
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test-only-key','TEST_COLLECTION':self.coll})
        self.client=self.app.test_client()

    def post(self,path,data=None):
        self.client.get('/sobre')
        with self.client.session_transaction() as session:
            token=session['csrf_token']
        return self.client.post(path,data={**(data or {}),'csrf_token':token})

    def test_all_pages_render_and_legacy_list_redirects(self):
        for path in ['/','/itens','/itens?pagina=2','/itens/novo','/itens/AP-0002','/itens/AP-0002/editar','/sobre','/consultas','/design-system']:
            with self.subTest(path=path):
                response=self.client.get(path)
                self.assertEqual(response.status_code,200)
                self.assertIn('Fatec Itapetininga',response.get_data(as_text=True))
        self.assertEqual(self.client.get('/emprestimos').status_code,301)
        self.assertEqual(self.client.get('/nao-existe').status_code,404)

    def test_create_sends_typed_record_and_invalid_input_does_not_write(self):
        result=self.post('/itens/novo',valid_form())
        self.assertEqual(result.status_code,302)
        doc=self.coll.insert_one.call_args.args[0]
        self.assertTrue(doc['codigo'].startswith('AP-'))
        self.assertEqual(doc['quantidade'],1)
        self.assertEqual(doc['local']['nome'],'Biblioteca')
        self.assertIn(doc['codigo'],result.headers['Location'])
        self.coll.insert_one.reset_mock()
        self.assertEqual(self.post('/itens/novo',{**valid_form(),'email':'invalid'}).status_code,422)
        self.coll.insert_one.assert_not_called()

    def test_update_delete_and_return_use_expected_documents(self):
        self.assertEqual(self.post('/itens/AP-0002/editar',{**valid_form(),'quantidade':'2'}).status_code,302)
        query,change=self.coll.update_one.call_args.args
        self.assertEqual(query,{'codigo':'AP-0002'})
        self.assertEqual(change['$set']['quantidade'],2)
        self.assertNotIn('criado_em',change['$set'])
        self.assertEqual(self.post('/itens/AP-0002/devolver',valid_return()).status_code,302)
        query,change=self.coll.update_one.call_args.args
        self.assertEqual(query,{'codigo':'AP-0002','status':'aguardando'})
        self.assertEqual(change['$set']['status'],'devolvido')
        self.assertEqual(change['$set']['retirante']['nome'],'Proprietário Exemplo')
        self.assertEqual(self.post('/itens/AP-0002/excluir').status_code,302)
        self.coll.delete_one.assert_called_once_with({'codigo':'AP-0002'})

    def test_return_without_proof_is_rejected_and_completed_cannot_return_again(self):
        self.assertEqual(self.post('/itens/AP-0002/devolver',{**valid_return(),'comprovacao':''}).status_code,422)
        self.coll.update_one.assert_not_called()
        self.coll.find_one.return_value['status']='encerrado'
        self.assertEqual(self.post('/itens/AP-0002/devolver',valid_return()).status_code,302)
        self.coll.update_one.assert_not_called()

    def test_search_escapes_regex_and_applies_real_filters(self):
        response=self.client.get('/itens?q=%5B.*%5D&tipo=perdido&categoria=Documentos&local=Biblioteca&status=antigos&prioridade=1&pagina=texto')
        self.assertEqual(response.status_code,200)
        query=self.coll.count_documents.call_args.args[0]
        self.assertEqual(query['tipo'],'perdido')
        self.assertEqual(query['categoria'],'Documentos')
        self.assertEqual(query['local.nome'],'Biblioteca')
        self.assertTrue(query['prioridade'])
        self.assertEqual(query['status'],'aguardando')
        self.assertEqual(query['$or'][0]['codigo']['$regex'],r'\[\.\*\]')

    def test_csrf_error_db_failure_and_missing_item(self):
        from pymongo.errors import ServerSelectionTimeoutError
        self.assertEqual(self.client.post('/itens/novo',data=valid_form()).status_code,400)
        self.client.get('/sobre')
        self.assertEqual(self.client.post('/itens/novo',data={'csrf_token':'inválido'}).status_code,400)
        self.coll.find_one.return_value=None
        self.assertEqual(self.client.get('/itens/AUSENTE').status_code,404)
        with patch.object(self.coll,'aggregate',side_effect=ServerSelectionTimeoutError('offline')):
            response=self.client.get('/')
        self.assertEqual(response.status_code,503)
        self.assertIn('MongoDB',response.get_data(as_text=True))

    def test_text_escaping_and_email_consent(self):
        doc=self.coll.find_one.return_value
        doc['descricao']='<script>alert("x")</script>'
        doc['relator']['email']='privado@example.com'
        doc['contato_autorizado']=False
        body=self.client.get('/itens/AP-0002').get_data(as_text=True)
        self.assertIn('&lt;script&gt;',body)
        self.assertNotIn('<script>alert',body)
        self.assertNotIn('privado@example.com',body)
        doc['contato_autorizado']=True
        self.assertIn('mailto:privado@example.com',self.client.get('/itens/AP-0002').get_data(as_text=True))

    def test_export_and_populated_report_projections(self):
        from datetime import datetime,timezone
        self.coll.find.return_value.sort.return_value.__iter__.return_value=iter(self.docs)
        response=self.client.get('/exportar.json')
        data=json.loads(response.data)
        self.assertEqual(len(data),36)
        self.assertIn('$date',data[0]['data_ocorrencia'])
        self.assertIn('fatec_achados_perdidos.json',response.headers['Content-Disposition'])
        self.coll.aggregate.side_effect=[
            [{'codigo':'AP-0002','titulo':'Garrafa de teste','local':'Biblioteca','dias':8,'prioridade':True}],
            [{'categoria':'Documentos','registros':3,'pendentes':2,'devolvidos':1,'unidades':3}],
            [{'local':'Biblioteca','registros':3,'encontrados':2,'perdidos':1,'primeira':datetime.now(timezone.utc)}],
            [{'caracteristica':'azul','registros':2,'categorias':1}],
        ]
        response=self.client.get('/consultas')
        self.assertEqual(response.status_code,200)
        self.assertIn('Garrafa de teste',response.get_data(as_text=True))
        self.assertIn('azul',response.get_data(as_text=True))
