import unittest
import resync.utils

class ThingWithCreated(object):
    def __init__(self): 
        self.created = None

class TestUtil(unittest.TestCase):

    def test01_utc_formatter(self):
        f = resync.utils.UTCFormatter()
        r = ThingWithCreated()
        r.created = 1234567890
        self.assertEqual( f.formatTime(r), "2009-02-13T23:31:30Z" )

    def test02_string(self):
        self.assertEqual( resync.utils.compute_md5_for_string('A file\n'),
                          'j912liHgA/48DCHpkptJHg==')

    def test03_file(self):
        # Should be same as the string above
        self.assertEqual( resync.utils.compute_md5_for_file('resync/test/testdata/a'),
                          'j912liHgA/48DCHpkptJHg==')

if __name__ == '__main__':
    unittest.main()
