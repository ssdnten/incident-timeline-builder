import unittest
from main import build

def event(time='2026-01-01T00:00:00Z',**kwargs): return dict(timestamp=time,source='auth',event_id='1',message='demo',**kwargs)
class Tests(unittest.TestCase):
    def test_timezone_dedup(self): self.assertEqual(build([event(),event('2026-01-01T05:00:00+05:00')])['duplicates_removed'],1)
    def test_provenance(self): self.assertEqual(build([event(_origin='a:2'),event(_origin='b:2')])['events'][0]['origins'],['a:2','b:2'])
    def test_fractional_order(self): self.assertEqual(build([event('2026-01-01T00:00:00.1Z'),event()])['events'][0]['timestamp'],'2026-01-01T00:00:00Z')
    def test_conflicting_id_preserved(self):
        a=event(); b=dict(a,message='different')
        self.assertEqual(len(build([a,b])['events']),2)
    def test_naive_rejected(self):
        with self.assertRaises(ValueError): build([event('2026-01-01T00:00:00')])
    def test_empty(self): self.assertEqual(build([]),dict(events=[],duplicates_removed=0))
    def test_missing_field(self):
        with self.assertRaises(ValueError): build([{}])
