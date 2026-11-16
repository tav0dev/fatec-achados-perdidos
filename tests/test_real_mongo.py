import json
import os
import unittest
from pathlib import Path
from uuid import uuid4


@unittest.skipUnless(os.environ.get('MONGO_TEST_URI'),'MONGO_TEST_URI não configurado; servidor real opcional.')
class RealMongoTests(unittest.TestCase):
    def test_schema_crud_and_four_pipelines(self):
        from pymongo import MongoClient
        from pymongo.errors import WriteError
        from achados.database import create_indexes
        from achados.queries import report_definitions
        from achados.seed_data import generate_documents
        client=MongoClient(os.environ['MONGO_TEST_URI'],serverSelectionTimeoutMS=4000,tz_aware=True)
        name='fatec_achados_test_'+uuid4().hex
        created=False
        try:
            client.admin.command('ping')
            db=client[name]
            root=Path(__file__).resolve().parents[1]
            schema=json.loads((root/'data/schema.json').read_text(encoding='utf-8'))
            db.create_collection('ocorrencias',validator=schema);created=True
            coll=db.ocorrencias;create_indexes(coll)
            coll.insert_many(generate_documents())
            self.assertEqual(coll.count_documents({}),36)
            for definition in report_definitions():
                self.assertTrue(list(coll.aggregate(definition['pipeline'])))
            with self.assertRaises(WriteError):coll.insert_one({'codigo':'INVALIDO'})
            coll.update_one({'codigo':'AP-0001'},{'$set':{'observacoes':'Atualizado no servidor real'}})
            self.assertEqual(coll.find_one({'codigo':'AP-0001'})['observacoes'],'Atualizado no servidor real')
            coll.delete_one({'codigo':'AP-0001'})
            self.assertEqual(coll.count_documents({}),35)
        finally:
            if created:client.drop_database(name)
            client.close()
