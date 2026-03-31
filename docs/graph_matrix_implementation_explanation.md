# How Graph Matrix Testing is Implemented in Python

If your professor asks: **"How exactly did you implement Graph Based Matrix Testing in your Python code?"**, you can confidently explain your approach using these three steps:

### 1. I explicitly mapped the program flow into a directed graph
"First, I analyzed my core booking logic (`/api/book_test` route) and mapped every major decision point into nodes and edges. I treated my Python backend strictly as a Control Flow Graph (CFG)."
*   **Node 1:** Function Start
*   **Node 2:** Patient validation fails
*   **Node 3:** Patient is valid, check Doctor schedule
*   ...and so on up to Node 10 (End).

### 2. I injected a dynamic "Path Tracker" directly into the source code
"In my Flask route `api_book_test()`, I initialized an array called `path = [1]` at the very start of the function. As the Python code executes and passes through different IF-statements (like checking if the doctor was available or if the payment was valid), the code dynamically appends the node ID to that `path` array (e.g., `path.append(3)`). When the HTTP response is returned to the client, it returns that exact path array showing the step-by-step trace of how the logic flowed."

### 3. I used Python's `unittest` to assert the edges in the Matrix
"In my testing file (`test_graph_matrix.py`), I didn't just guess test scenarios. 
1.  **Complexity Calculation:** I created an array of my nodes and edges and programmed Python to calculate Cyclomatic Complexity dynamically (`E - N + 2`), which outputted **4**. This mathematically proved I needed exactly 4 independent path test cases.
2.  **Mapping Tests to Paths:** I wrote exactly 4 unit test methods. Each test sends a specific HTTP payload specifically designed to force the backend to travel down one of those 4 calculated paths.
3.  **Assertion (The core proof):** I used `self.assertEqual()` to compare the dynamically generated `path` array returned from the backend against my hardcoded expected Matrix Path (for example: `[1, 3, 5, 7, 8, 9, 10]`). If my code took a wrong turn at an edge, the array wouldn't match, and the test would fail."

**Summary Sentence:**
*"I implemented it by converting my API's control flow into a mathematical graph, injecting a node-tracker into the backend execution, and then using the `unittest` library to assert that the runtime execution path perfectly matched my calculated Basis Paths."*