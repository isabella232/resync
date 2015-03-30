import unittest
import re
import logging
import sys, StringIO, contextlib

from resync.client import Client, ClientFatalError
from resync.mapper import MapperError

# From http://stackoverflow.com/questions/2654834/capturing-stdout-within-the-same-process-in-python
class Data(object):
    pass

@contextlib.contextmanager
def capture_stdout():
    old = sys.stdout
    capturer = StringIO.StringIO()
    sys.stdout = capturer
    data = Data()
    yield data
    sys.stdout = old
    data.result = capturer.getvalue()


class TestClient(unittest.TestCase):

    _logstream = None

    @classmethod
    def setUpClass(cls):
        # set up logging to class variable logstream
        cls._logstream = StringIO.StringIO()
        logging.basicConfig(level=logging.DEBUG, stream=cls._logstream)

    def setUp(self):
        # clear logstream so we can readily check for new output in any test
        if (self._logstream is None):
            self.setUpClass() #not run automatically in 2.6
        self._logstream.truncate(0)

    def test01_make_resource_list_empty(self):
        c = Client()
        # No mapping is an error
        self.assertRaises( ClientFatalError, c.build_resource_list )

    def test02_source_uri(self):
        c = Client()
        # uris
        self.assertEqual( c.sitemap_uri('http://example.org/path'), 'http://example.org/path')
        self.assertEqual( c.sitemap_uri('info:whatever'), 'info:whatever')
        self.assertEqual( c.sitemap_uri('http://example.org'), 'http://example.org')
        # absolute local
        self.assertEqual( c.sitemap_uri('/'), '/')
        self.assertEqual( c.sitemap_uri('/path/anything'), '/path/anything')
        self.assertEqual( c.sitemap_uri('/path'), '/path')
        # relative, must have mapper
        self.assertRaises( MapperError, c.sitemap_uri, 'a' )
        c.set_mappings( ['http://ex.a/','/a'])
        self.assertEqual( c.sitemap_uri('a'), 'http://ex.a/a')

    def test03_build_resource_list(self):
        c = Client()
        c.set_mappings( ['http://ex.a/','resync/test/testdata/dir1'])
        rl = c.build_resource_list(paths='resync/test/testdata/dir1')
        self.assertEqual( len(rl), 2 )
        # check max_sitemap_entries set in resulting resourcelist
        c.max_sitemap_entries=9
        rl = c.build_resource_list(paths='resync/test/testdata/dir1')
        self.assertEqual( len(rl), 2 )
        self.assertEqual( rl.max_sitemap_entries, 9 )

    def test04_log_event(self):
        c = Client()
        c.log_event("xyz")
        self.assertEqual( self._logstream.getvalue(), "DEBUG:resync.client:Event: 'xyz'\n" )

    def test05_baseline_or_audit(self):
        # Not setup...
        c = Client()
        self.assertRaises( ClientFatalError, c.baseline_or_audit )
        c.set_mappings( ['http://example.org/bbb','/tmp/this_does_not_exist'] )
        self.assertRaises( ClientFatalError, c.baseline_or_audit )
        c.set_mappings( ['/tmp','/tmp']) #unsafe
        self.assertRaises( ClientFatalError, c.baseline_or_audit )
        # empty list to get no resources error
        c = Client()
        c.set_mappings( ['resync/test/testdata/empty_lists','resync/test/testdata/empty_lists'])
        self.assertRaises( ClientFatalError, c.baseline_or_audit, audit_only=True )
        # checksum will be set False if source list has no md5 sums
        c = Client()
        c.set_mappings( ['resync/test/testdata/dir1_src_in_sync','resync/test/testdata/dir1'])
        c.checksum=True
        c.baseline_or_audit(audit_only=True)
        self.assertFalse( c.checksum )
        # include resource in other domain (exception unless noauth set)
        c = Client()
        c.set_mappings( ['resync/test/testdata/dir1_src_with_ext','resync/test/testdata/dir1'])
        self.assertRaises( ClientFatalError, c.baseline_or_audit, audit_only=False )

    def test06_write_capability_list(self):
        c = Client()
        with capture_stdout() as capturer:
            c.write_capability_list( { 'a':'uri_a', 'b':'uri_b' } )
        self.assertTrue( re.search(r'<urlset ',capturer.result) )
        self.assertTrue( re.search(r'<rs:md capability="capabilitylist" />',capturer.result) )
        self.assertTrue( re.search(r'<url><loc>uri_a</loc><rs:md capability="a"',capturer.result) )
        self.assertTrue( re.search(r'<url><loc>uri_b</loc><rs:md capability="b"',capturer.result) )

    def test07_write_source_description(self):
        c = Client()
        with capture_stdout() as capturer:
            c.write_source_description( [ 'a','b','c' ] )
        #print capturer.result
        self.assertTrue( re.search(r'<urlset ',capturer.result) )
        self.assertTrue( re.search(r'<rs:md capability="description" />',capturer.result) )
        self.assertTrue( re.search(r'<url><loc>a</loc><rs:md capability="capabilitylist" /></url>',capturer.result) )
        self.assertTrue( re.search(r'<url><loc>b</loc><rs:md capability="capabilitylist" /></url>',capturer.result) )

    def test20_parse_document(self):
        # Key property of the parse_document() method is that it parses the
        # document and identifies its type
        c = Client()
        with capture_stdout() as capturer:
            c.sitemap_name='resync/test/testdata/examples_from_spec/resourcesync_ex_1.xml'
            c.parse_document()
        self.assertTrue( re.search(r'Parsed resourcelist document with 2 entries',capturer.result) )
        with capture_stdout() as capturer:
            c.sitemap_name='resync/test/testdata/examples_from_spec/resourcesync_ex_17.xml'
            c.parse_document()
        self.assertTrue( re.search(r'Parsed resourcedump document with 3 entries',capturer.result) )
        with capture_stdout() as capturer:
            c.sitemap_name='resync/test/testdata/examples_from_spec/resourcesync_ex_19.xml'
            c.parse_document()
        self.assertTrue( re.search(r'Parsed changelist document with 4 entries',capturer.result) )
        with capture_stdout() as capturer:
            c.sitemap_name='resync/test/testdata/examples_from_spec/resourcesync_ex_22.xml'
            c.parse_document()
        self.assertTrue( re.search(r'Parsed changedump document with 3 entries',capturer.result) )

    def test40_write_resource_list_mappings(self):
        c = Client()
        c.set_mappings( ['http://example.org/','resync/test/testdata/'] )
        # with no explicit paths seting the mapping will be used
        with capture_stdout() as capturer:
            c.write_resource_list()
        #sys.stderr.write(capturer.result)
        self.assertTrue( re.search(r'<rs:md at="\S+" capability="resourcelist"', capturer.result ) )
        self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_a</loc>', capturer.result ) )
        self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_b</loc>', capturer.result ) )
        self.assertTrue( re.search(r'<url><loc>http://example.org/dir2/file_x</loc>', capturer.result ) )

    def test41_write_resource_list_path(self):
        c = Client()
        c.set_mappings( ['http://example.org/','resync/test/testdata/'] )
        # with an explicit paths setting only the specified paths will be included
        with capture_stdout() as capturer:
            c.write_resource_list(paths='resync/test/testdata/dir1')
        sys.stderr.write(capturer.result)
        self.assertTrue( re.search(r'<rs:md at="\S+" capability="resourcelist"', capturer.result ) )
        self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_a</loc>', capturer.result ) )
        self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_b</loc>', capturer.result ) )
        self.assertFalse( re.search(r'<url><loc>http://example.org/dir2/file_x</loc>', capturer.result ) )
        # Travis CI does not preserve timestamps from github so test here for the file
        # size but not the datestamp
        #self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_a</loc><lastmod>[\w\-:]+</lastmod><rs:md length="20" /></url>', capturer.result ) )
        #self.assertTrue( re.search(r'<url><loc>http://example.org/dir1/file_b</loc><lastmod>[\w\-:]+</lastmod><rs:md length="45" /></url>', capturer.result ) )

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClient)
    unittest.TextTestRunner(verbosity=2).run(suite)
