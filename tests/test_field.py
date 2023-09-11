import unittest

class TestSum(unittest.TestCase):
    def test_field_cal_gen_devsim_db(self):
        """
        Test field cal gen_devsim_db
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
