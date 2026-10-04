import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from atlas import kv
from atlas.live_graph import build_live_view
from atlas.server import Application
from atlas.store import Store
try:
    from tests.test_live_graph import fixture
except ImportError:   # run as `unittest discover -s tests`
    from test_live_graph import fixture

ROOT = Path(__file__).resolve().parents[1]
TEST_TMP = ROOT / 'data' / 'test-tmp'
TEST_TMP.mkdir(parents=True, exist_ok=True)
KV_ENV = {'KV_REST_API_URL': 'https://kv.example.upstash.io', 'KV_REST_API_TOKEN': 'test-token'}


class FakeKV:
    """Stands in for the Upstash REST endpoint: one shared dict, like one Redis database."""
    def __init__(self):
        self.data = {}

    def __call__(self, url, command, headers, allowed):
        assert url == KV_ENV['KV_REST_API_URL'] and allowed == {'kv.example.upstash.io'}
        assert headers['Authorization'] == 'Bearer test-token'
        if command[0] == 'SET':
            self.data[command[1]] = command[2]
            return {'result': 'OK'}
        return {'result': self.data.get(command[1])}


class ServerlessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TEST_TMP)

    def tearDown(self):
        self.tmp.cleanup()

    def app(self, name='a.sqlite'):
        return Application(Path(self.tmp.name) / name)

    def test_analysis_runs_inline_and_returns_the_report(self):
        app = self.app()
        with patch('atlas.server.SERVERLESS', True):
            job = app.start_job({'focus': 'MONDO:0012812', 'role': 'patient'})
        self.assertEqual(job['status'], 'complete')
        self.assertEqual(job['report']['id'], job['report_id'])
        self.assertIn('No outreach has been sent', job['report']['export'])
        app.pool.shutdown(wait=True)

    def test_views_and_reports_are_shared_through_kv(self):
        fake = FakeKV()
        view = build_live_view(fixture(), annotate=False)
        with patch.dict(os.environ, KV_ENV), patch('atlas.kv.secure_request', fake):
            self.assertTrue(kv.enabled())
            Store(Path(self.tmp.name) / 'instance-a.sqlite').save_graph_view(view)
            other = Store(Path(self.tmp.name) / 'instance-b.sqlite')   # a different instance, empty /tmp
            self.assertEqual(other.graph_view(view['id'])['focus'], view['focus'])
        self.assertIn('asterisk:graph:' + view['id'], fake.data)

    def test_kv_failure_falls_back_to_local_storage(self):
        def broken(*args):
            raise OSError('network down')
        view = build_live_view(fixture(), annotate=False)
        with patch.dict(os.environ, KV_ENV), patch('atlas.kv.secure_request', broken):
            store = Store(Path(self.tmp.name) / 'x.sqlite')
            store.save_graph_view(view)
            self.assertEqual(store.graph_view(view['id'])['id'], view['id'])
            self.assertIsNone(Store(Path(self.tmp.name) / 'y.sqlite').graph_view(view['id']))

    def test_missing_view_is_rebuilt_from_its_query(self):
        app = self.app()
        graph_id = '0f0f0f0f-0000-4000-8000-000000000001'
        live = fixture()
        with patch('atlas.server.live_search', return_value=live), patch('atlas.live_graph.pubtator_annotations', return_value=[]):
            graph = app.graph({'graph_id': graph_id, 'live_query': 'Gaucher disease', 'live_focus': 'MONDO:0018150'})
        self.assertEqual(graph['focus'], 'MONDO:0018150')
        self.assertEqual(app.store.graph_view(graph_id)['id'], graph_id)
        for bad in ({'graph_id': graph_id}, {'graph_id': 'not-a-uuid', 'live_query': 'x'}):
            with self.assertRaises(ValueError):
                self.app('b.sqlite').graph(bad)

    def test_entry_point_restores_the_original_path(self):
        with patch.dict(os.environ, {'ATLAS_DATA_DIR': self.tmp.name}):
            sys.path.insert(0, str(ROOT))
            entry = importlib.import_module('api.index')
        self.assertEqual(entry.original_path('/api/index?__path=graph&focus=MONDO%3A0012812'), '/api/graph?focus=MONDO%3A0012812')
        self.assertEqual(entry.original_path('/api/index?__path=reports/abc/proposal'), '/api/reports/abc/proposal')
        self.assertEqual(entry.original_path('/api/health'), '/api/health')
        entry.APP.pool.shutdown(wait=True)
