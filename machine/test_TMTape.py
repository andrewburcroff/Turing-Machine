from unittest import TestCase
import machine

class TestTMTape(TestCase):
    def test_write(self):
        T = machine.TMTape("")
        for i in range(10):
            if i > 0:
                T.write("a", i)
        #T.write(T.read(10), 10)
        self.assertEqual(str(T), machine.kBLANK+"aaaaaaaaa"+machine.kBLANK)
        for i in range(10):
            i = -i
            if i < 0:
                T.write("b", i)
        #T.write(T.read(-10), -10)
        self.assertEqual(str(T), machine.kBLANK+"bbbbbbbbb"+machine.kBLANK+"aaaaaaaaa"+machine.kBLANK)

    def test_read(self):
        T = machine.TMTape("")
        self.assertEqual(T.read(13), machine.kBLANK)
        self.assertEqual(T.read(-7), machine.kBLANK)
        T.write("a",  5)
        T.write(T.read(6), 6)
        test = ""
        for i in range(5):
            test = test + machine.kBLANK
        test = test + "a"
        test = test + machine.kBLANK
        self.assertEqual(str(T), test)
