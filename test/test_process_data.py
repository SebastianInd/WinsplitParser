import unittest

from src.process_data import process_data


class TestProcessData(unittest.TestCase):

    def setUp(self):
        self.data = {
            "results": [
                {
                    "name": "Sebastian Inderst",
                    "club": "Göteborg-Majorna OK",
                    "total_time": 379,
                    "status": "OK",
                    "position": 1,
                    "splits": [
                        {
                            "split_number": 1,
                            "control_code": "118",
                            "time": 72,
                            "split_time": 72,
                        },
                        {
                            "split_number": 2,
                            "control_code": "40",
                            "time": 202,
                            "split_time": 130,
                        },
                        {
                            "split_number": 3,
                            "control_code": "36",
                            "time": 259,
                            "split_time": 57,
                        },
                        {
                            "split_number": 4,
                            "control_code": "58",
                            "time": 379,
                            "split_time": 120,
                        },
                    ],
                },
                {
                    "name": "Mispunched Runner",
                    "club": "Unknown Club",
                    "total_time": 380,
                    "status": "MissingPunch",
                    "position": None,
                    "splits": [
                        {
                            "split_number": 1,
                            "control_code": "118",
                            "time": 80,
                            "split_time": 80,
                        },
                        {
                            "split_number": 2,
                            "control_code": "40",
                            "time": None,
                            "split_time": None,
                        },
                        {
                            "split_number": 3,
                            "control_code": "36",
                            "time": 280,
                            "split_time": None,
                        },
                        {
                            "split_number": 4,
                            "control_code": "58",
                            "time": 380,
                            "split_time": 100,
                        },
                    ],
                },
            ]
        }

    def test_process_data(self):
        process_data(self.data)

        self.assertEqual(self.data["winning_time"], 379)

        splits_runner_0 = self.data["results"][0]["splits"]
        splits_runner_1 = self.data["results"][1]["splits"]

        self.assertEqual(splits_runner_0[0]["split_gap"], 0)
        self.assertEqual(splits_runner_0[0]["percentage_gap"], 0.0)

        self.assertEqual(splits_runner_1[0]["split_gap"], 8)
        self.assertAlmostEqual(splits_runner_1[0]["percentage_gap"], 11.11, 2)

        self.assertEqual(splits_runner_1[1]["split_gap"], None)
        self.assertEqual(splits_runner_1[1]["percentage_gap"], None)


if __name__ == "__main__":
    unittest.main()
