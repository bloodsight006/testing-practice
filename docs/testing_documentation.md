# Hospital Appointment Booking System - Graph Matrix Based Testing

## 1. Control Flow Graph (CFG)
```text
      [S1: Start]
           |
           v
  [S2: Login Validation]
      /            \
(Invalid)        (Valid)
    /                \
[S3: Terminate]  [S4: Check Doc Avail]
    |                /            \
    |      (Unavailable)        (Available)
    |            /                  \
    |     [S5: Exit]         [S6: Check Slot]
    |            |               /            \
    |            |         (Taken)          (Free)
    |            |           /                \
    |            |    [S7: Error]      [S8: Confirm]
    |            |           |                |
    |            |           |         [S9: Notify]
    \            |           |                /
     \           |           |               /
      \          v           v              /
       +-----> [S10: End] <----------------+
```

## 2. Nodes and Edges List
**Nodes (N = 10):**
* 1: Start
* 2: Patient login validation
* 3: Terminate (invalid login)
* 4: Check doctor availability
* 5: Exit (doctor unavailable)
* 6: Check time slot availability
* 7: Show error (slot taken)
* 8: Confirm appointment booking
* 9: Send confirmation notification
* 10: End

**Edges (E = 12):**
* e1: 1 → 2
* e2: 2 → 3
* e3: 2 → 4
* e4: 3 → 10
* e5: 4 → 5
* e6: 4 → 6
* e7: 5 → 10
* e8: 6 → 7
* e9: 6 → 8
* e10: 7 → 10
* e11: 8 → 9
* e12: 9 → 10

## 3. Graph Adjacency Matrix
A 10x10 matrix representing the directed edges between nodes. `1` indicates an edge exists from Node(row) to Node(column), `0` otherwise.

| Node | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|------|---|---|---|---|---|---|---|---|---|----|
| **1**| 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0  |
| **2**| 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0  |
| **3**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1  |
| **4**| 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0  |
| **5**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1  |
| **6**| 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0  |
| **7**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1  |
| **8**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0  |
| **9**| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1  |
| **10**|0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0  |

## 4. Cyclomatic Complexity Calculation
Using the standard formula: **V(G) = E - N + 2P** (where P is the number of connected components, which is 1).
* E (Edges) = 12
* N (Nodes) = 10
* **V(G) = 12 - 10 + 2 = 4**

Alternatively, V(G) = Number of decision nodes + 1. Decision nodes are 2, 4, and 6 (total 3).
* **V(G) = 3 + 1 = 4**

## 5. Independent Paths
Based on a cyclomatic complexity of 4, there are 4 linearly independent paths through the system:
* **Path 1:** 1 → 2 → 3 → 10 (Login fails)
* **Path 2:** 1 → 2 → 4 → 5 → 10 (Login success, Doctor unavailable)
* **Path 3:** 1 → 2 → 4 → 6 → 7 → 10 (Login success, Doctor available, Slot taken)
* **Path 4:** 1 → 2 → 4 → 6 → 8 → 9 → 10 (Login success, Doctor available, Slot free -> BOOKED)

## 6. Minimum Test Cases
We need a minimum of **4 test cases** to ensure 100% Path Coverage (Basis Path Testing).

## 7. Test Case Table
| Test Case ID | Path Covered | Input Data | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC_01 | Path 1 | User="invalid", Pass="wrong" | "Login failed. Terminating." | Pending | Pending |
| TC_02 | Path 2 | User="valid", Pass="ok", Doctor="Dr. Smith" (Unavailable flag) | "Doctor is currently unavailable." | Pending | Pending |
| TC_03 | Path 3 | User="valid", Pass="ok", Doctor="Dr. Smith" (Available), Time="10:00 AM" (Taken) | "Time slot already taken." | Pending | Pending |
| TC_04 | Path 4 | User="valid", Pass="ok", Doctor="Dr. Smith" (Available), Time="11:00 AM" (Free) | "Appointment Confirmed & Notified" | Pending | Pending |

## 8. Path Coverage Explanation
Path coverage is achieved when every linearly independent path through the program has been executed at least once test. Since we determined the cyclomatic complexity is 4, executing the 4 test cases outlined in the table guarantees that every node and every edge (decision branch) in the appointment booking flow is tested at least once, maximizing fault detection inside these logic branches.