import unittest
from app import app, init_db
import json

class GraphMatrixTesting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize DB with fresh data for tests
        init_db()
        
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # S1: Start
        # S2: Val Patient
        # S3: Doc Check
        # S4: Doc Unavail (End)
        # S5: Form/Pay Check
        # S6: Form/Pay Fail (End)
        # S7: Form/Pay Succes
        # S8: Save Match
        # S9: Confirm Notify
        # S10: End End 
        
        # Define the Graph Matrix Logic Mapping
        self.nodes = list(range(1, 11))
        # Edge Definitions from the route `/api/book_test` mapped manually:
        self.edges = [
            (1, 2),  # Not logged in
            (1, 3),  # Logged in Start 
            (2, 10), # End from S2
            (3, 4),  # Doc unavailable
            (3, 5),  # Doc Available
            (4, 10), # End from doc unavailable
            (5, 6),  # Pay/Form invalid
            (5, 7),  # Pay/Form valid
            (6, 10), # End form invalid
            (7, 8),  # Trigger Save
            (8, 9),  # Notification
            (9, 10)  # End Success
        ]

    def test_calculate_metrics(self):
        E = len(self.edges)
        N = len(self.nodes)
        v_g = E - N + 2
        print(f"\n[Graph Analysis - Updated Booking Flow]")
        print(f"Edges / Paths Logic: {E}, Nodes: {N}")
        print(f"Cyclomatic Complexity V(G) = {v_g} (Calculated 4 Paths)")
        self.assertEqual(v_g, 4, "Should resolve 4 independent paths")

    def test_path_1_not_logged_in(self):
        """Path 1: 1 -> 2 -> 10 (Not logged in)"""
        print("Testing Path 1...")
        res = self.app.post('/api/book_test', json={
            "patient_id": None
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["path"], [1, 2, 10])

    def test_path_2_doc_unavailable(self):
        """Path 2: 1 -> 3 -> 4 -> 10 (Doctor Unavailable slot)"""
        print("Testing Path 2...")
        # Pre-seed: let's immediately try to double book a slot
        # Book it once first to make it unavailable:
        self.app.post('/api/book_test', json={"patient_id": 4, "doctor_id": 2, "date": "2026-05-01", "time": "10:00", "history": "Flu", "fee": 50})
        
        # Try same slot
        res = self.app.post('/api/book_test', json={
            "patient_id": 4, "doctor_id": 2, "date": "2026-05-01", "time": "10:00"
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["path"], [1, 3, 4, 10])

    def test_path_3_invalid_form_or_payment(self):
        """Path 3: 1 -> 3 -> 5 -> 6 -> 10 (Invalid form or Fee < 50)"""
        print("Testing Path 3...")
        res = self.app.post('/api/book_test', json={
            "patient_id": 4, "doctor_id": 2, "date": "2026-05-01", "time": "11:00",
            "history": "", # Invalid form
            "fee": 40      # Invalid fee
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["path"], [1, 3, 5, 6, 10])

    def test_path_4_successful_booking(self):
        """Path 4: 1 -> 3 -> 5 -> 7 -> 8 -> 9 -> 10 (Valid booking & payment)"""
        print("Testing Path 4...")
        res = self.app.post('/api/book_test', json={
            "patient_id": 4, "doctor_id": 2, "date": "2026-05-01", "time": "14:00",
            "history": "Headaches for a week",
            "fee": 100
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["path"], [1, 3, 5, 7, 8, 9, 10])

if __name__ == '__main__':
    unittest.main()
