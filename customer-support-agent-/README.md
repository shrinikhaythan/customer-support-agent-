# customer-support-agent-
#PROBLEM STATEMENT - EXACTLY AS GIVEN 
1. Background

ABC Technologies is a SaaS company that provides cloud-based business management software to thousands of customers worldwide.

The company receives a large volume of daily support requests covering product information, technical issues, billing queries, account management, and refund requests.

All requests are currently handled manually by support executives, resulting in longer response times and higher operational costs. To improve efficiency, the company wants to build an AI-Powered Customer Support Automation System using LangGraph.

2. Business Requirements

The system should:

1.     Accept customer queries.

2.     Identify the customer's issue type.

3.     Route the query to the appropriate support department.

4.     Retrieve relevant information from company documents.

5.     Remember previous customer interactions.

6.     Escalate critical requests to a human supervisor for approval.

7.     Generate a final response for the customer.

3. Available Support Departments

Department

Handles

Sales

Product information, subscription plans, pricing details

Technical Support

Application errors, installation issues, login problems, configuration issues

Billing

Invoice requests, payment issues, refund requests

Account

Password reset, profile updates, account activation/deactivation


4. Knowledge Base Documents

The AI system should retrieve relevant information from the following documents whenever required:

•       Company Policy Document

•       Pricing Guide

•       Technical Manual

•       FAQ Document

5. Human-in-the-Loop Requirement

The following request types must not be approved automatically. They must be reviewed and approved by a human supervisor before the final response is sent to the customer:

•       Refund requests

•       Subscription cancellation

•       Account closure requests

•       Compensation requests

•       Escalation to management

6. Memory Requirement

The system should maintain customer conversation history using SQLite memory. For example:

Customer: “My name is David. I have a billing issue.”

Customer (later): “What was my previous issue?”

The system should retrieve and answer using stored memory.

7. Tasks

Complete the following ten tasks in order. Each task builds on the previous one.

Task

Description

Task 1

Design a LangGraph workflow for the Customer Support Automation System.

Task 2

Create a suitable State structure to manage customer information, query details, retrieved context, approval status, and responses.

Task 3

Implement an Intent Classification node that categorizes customer queries into Sales, Technical, Billing, or Account.

Task 4

Implement conditional routing to direct queries to the appropriate support agent.

Task 5

Develop specialized agents for Sales Support, Technical Support, Billing Support, and Account Support.

Task 6

Integrate a RAG pipeline using the provided company documents.

Task 7

Implement SQLite-based memory to store and retrieve customer conversation history.

Task 8

Design a human-in-the-loop approval process for high-risk customer requests.

Task 9

Create a Supervisor agent that validates and improves responses before they are sent to customers.

Task 10

Demonstrate the system using the five sample customer queries provided.



8. Demonstration Queries

Demonstrate the completed system using the following sample customer queries:

#

Sample query

Expected path

Query 1

What are the pricing plans available for your software?

Sales

Query 2

I forgot my account password.

Account

Query 3

My application crashes whenever I upload a file.

Technical Support

Query 4

I need a refund for my annual subscription.

Billing — requires human approval

Query 5

What was my previous support issue?

Memory recall — no department routing



9. Expected Deliverables

•       LangGraph workflow diagram

•       Source code

•       RAG integration

•       SQLite memory implementation

•       Human-in-the-loop workflow

•       Documentation report

•       Project demonstration

10. Submission Checklist

Students must upload a single ZIP file containing:

Source Code (.zip) – Complete project files with comments.
README.md – Project description, setup steps, and run instructions.
Workflow Diagram – LangGraph architecture diagram (PNG/JPG/PDF).
Screenshots PDF – Screenshots of project execution and outputs.
SQLite Memory File/Schema – Database file (memory.db) or schema script.
Task Output Screenshots – 
Agent Routing
Human-in-the-Loop
RAG Retrieval
Memory Storage & Recall
Final Response Generation