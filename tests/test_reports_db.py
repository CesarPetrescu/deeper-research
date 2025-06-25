import unittest
import os
from deep_crawler import reports_db

class TestReportsDB(unittest.TestCase):

    def setUp(self):
        self.db_path = reports_db.DB_PATH
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        reports_db.con = reports_db.get_db_connection()

    def tearDown(self):
        reports_db.con.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_store_and_get_report(self):
        reports_db.store_report('test_id', 'test_question', 'test_content', 'test_stream')
        report = reports_db.get_report('test_id')
        self.assertIsNotNone(report)
        self.assertEqual(report['id'], 'test_id')
        self.assertEqual(report['question'], 'test_question')
        self.assertEqual(report['content'], 'test_content')

    def test_list_reports(self):
        reports_db.store_report('test_id_1', 'q1', 'c1', 's1')
        reports_db.store_report('test_id_2', 'q2', 'c2', 's2')
        reports = reports_db.list_reports()
        self.assertEqual(len(reports), 2)

    def test_delete_report(self):
        reports_db.store_report('test_id', 'q', 'c', 's')
        reports_db.delete_report('test_id')
        report = reports_db.get_report('test_id')
        self.assertIsNone(report)

if __name__ == '__main__':
    unittest.main()
