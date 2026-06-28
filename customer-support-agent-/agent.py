import os
from typing import Annotated, Literal, TypedDict,List
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage 
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver 
from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
import os

load_dotenv()

print("Current directory:", os.getcwd())
print("API KEY:", repr(os.getenv("GROQ_API_KEY")))





llm = ChatGroq(model="qwen/qwen3.6-27b", temperature=0,api_key=os.getenv("GROQ_API_KEY"))
embeddings= HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
new_vectorstore = FAISS.load_local(
       "vector_database", embeddings, allow_dangerous_deserialization=True
   )

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage],add_messages]
    classify:Literal['sales','technical_support','billing','account','memory']
    is_human_approval_required : bool
    query:str 

@tool 
def retreive_company_policy(query:str)->str :
    """
    based on the input query ,retrives and returns  the most relevant chunks 
    present in the company policy document
    used for queries relating to company policies  such as 
   it contains rules, procedures, and business policies, such as:

Refund policy
Cancellation policy
Account closure policy
Privacy policy
Escalation policy
Customer verification process

It answers questions like:

"Can I get a refund?"
"How is my data handled?"
"What is your cancellation policy?" 
like these type of questions 
    """
    
    filter={
        "source":"company_policy"
    }
    retreived_docs=new_vectorstore.similarity_search(
        query,k=3,filter=filter 
    )
    result ="upon searching the document the most relevant information are : \n"
    for doc in retreived_docs :
        result+=f"{doc.page_content} \n"

    return result

@tool 
def retreive_pricing_guide(query:str)->str :
    """
    based on the input query ,retrives and returns  the most relevant chunks 
    present in the pricing_guide document of the company 
    used for queries relating to short product description, like what does the product do 
    and the pricing guide - ie the pricing details of the product 
    
    """
    
    filter={
        "source":"pricing_guide"
    }
    retreived_docs=new_vectorstore.similarity_search(
        query,k=3,filter=filter 
    )
    result ="upon searching the document the most relevant information are : \n"
    for doc in retreived_docs :
        result+=f"{doc.page_content} \n"

    return result


@tool 
def retreive_technical_manual(query:str)->str :
    """
    based on the input query ,retrives and returns  the most relevant chunks 
    present in the technical_manual  document of the company 
    used for queries related to technical stuff of the company 
    """
    
    filter={
        "source":"technical_manual"
    }
    retreived_docs=new_vectorstore.similarity_search(
        query,k=3,filter=filter 
    )
    result ="upon searching the document the most relevant information are : \n"
    for doc in retreived_docs :
        result+=f"{doc.page_content} \n"

    return result

@tool 
def retreive_faq(query:str)->str :
    """
    based on the input query ,retrives and returns  the most relevant chunks 
    present in the frequently asked questions  document of the company 
    general frequently asked questions ,covering all aspects ,can be used to check if question similar to 
    query asked by the user is already answered 
    """
   
    filter={
        "source":"faq"
    }
    retreived_docs=new_vectorstore.similarity_search(
        query,k=3,filter=filter 
    )
    result ="upon searching the document the most relevant information are : \n"
    for doc in retreived_docs :
        result+=f"{doc.page_content} \n"

    return result

tools=[retreive_company_policy,retreive_faq,retreive_pricing_guide,retreive_technical_manual]
class ClassifyFormat(BaseModel):
    intent:Literal['sales','technical_support','billing','account','memory']

def classify_node(state : AgentState)->AgentState :


    prompt= f"""
classify the following prompt into strictly the following categories 
either 'sales' or 'technical_support' or 'billing' or 'account' or 'memory'
Choose memory ONLY if the user is asking about previous conversations,
past issues, earlier messages, previous interactions, or conversation history.
{state["messages"][-1].content}
"""


    structured_llm=llm.with_structured_output(ClassifyFormat)
    result=structured_llm.invoke(prompt)
    state["classify"]=result.intent
    state["query"]=state["messages"][-1].content 
    return state 

def sales_node (state: AgentState)->dict :
    """
    sales handle queries related to Product information, subscription plans, pricing details
    """
    state["is_human_approval_required"]=False 

    tool1=[retreive_pricing_guide,retreive_faq]
    llm_tools=llm.bind_tools(tool1)
    prompt=[SystemMessage(content="""

You are the Sales Support Agent for ABC Technologies.

Your responsibilities include:
- Product information
- Subscription plans
- Pricing details

Answer the customer's question accurately and professionally.

Whenever company-specific information is required, use the available tools instead of relying on your own knowledge.

If the information cannot be found using the available tools, politely inform the customer that you are unable to find the requested information.


""")]+ state["messages"]



    response=llm_tools.invoke(prompt)
    return {
    "messages":[response],
    "is_human_approval_required": state["is_human_approval_required"]
}

def technical_support_node(state: AgentState)->dict  :
    tool2=[retreive_technical_manual,retreive_faq]
    llm_tool=llm.bind_tools(tool2)
    state["is_human_approval_required"]=False 
    prompt=[SystemMessage(content="""

you are technical support agent . you handle queries relating to technical queries,your responsibilities 
are providing assistance to user based on 
Application errors, installation issues, login problems, configuration issues related issues 
if you are not able give the answer even after referring to tools, mention politely that you dont know 
dont hallucinate 

""")] + state["messages"]
    response=llm_tool.invoke(prompt)
    return {
    "messages":[response],
    "is_human_approval_required": state["is_human_approval_required"]
}

def billing_node(state : AgentState)->dict  :
    billing_tools=[retreive_company_policy,retreive_pricing_guide,retreive_faq]
    llm_tools= llm.bind_tools(billing_tools)
    query = state["query"].lower()

    if any(keyword in query for keyword in [
        "refund",
        "cancel subscription",
        "subscription cancellation",
        "compensation",
        "escalate",
        "management"
        ]):
        state["is_human_approval_required"]=True 
    else :
        state["is_human_approval_required"]=False
    prompt=[SystemMessage(content="""
you are a billing agent expert , you handle or respond to queries based on 

Invoice requests, payment issues, refund requests subscription cancellation
compensation requests, refer the tools for company related info , if you feel the need to do so 
if you are not able give the answer even after referring to tools, mention politely that you dont know 
dont hallucinate 



""")]+ state["messages"]
    
    response=llm_tools.invoke(prompt)
    return {
    "messages":[response],
    "is_human_approval_required": state["is_human_approval_required"]
}

def account_node(state:AgentState)->dict :
    account_tools=[retreive_company_policy,retreive_technical_manual,retreive_faq]
    llm_tools= llm.bind_tools(account_tools)
    query = state["query"].lower()

    account_closure_keywords = [
        "close my account",
        "delete my account",
        "deactivate my account",
        "remove my account",
        "terminate my account",
        "account closure",
        "close account"
    ]
    if any(keyword in query for keyword in account_closure_keywords):
        state["is_human_approval_required"]=True 
    else :
        state["is_human_approval_required"]=False 

    prompt=[SystemMessage(content="""
you are a account  agent expert , you handle or respond to queries based on 

Password reset, profile updates, account activation/deactivation and account closure requests and related tasks , refer the tools for company related info and policies  , if you feel the need to do so 
if you are not able give the answer even after referring to tools, mention politely that you dont know 
dont hallucinate 



""")] + state["messages"]
    
    response=llm_tools.invoke(prompt)
    return {
    "messages":[response],
    "is_human_approval_required": state["is_human_approval_required"]
}

def supervisor_node(state: AgentState)->AgentState:
    response=state["messages"][-1].content 
    print(f"response by ai is {response}\n")
    print ("to supervisor : is the given response ok ?\n")
    print("if its ok type 'yes' else type the full response that u want to give \n" )
    human_response=input()
    if(human_response=="yes"):
        return state 
    else :
        state["messages"].append(
    AIMessage(content=human_response)
)
        return state 

def end (state : AgentState)-> AgentState:
    return state 

def dummy_node(state:AgentState)->AgentState :
    return state #for tool call and human loop conditional edge 

def memory_node(state: AgentState):

    messages = [
        SystemMessage(
            content="""
You are a memory assistant.

Answer ONLY using the previous conversation history.

Do not make up information.

If the answer is not present in the conversation history,
say you do not know.
"""
        )
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages":[response]
    }

def router_classify(state : AgentState)->str :
    if state["classify"]=="account":
        return "account"
    elif state["classify"]=="billing":
        return "billing"
    elif state["classify"]=="sales":
        return "sales"
    elif state["classify"]=="technical_support" :
        return "technical_support"
    else :
        return "memory"
    

def router_supervisor(state :AgentState)->str :
    if(state["is_human_approval_required"]):
        return "human"
    else :
        return "end"
    
#creating tool list for all. 
sales_tools=[retreive_pricing_guide,retreive_faq]
technical_support_tools=[retreive_technical_manual,retreive_faq]
billing_tools=[retreive_company_policy,retreive_pricing_guide,retreive_faq]
account_tools=[retreive_company_policy,retreive_technical_manual,retreive_faq]

graph= StateGraph(AgentState)
graph.add_node("classify",classify_node)
graph.add_node("billing",billing_node)
graph.add_node("technical_support",technical_support_node)
graph.add_node("sales",sales_node)
graph.add_node("supervisor",supervisor_node)
graph.add_node("account",account_node)
graph.add_node("end",end)
graph.add_node("dummy",dummy_node)
graph.add_node("memory",memory_node)
#adding toool nodess 
graph.add_node("sales_tools",ToolNode(sales_tools))
graph.add_node("technical_support_tools",ToolNode(technical_support_tools))
graph.add_node("billing_tools",ToolNode(billing_tools))
graph.add_node("account_tools",ToolNode(account_tools))



graph.set_entry_point("classify")
graph.set_finish_point("end")

graph.add_conditional_edges("classify",router_classify,{
    "billing":"billing",
    "technical_support":"technical_support",
    "sales":"sales",
    "account":"account",
    "memory":"memory"
})

graph.add_edge("supervisor","end")
graph.add_edge("memory","end")
graph.add_conditional_edges(
    "dummy",router_supervisor,{
        "human":"supervisor",
        "end":"end"
    }
)



#adding tools edges 

graph.add_conditional_edges(
    "sales",
    tools_condition,
    {
        "tools": "sales_tools",  
        "__end__": "end"            
    }
)


graph.add_edge("sales_tools", "sales")

graph.add_conditional_edges(
    "technical_support",tools_condition,{
        "tools":"technical_support_tools",
        "__end__":"end"
    }
)

graph.add_edge("technical_support_tools","technical_support")

#add cond edges with human in loop and tool 
graph.add_conditional_edges(
    "billing",tools_condition,{
        "tools":"billing_tools",
        "__end__":"dummy"
    }


)
graph.add_edge(
    "billing_tools","billing"
)
graph.add_conditional_edges(
    "account",tools_condition,{
        "tools":"account_tools",
        "__end__":"dummy"
    }
)
graph.add_edge(
    "account_tools","account"
)


if __name__ == "__main__":

    with SqliteSaver.from_conn_string("memory.db") as memory:

        agent = graph.compile(
            checkpointer=memory
        )

        config = {
            "configurable": {
                "thread_id": "shrini"
            }
        }

        queries = [
            "What are the pricing plans available for your software?",
            "I forgot my account password.",
            "My application crashes whenever I upload a file.",
            "I need a refund for my annual subscription.",
            "What was my previous support issue?"
        ]

        for i, query in enumerate(queries, start=1):

            result = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=query)
                    ]
                },
                config=config
            )

            print(f"\nQuery {i}: {query}")
            print(result["classify"])
            print(result["messages"][-1].content)

