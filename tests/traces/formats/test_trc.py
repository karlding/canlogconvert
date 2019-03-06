import unittest

from canlogconvert.traces.formats.trc import load_string


class TrcTest(unittest.TestCase):
    def test_load_string_supported_version(self):
        # We currently only support File Version 2.1
        input_string = """\
;$FILEVERSION=2.1
;$STARTTIME=43474.7738065227
;$COLUMNS=N,O,T,B,I,d,R,L,D
        """

        load_string(input_string)
        self.assertEqual(True, True)

    def test_load_string_unsupported_version(self):
        # We currently only support File Version 2.1
        input_string = """\
;$FILEVERSION=1.1
;$STARTTIME=43474.7738065227
;$COLUMNS=N,O,T,B,I,d,R,L,D
        """

        self.assertRaises(ValueError, load_string, input_string)


if __name__ == "__main__":
    unittest.main()
