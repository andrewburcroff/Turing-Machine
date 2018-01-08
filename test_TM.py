from unittest import TestCase
import machine
import os
import json

class TestTM(TestCase):
    def test_load(self):
        M = machine.TM(os.path.join("..",  "configs", "ex_821.tm"))
        with self.assertRaises(machine.InvalidCharacterInTape):
            M.load(machine.TMTape("abc"))
        self.assertIsNone(M.load(machine.TMTape("ab")))

    def test_config(self):
        M = machine.TM()
        with self.assertRaises(FileNotFoundError):
            M.config("junk")
        self.assertIsInstance(M, machine.TM)

    def test_get_c(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.load(machine.TMTape("ab"))
        self.assertEqual(M.get_c(), "q0"+machine.kBLANK+"ab"+machine.kBLANK)

    def test_step(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.load(machine.TMTape("ab"))
        self.assertEqual(M.step(), "⊢"+machine.kBLANK+"q1ab"+machine.kBLANK)

    def test_is_accepted(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.load(machine.TMTape("aa"))
        M.exec()
        self.assertTrue(M.is_accepted())
        M.load(machine.TMTape("ab"))
        M.exec()
        self.assertFalse(M.is_accepted())

    def test_export(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        with self.assertRaises(FileNotFoundError):
            M.export(os.path.join("..", "configs", "baddir", "badfile.tm"))
        self.assertIsNone(M.export(os.path.join("..", "configs", "export_file.tm")))
        with open(os.path.join("..", "configs", "ex_821.tm"), "r", encoding="utf-8") as f:
            a = json.load(f)
            for this_key in a.keys():
                try:
                    a[this_key].sort()
                except:
                    pass
        with open(os.path.join("..", "configs", "export_file.tm"), "r", encoding="utf-8") as f:
            b = json.load(f)
            for this_key in b.keys():
                try:
                    b[this_key].sort()
                except:
                    pass
        self.assertDictEqual(a,b)

    def test_exec(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.load(machine.TMTape("aa"))
        trace = M.exec()
        expected = [
            "q0БaaБ",
            "⊢Бq1aaБ",
            "⊢Бaq2aБ",
            "⊢Бaaq3Б",
            "Accepted: БaaБ"
        ]
        self.assertListEqual(trace, expected)

    def test_reset(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.load(machine.TMTape("aa"))
        M.exec()
        self.assertNotEqual(M.current_position, 0)
        self.assertNotEqual(M.current_state, M.start)
        M.reset()
        self.assertEqual(M.current_position, 0)
        self.assertEqual(M.current_state, M.start)

    def test_dumps(self):
        M = machine.TM(os.path.join("..", "configs", "ex_821.tm"))
        M.export(os.path.join("..", "configs", "export_file.tm"))
        with open(os.path.join("..", "configs", "export_file.tm"), "r", encoding="utf-8") as f:
            a = json.load(f)
        self.assertEqual(M.dumps(), json.dumps(a, sort_keys=True, indent=4, ensure_ascii=False))
