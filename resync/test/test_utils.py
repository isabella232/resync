import unittest, os.path
import resync.utils

curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestUtill(unittest.TestCase):

    def test1_string(self):
        self.assertEqual('j912liHgA/48DCHpkptJHg==', resync.utils.compute_md5_for_string('A file\n'))

    def test2_file(self):
        # Should be same as the string above
        file = os.path.join(curr_dir, "testdata/a")
        self.assertEqual('j912liHgA/48DCHpkptJHg==', resync.utils.compute_md5_for_file(file))

    def test3_file(self):
        # non-text rs can also be hashed
        file = os.path.join(curr_dir, "testdata/finder.png")
        self.assertEqual('KILnhtMbzHrN3yjI7cRxlg==', resync.utils.compute_md5_for_file(file))

if __name__ == '__main__':
    unittest.main()
