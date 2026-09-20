# 💬 Multi-Agent Customer Support Agent

A production-grade, multi-agent customer service assistant built using **LangGraph**, **LangChain Groq (Qwen 2.5)**, and a custom **Streamlit UI**. 

This system uses a smart triage router to automatically analyze customer intent and delegate tasks to specialized agents (Order Management vs. Company Policy) while maintaining persistent chat history and a real-time word-streaming interface.

---

## 🚀 Key Features

- **Triage Supervisor Node:** Dynamically analyzes incoming customer queries using LLM intent classification and routes the ticket to the appropriate specialist.
- **Order Management Specialist:** Simulates a secure internal system scanner that matches user queries against a simulated e-commerce tracking network.
- **Corporate Policy Specialist:** Confidently handles rules regarding return timelines and refund eligibility windows while offering polite, human-centric fallback options for out-of-scope inquiries.
- **Premium Chat Canvas:** A streamlined, black-themed (`#111111`) chat screen built with Streamlit featuring asynchronous word-by-word text streaming emulation.
- **Local Persistence & Feedback:** Automatically records full chat sessions to a local `chat_history.json` layout, enabling multi-session selection via a sidebar along with live helpfulness ratings (👍 / 👎).

---

## 🛠️ Project Architecture

```text
               +-----------------------+

               |  User Input (Chat)    |
               +-----------+-----------+
                           |
                           v
               +-----------------------+

               |   Router (Triage)     |
               +-----+-----------+-----+

                     |           |
       [If 'order']  |           | [If 'policy']
                     v           v
        +------------+----+  +---+------------+

        |  Order Agent    |  |  Policy Agent  |
        | (Mock Database) |  |  (Policy DB)   |
        +------------+----+  +---+------------+

                     |           |
                     +-----+-----+
                           |
                           v
               +-----------+-----------+

               |  Resolution Output    |
               +-----------------------+
```

---

## 💻 Tech Stack

- **Framework:** LangGraph (StateGraph, InMemorySaver)
- **LLM Engine:** ChatGroq (`qwen/qwen3.8-27b`)
- **Frontend App:** Streamlit (Chat UI Elements & Custom CSS)
- **Environment:** Python Dotenv & Pydantic

---

## 🔧 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com
   cd Customer_Support_Agent
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root directory and securely paste your Groq credential:
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```
   *(Note: The `.env` file is already added to `.gitignore` to protect your tokens from being leaked.)*

3. **Install Dependencies:**
   ```bash
   pip install streamlit langchain-groq langgraph pydantic python-dotenv
   ```

4. **Launch the Application:**
   ```bash
   streamlit run app.py
   ```

---

## 📂 Project Structure

- `customer_support.py` - Core graph topology setup, agent node definitions, and edge logic rules.
- `app.py` - User canvas wrapper engine, custom css style injections, local tracking history state storage, and streaming logic execution.
- `.gitignore` - Safeguards your local tracking json caches and active API credentials.
