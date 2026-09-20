import os
import logging
from typing import TypedDict, List, Literal, Annotated
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0,
    api_key=os.getenv('GROQ_API_KEY'),
    max_tokens=2000,
    reasoning_effort=None
)

MOCK_POLICY_DB = "Return Policy: Items can be returned within 30 days for a full refund if unused. Open items or items past 30 days are eligible only for store credit."

MOCK_ORDER_DB = {
    "12345": "Status: Shipped via Flipkart. Tracking ID: 12345XYZ. Status: Delayed due to weather conditions in transit.",
    "67890": "Status: Delivered yesterday at 4:15 PM. Signed for by receptionist.",
    "abcde": "Status: Processing at fulfillment center. Expected shipping date: Tomorrow morning."
}

class CustomerSupport(TypedDict):
    customer_query: str
    current_agent: str
    agent_logs: List[str]
    resolution: str
    order_id: str | None

def router_agent(state: CustomerSupport) -> dict:
    system_prompt = (
        "You are an expert triage supervisor for an e-commerce company.\n"
        "Analyze the user's intent and route the ticket to the best specialist.\n"
        "Return EXACTLY one word: 'policy' (for returns, refunds, rules, shipping terms) "
        "or 'order' (for status checks, tracking numbers, shipping delays, updates).\n"
        "If a specific order number/ID is mentioned, route to 'order'."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["customer_query"])
    ])
    
    result = response.content.strip().lower()
    if "order" in result:
        result = "order"
    else:
        result = "policy"
        
    return {
        "current_agent": result,
        "agent_logs": state.get("agent_logs", []) + [f"Triage routed to: {result}"]
    }

def policy_agent(state: CustomerSupport) -> dict:
    system_prompt = (
        "You are a professional, polite, and helpful Customer Policy Specialist.\n"
        f"Use this official policy data to answer the user: {MOCK_POLICY_DB}\n\n"
        "RULES:\n"
        "1. Answer the query confidently using the rules provided above.\n"
        "2. Never use system speak like 'according to the mock database' or 'I only have access to'. Speak naturally.\n"
        "3. If the query is outside this policy (e.g., asking for corporate contact details), politely inform them "
        "you do not have that structural information available on your terminal and offer to escalate to senior leadership."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["customer_query"]),
    ])
    return {
        "resolution": response.content,
        "agent_logs": state["agent_logs"] + ["Policy Agent resolved the issue."]
    }

def order_management(state: CustomerSupport) -> dict:
    query = state["customer_query"]
    

    found_status = "No direct order match found in the current system state."
    for order_id, status_info in MOCK_ORDER_DB.items():
        if order_id in query.lower() or order_id in query:
            found_status = f"Order ID {order_id} found. Details: {status_info}"
            break

    system_prompt = (
        "You are a stellar Live Order Tracking Specialist.\n"
        f"Here are the live results from the system lookup: {found_status}\n\n"
        "RULES:\n"
        "1. Communicate the status clearly, professionally, and with absolute human empathy.\n"
        "2. Never mention 'internal dictionary lookup' or 'mock lookup results'. Make it sound seamless.\n"
        "3. IF NO MATCH WAS FOUND (the user didn't provide a valid ID or asked a generic question like 'where is my order?'), "
        "ask them kindly to provide their 5-digit Order ID so you can check the real-time tracking network for them."
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ])
    return {
        "resolution": response.content,
        "agent_logs": state["agent_logs"] + ["Order Agent resolved the issue."]
    }

graph = StateGraph(CustomerSupport)
graph.add_node('router', router_agent)
graph.add_node('policy', policy_agent)
graph.add_node('order', order_management)
graph.set_entry_point("router")

def route_decision(state: CustomerSupport) -> Literal["policy", "order"]:
    if state["current_agent"] == "order":
        return "order"
    return "policy"

graph.add_conditional_edges("router", route_decision)
graph.add_edge("policy", END)
graph.add_edge("order", END)

checkpoint = InMemorySaver()
app = graph.compile(checkpointer=checkpoint)
