# Running the Project

## Project Structure

```text
customer-support-agent/
│
├── README.md
├── business_requirement.md
└── customer-support-agent/
    ├── agent.py
    ├── vector_db.py
    ├── requirements.txt
    ├── knowledge base/
    ├── vector_database/
    ├── .env
    └── ...
```

The actual implementation of the AI Customer Support Automation System is located inside the **`customer-support-agent/`** directory.

---

# Prerequisites

* Python 3.13
* Git
* Groq API Key

---

# Step 1: Clone the Repository

```bash
git clone <repository-url>
```

Navigate to the repository.

```bash
cd customer-support-agent
```

---

# Step 2: Navigate to the Project Directory

The implementation is present inside the inner project folder.

```bash
cd customer-support-agent
```

You should now be inside the project directory containing:

```text
agent.py
vector_db.py
requirements.txt
knowledge base/
```

---

# Step 3: Create a Virtual Environment

```bash
python3.13 -m venv .venv
```

Activate the virtual environment.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

# Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Step 5: Configure Environment Variables

Create a `.env` file inside the project directory.

```text
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Replace `YOUR_GROQ_API_KEY` with your actual Groq API key.

---

# Step 6: Build the Vector Database

Before running the application, generate the FAISS vector database.

```bash
python vector_db.py
```

This creates the `vector_database/` directory containing:

```text
index.faiss
index.pkl
```

---

# Step 7: Run the Customer Support Agent

```bash
python agent.py
```

The application will execute the LangGraph workflow and demonstrate the sample customer queries provided in the assignment.

---

# Demonstration Queries

The system demonstrates the following customer queries:

1. What are the pricing plans available for your software?
2. I forgot my account password.
3. My application crashes whenever I upload a file.
4. I need a refund for my annual subscription.
5. What was my previous support issue?

---

# Features Implemented

* Intent Classification using LangGraph
* Conditional Agent Routing
* Specialized Department Agents
* Retrieval-Augmented Generation (FAISS)
* HuggingFace Embeddings
* SQLite Conversation Memory
* Human-in-the-Loop Approval
* Supervisor Agent
* Multi-Agent Workflow using LangGraph

---

# Notes

* Ensure that the `.env` file is **not committed** to the repository.
* Run `vector_db.py` before executing `agent.py`.
* Use the same `thread_id` while testing memory functionality so previous conversations can be recalled.
* The generated `vector_database/` directory is required for document retrieval.
