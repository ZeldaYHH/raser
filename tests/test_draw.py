import unittest

class TestSum(unittest.TestCase):
    def test_draw(self):
        """
        Test draw functions
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
