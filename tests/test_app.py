"""CRUD e resultados das agregações com mongomock, quando instalado."""
import unittest
from datetime import timedelta
from importlib.util import find_spec

from tests.factories import valid_form,valid_return

HAS_DEPENDENCIES=all(find_spec(m) is not None for m in ('flask','pymongo','mongomock'))


@unittest.skipUnless(HAS_DEPENDENCIES,'Instale requirements-dev.txt para executar o MongoDB simulado.')
class ApplicationTests(unittest.TestCase):
    def setUp(self):
        import mongomock
        from achados import create_app
        from achados.seed_data import generate_documents
        self.coll=mongomock.MongoClient(tz_aware=True).fatec_achados_perdidos.ocorrencias
        self.coll.insert_many(generate_documents())
        self.app=create_app({'TESTING':True,'TEST_COLLECTION':self.coll,'SECRET_KEY':'test-only-key'})
        self.client=self.app.test_client()

    def post(self,path,data):
        self.client.get('/sobre')
        with self.client.session_transaction() as session:
            token=session['csrf_token']
        return self.client.post(path,data={**data,'csrf_token':token},follow_redirects=True)

    def test_crud_and_return_persist(self):
        response=self.post('/itens/novo',valid_form())
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.coll.count_documents({}),37)
        doc=self.coll.find_one({'titulo':'Garrafa azul de teste'});code=doc['codigo']
        self.post(f'/itens/{code}/editar',{**valid_form(),'cor':'Azul-marinho'})
        self.assertEqual(self.coll.find_one({'codigo':code})['cor'],'Azul-marinho')
        self.post(f'/itens/{code}/devolver',valid_return())
        self.assertEqual(self.coll.find_one({'codigo':code})['status'],'devolvido')
        self.post(f'/itens/{code}/excluir',{})
        self.assertIsNone(self.coll.find_one({'codigo':code}))

    def test_aggregation_totals_match_records(self):
        from achados.queries import report_definitions
        from achados.validation import today_utc
        docs=list(self.coll.find());today=today_utc()
        reports={r['slug']:list(self.coll.aggregate(r['pipeline'])) for r in report_definitions(today)}
        expected={d['codigo'] for d in docs if d['status']=='aguardando' and d['data_ocorrencia']<=today-timedelta(days=7)}
        self.assertTrue(expected)
        self.assertEqual({d['codigo'] for d in reports['pendentes']},expected)
        for result in reports['pendentes']:
            original=next(d for d in docs if d['codigo']==result['codigo'])
            self.assertEqual(result['dias'],(today-original['data_ocorrencia']).days)
        relevant=[d for d in docs if d['status']!='encerrado']
        self.assertEqual(sum(r['registros'] for r in reports['categorias']),len(relevant))
        self.assertEqual(sum(r['devolvidos'] for r in reports['categorias']),sum(d['status']=='devolvido' for d in relevant))
        self.assertEqual(sum(r['registros'] for r in reports['locais']),len(relevant))
        for row in reports['caracteristicas']:
            matches=[d for d in docs if d['status']=='aguardando' and row['caracteristica'] in d['caracteristicas']]
            self.assertEqual(row['registros'],len(matches))
            self.assertEqual(row['categorias'],len({d['categoria'] for d in matches}))

    def test_rendered_pages_and_empty_search(self):
        for path in ['/','/itens','/consultas','/itens/AP-0002','/itens/AP-0002/editar']:
            self.assertEqual(self.client.get(path).status_code,200)
        self.assertIn('Nenhum item',self.client.get('/itens?q=%5B.*%5D').get_data(as_text=True))
