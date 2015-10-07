import re
import sys
import io
import os
import unittest
import contextlib

from resync_publisher.ehri_client import ResourceSyncPublisherClient


class Data(object):
    pass


@contextlib.contextmanager
def capture_stdout():
    old = sys.stdout
    capturer = io.StringIO()
    sys.stdout = capturer
    data = Data()
    yield data
    sys.stdout = old
    data.result = capturer.getvalue()


class TestClient(unittest.TestCase):
    '''
    classdocs
    '''
    def getUri(self, filename):
        return 'file://' + os.path.abspath('resync/test/testdata/examples_from_spec/' + filename)

    def test50_update_resource_list(self):
        c = ResourceSyncPublisherClient()
        c.set_mappings(['http://example.org/', 'resync/test/testdata/'])
        with capture_stdout() as capturer:
            c.calculate_changelist(
                paths='resync/test/testdata/dir1',
                resource_sitemap=self.getUri('resourcesync_ex_34.xml'),
                changelist_sitemap=self.getUri('resourcesync_cl_01.xml'))
        # sys.stderr.write('----------\n')
        # sys.stderr.write(capturer.result)
        self.assertTrue(
            re.search(r'<rs:md capability="changelist"', capturer.result))
        self.assertTrue(
            re.search(r'<url><loc>http://example.org/dir1/file_a</loc>',
                      capturer.result))
        self.assertTrue(
            re.search(r'<url><loc>http://example.org/dir1/file_b</loc>',
                      capturer.result))
        self.assertTrue(
            re.search(r'<url><loc>http://example.com/res1.html</loc>',
                      capturer.result))
        self.assertTrue(
            re.search(r'<url><loc>http://example.com/res2.pdf</loc>',
                      capturer.result))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    unittest.TextTestRunner(verbosity=2).run(suite)
