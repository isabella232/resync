import unittest
import os
import tempfile
from resync.client_state import ClientState

class TestClientState(unittest.TestCase):

    def test01_init(self):
        cs = ClientState()
        self.assertTrue( isinstance(cs.status_file, basestring), "status file name is string" )

    def test02_get_and_set(self):
        (fd,filename) = tempfile.mkstemp()
        os.close(fd)
        cs = ClientState()
        cs.status_file = filename
        site = 'http://example.com/'
        self.assertEqual( cs.get_state(site), None )
        cs.set_state(site,123456)
        self.assertEqual( cs.get_state(site), 123456 )
        cs.set_state(site)
        self.assertEqual( cs.get_state(site), None )

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestClientState)
    unittest.TextTestRunner(verbosity=2).run(suite)
