# customer-support-agent-

# AI-Powered Customer Support Automation System using LangGraph

## Overview

This project implements an **AI-Powered Customer Support Automation System** for **ABC Technologies** using **LangGraph**, **LangChain**, **FAISS**, **HuggingFace Embeddings**, **SQLite Memory**, and **Groq LLMs**.

The system automates customer support by classifying customer queries, routing them to specialized department agents, retrieving company-specific knowledge through Retrieval-Augmented Generation (RAG), maintaining conversation memory, and incorporating Human-in-the-Loop (HITL) approval for sensitive requests.

The entire workflow follows a modular multi-agent architecture where each department is represented by an independent AI agent.

---

# Technologies Used

* LangGraph
* LangChain
* Groq LLM (Qwen 3.6 27B)
* HuggingFace Embeddings (all-MiniLM-L6-v2)
* FAISS Vector Database
* SQLite Checkpointer
* Python
* Pydantic

---

# System Architecture

```
                         User Query
                              │
                              ▼
                  Intent Classification Node
                              │
      ┌──────────────┬─────────┼────────────┬─────────────┬─────────────┐
      ▼              ▼         ▼            ▼             ▼
  Sales Agent   Technical   Billing      Account      Memory Node
                   Agent       Agent         Agent
      │              │            │             │
      ▼              ▼            ▼             ▼
 Sales Tool      Technical     Billing      Account
   Node          Tool Node     Tool Node    Tool Node
      │              │            │             │
      └──────────────┴────────────┴─────────────┘
                              │
                              ▼
                 Human Approval Required?
                      │               │
                     Yes              No
                      │               │
                      ▼               ▼
              Supervisor Node        END
                      │
                      ▼
                     END
```

---

# Workflow Description

The workflow begins by accepting a customer query.

The query is first passed to the **Intent Classification Node**, which classifies the request into one of the available customer support departments.

Depending on the predicted intent, the workflow routes the request to the corresponding specialized department agent.

Each department agent is capable of invoking retrieval tools whenever company-specific information is required. The retrieval tools perform semantic search over the vector database and return the most relevant document chunks.

For high-risk requests such as refunds, subscription cancellations, account closures, compensation requests, or escalation requests, the workflow routes the response to a Human Supervisor before sending the final answer to the customer.

Conversation history is maintained using SQLite checkpoint memory, enabling the system to answer questions based on previous interactions.

---

# State Structure

The workflow maintains the following shared state.

| Field                      | Description                                       |
| -------------------------- | ------------------------------------------------- |
| messages                   | Complete conversation history                     |
| classify                   | Predicted customer department                     |
| query                      | Current customer query                            |
| is_human_approval_required | Indicates whether supervisor approval is required |

The `messages` field is automatically updated using LangGraph's `add_messages` reducer.

---

# Intent Classification Node

The first node in the workflow is responsible for understanding the customer's intent.

Responsibilities:

* Analyze customer query
* Predict department
* Store department in state
* Store original query

Possible classifications:

* Sales
* Technical Support
* Billing
* Account
* Memory (optional extension)

---

# Sales Support Agent

The Sales Agent handles customer requests related to:

* Product information
* Subscription plans
* Pricing details

Available Tools

* Pricing Guide Retriever
* FAQ Retriever

Workflow

```
Sales Agent
      │
Tool Needed?
      │
 ┌────┴─────┐
 │          │
No         Yes
 │          │
 ▼          ▼
END     Sales Tool Node
             │
             ▼
        Sales Agent
             │
             ▼
            END
```

---

# Technical Support Agent

Responsibilities

* Installation issues
* Application crashes
* Configuration issues
* Login problems
* Error troubleshooting

Available Tools

* Technical Manual Retriever
* FAQ Retriever

The agent retrieves troubleshooting steps before generating a response.

---

# Billing Agent

Responsibilities

* Payment issues
* Invoice requests
* Refund requests

Available Tools

* Company Policy Retriever
* Pricing Guide Retriever
* FAQ Retriever

Additional Logic

The Billing Agent detects whether Human Approval is required.

The following requests require approval:

* Refund request
* Subscription cancellation
* Compensation request
* Escalation request

If approval is required, control is transferred to the Supervisor Node.

---

# Account Agent

Responsibilities

* Password reset
* Account activation
* Account deactivation
* Profile updates

Available Tools

* Company Policy Retriever
* Technical Manual Retriever
* FAQ Retriever

Additional Logic

The Account Agent detects account closure requests.

Examples include:

* Delete account
* Close account
* Deactivate account
* Terminate account

These requests require Human approval.

---

# Memory Node

The Memory Node answers customer questions related to previous interactions.

Example

Customer:

> My name is David.

Later

Customer:

> What was my previous issue?

The node retrieves previous conversation history from SQLite checkpoint memory.

No department routing is required.

---

# Retrieval-Augmented Generation (RAG)

The project uses Retrieval-Augmented Generation to answer company-specific questions.

Knowledge Base

* Company Policy
* Pricing Guide
* Technical Manual
* FAQ

---

## Vector Database Creation

The documents are loaded from the knowledge base directory.

Each document is:

1. Read from disk
2. Split into overlapping chunks
3. Converted into embeddings
4. Stored in a FAISS vector database

Metadata is assigned to every chunk.

Example

```
source = company_policy
```

This enables metadata filtering during retrieval.

---

# Retrieval Tools

## Company Policy Retriever

Purpose

Retrieves policy-related information.

Examples

* Refund policy
* Cancellation policy
* Account closure policy
* Privacy policy

---

## Pricing Guide Retriever

Purpose

Retrieves

* Product information
* Subscription plans
* Pricing

---

## Technical Manual Retriever

Purpose

Retrieves

* Troubleshooting steps
* Configuration instructions
* Installation procedures

---

## FAQ Retriever

Purpose

Retrieves frequently asked customer questions.

This tool is usually consulted before larger knowledge documents.

---

# Tool Routing

Each department owns a Tool Node.

The LLM decides whether tool execution is necessary.

If a tool call exists

```
Agent
   │
ToolNode
   │
Agent
```

Otherwise

```
Agent
   │
 END
```

This follows the standard ReAct execution pattern provided by LangGraph.

---

# Human-in-the-Loop

Certain customer requests cannot be automatically approved.

The workflow performs keyword detection to determine whether approval is required.

Requests requiring approval include:

* Refund requests
* Subscription cancellation
* Account closure
* Compensation
* Escalation to management

If approval is required

```
Department Agent
        │
        ▼
Supervisor
        │
        ▼
       END
```

Otherwise

```
Department Agent
        │
        ▼
       END
```

The Supervisor reviews the generated response and may either approve it or modify it before it is returned to the customer.

---

# SQLite Memory

Conversation history is maintained using LangGraph SQLite Checkpointer.

The checkpointer stores:

* Messages
* State
* Graph checkpoints

The same `thread_id` is reused across multiple interactions.

This enables long-term conversational memory.

Example

```
Customer:
My name is David.

Customer:
I have a billing issue.

Customer:
What was my previous issue?
```

The workflow retrieves previous messages automatically and allows the LLM to answer using conversation history.

---

# Graph Routing

The graph uses conditional routing.

Intent Routing

```
Classifier

↓

Sales
Technical
Billing
Account
Memory
```

Tool Routing

```
Agent

↓

Tool Needed?

↓

Yes → ToolNode

↓

Agent

↓

END
```

Supervisor Routing

```
Approval Required?

↓

Yes

↓

Supervisor

↓

END

No

↓

END
```

---

# Business Requirements Satisfaction

| Requirement                 | Implementation       |
| --------------------------- | -------------------- |
| Accept customer queries     | LangGraph Entry Node |
| Intent identification       | Classification Node  |
| Department routing          | Conditional Edges    |
| Company document retrieval  | RAG + FAISS          |
| Previous interaction memory | SQLite Checkpointer  |
| Human approval              | Supervisor Node      |
| Final response generation   | Department Agents    |

---

# Demonstration Queries

## Query 1

```
What are the pricing plans available for your software?
```

Expected Route

```
Classifier
↓

Sales

↓

Pricing Tool

↓

Sales

↓

END
```

---

## Query 2

```
I forgot my account password.
```

Expected Route

```
Classifier

↓

Account

↓

Technical Manual

↓

Account

↓

END
```

---

## Query 3

```
My application crashes whenever I upload a file.
```

Expected Route

```
Classifier

↓

Technical

↓

Technical Manual

↓

Technical

↓

END
```

---

## Query 4

```
I need a refund for my annual subscription.
```

Expected Route

```
Classifier

↓

Billing

↓

Company Policy

↓

Billing

↓

Supervisor

↓

END
```

---

## Query 5

```
What was my previous support issue?
```

Expected Route

```
Classifier

↓

Memory

↓

END
```

---

# Project Outcome

The developed Customer Support Automation System demonstrates the use of LangGraph for orchestrating multiple AI agents capable of intelligent routing, Retrieval-Augmented Generation, conversational memory, and Human-in-the-Loop approval.

The modular architecture enables independent support agents for different business departments while ensuring company-specific responses through document retrieval and maintaining customer context across multiple conversations using SQLite checkpoint memory.
