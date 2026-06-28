# Business Requirement Mapping

This section explains how each business requirement specified in the problem statement has been implemented in the proposed LangGraph-based Customer Support Automation System.

| Business Requirement                                              | Implementation                                                                                                                                                                                                                                                                                 |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Accept customer queries**                                       | The workflow begins by accepting a customer query through the LangGraph entry point. The query is stored in the shared `AgentState` and added to the conversation history.                                                                                                                     |
| **Identify the customer's issue type**                            | The **Intent Classification Node** analyzes the customer query using a Large Language Model with structured output and classifies it into one of the supported departments: Sales, Technical Support, Billing, Account (and Memory for conversation recall if implemented).                    |
| **Route the query to the appropriate support department**         | Conditional edges are used to dynamically route the workflow to the corresponding department node based on the predicted intent. This ensures that every query is handled by a specialized support agent.                                                                                      |
| **Retrieve relevant information from company documents**          | Each department agent has access to one or more retrieval tools. These tools perform semantic search over a FAISS vector database containing embeddings generated from the company knowledge base. Metadata filtering ensures that only the relevant document is searched.                     |
| **Remember previous customer interactions**                       | LangGraph's SQLite Checkpointer stores the complete graph state, including conversation history (`messages`), allowing future customer queries to reference previous interactions using the same `thread_id`.                                                                                  |
| **Escalate critical requests to a human supervisor for approval** | Billing and Account agents perform keyword-based detection of high-risk requests such as refunds, account closure, subscription cancellation, compensation, and escalation requests. If detected, the workflow routes the request to the Supervisor Node before generating the final response. |
| **Generate the final customer response**                          | After retrieving the required knowledge and optionally receiving supervisor approval, the department agent generates the final response and returns it to the customer.                                                                                                                        |

---

# Requirement-wise Implementation

## 1. Customer Query Acceptance

The workflow starts by accepting a customer query through LangGraph.

The incoming query is stored inside the shared `AgentState` and appended to the `messages` list. Since `messages` uses LangGraph's `add_messages` reducer, the complete conversation history is maintained automatically throughout graph execution.

---

## 2. Intent Identification

The Intent Classification Node is responsible for understanding the customer's request.

The node uses a Large Language Model with structured output to classify the query into one of the supported departments.

Supported intents include:

* Sales
* Technical Support
* Billing
* Account
* Memory (conversation recall)

The predicted intent is stored in the `classify` field of the shared state.

---

## 3. Intelligent Department Routing

Once the customer's intent has been identified, LangGraph Conditional Edges route the workflow to the corresponding specialized department.

Routing logic:

```text
Sales  → Sales Agent

Technical Support → Technical Agent

Billing → Billing Agent

Account → Account Agent

Memory → Memory Node
```

This modular architecture ensures that each support request is handled by an agent specialized in that business domain.

---

## 4. Retrieval-Augmented Generation (RAG)

Instead of relying solely on the LLM's internal knowledge, department agents retrieve company-specific information from the organization's knowledge base.

The knowledge base consists of four documents:

* Company Policy
* Pricing Guide
* Technical Manual
* FAQ

These documents are:

1. Loaded into memory.
2. Split into overlapping chunks.
3. Converted into dense vector embeddings using HuggingFace Embeddings.
4. Stored inside a FAISS Vector Database.

Whenever an agent requires company-specific information, it invokes the appropriate retrieval tool.

The retrieval tool:

* Performs semantic similarity search.
* Filters results using document metadata.
* Returns the most relevant document chunks to the LLM.

This enables accurate and context-aware customer responses.

---

## 5. Specialized Department Agents

Each business department is implemented as an independent LangGraph node.

### Sales Agent

Handles:

* Product information
* Subscription plans
* Pricing

Available tools:

* Pricing Guide Retriever
* FAQ Retriever

---

### Technical Support Agent

Handles:

* Application crashes
* Login issues
* Installation problems
* Configuration issues

Available tools:

* Technical Manual Retriever
* FAQ Retriever

---

### Billing Agent

Handles:

* Refund requests
* Invoice requests
* Payment issues

Available tools:

* Company Policy Retriever
* Pricing Guide Retriever
* FAQ Retriever

The Billing Agent additionally detects whether the request requires Human-in-the-Loop approval.

---

### Account Agent

Handles:

* Password reset
* Profile updates
* Account activation
* Account deactivation

Available tools:

* Company Policy Retriever
* Technical Manual Retriever
* FAQ Retriever

The Account Agent also checks whether the customer is requesting account closure.

---

## 6. Human-in-the-Loop Approval

Certain customer requests cannot be automatically approved according to company policy.

The Billing and Account agents perform keyword-based detection for high-risk requests.

These include:

* Refund requests
* Subscription cancellation
* Account closure
* Compensation requests
* Escalation to management

When such requests are detected:

```text
Department Agent

↓

Supervisor Node

↓

Customer Response
```

The Supervisor reviews the generated response and may either approve it or modify it before it is returned to the customer.

This ensures compliance with business policies while keeping the rest of the workflow fully automated.

---

## 7. SQLite Conversation Memory

Long-term conversation memory is implemented using LangGraph's SQLite Checkpointer.

The checkpointer automatically stores:

* Conversation history
* Shared graph state
* Intermediate graph checkpoints

using a unique `thread_id`.

When the same customer interacts again, LangGraph restores the previous graph state before executing the workflow.

This enables responses such as:

```text
Customer:
My name is David.

Customer:
I have a billing issue.

Customer:
What was my previous support issue?
```

The Memory Node (or restored conversation history) allows the system to answer using previous interactions without requiring the user to repeat information.

---

## 8. Final Response Generation

After retrieval and optional supervisor approval, the corresponding department agent generates the final customer response.

The response is grounded using retrieved company documents, previous conversation history, and department-specific instructions.

The generated response is then returned to the customer, completing the workflow.

---

# Summary

The proposed LangGraph workflow satisfies every functional requirement specified in the problem statement by combining intelligent routing, Retrieval-Augmented Generation, persistent SQLite memory, specialized support agents, and Human-in-the-Loop approval into a unified multi-agent customer support system.
