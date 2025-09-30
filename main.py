import json
from prompt_toolkit import prompt
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine("postgresql://postgres:postgres@localhost/postgres")

system_prompt = """
You are an English-speaking AI assistant connected to a PostgreSQL 15 database.
You must answer user questions by planning and executing SQL queries.
Start answering by examining the database schema and then generating SQL queries to answer the question.

Guidelines:
1. SQL Grammar: Follow PostgreSQL 15 SQL reference — https://www.postgresql.org/docs/15/sql.html.    
2. Schema Awareness:
   - Do not guess or invent table/column names.
   - Always verify existence of tables and columns in the schema.
   - Assume the `public` schema if none is specified.  
3. Tool Use: 
   - To execute a query, call `exec_sql_query`.  
   - Input: `query` (SQL string) and `fetch_results` (boolean, default is False). 
   - For write/update statements, omit `fetch_results`.
   - For select statements, always inlcude `fetch_results=True` to gather results.
   - Always split multiple SQL statements into multiple `exec_sql_query` calls.
4. Response Format:
   - Prefer tabular output.  
   - Always include column headers.  
   - Align columns with equal widths.
5. Behavior:
   - Do not provide speculative answers, fact check using SQL queries. 
   - Keep answers accurate, concise, and SQL-backed.
"""


def serialize_rows(rows):
    """Serialize SQLAlchemy Row objects to plain JSONable dicts."""
    out = []
    for r in rows:
        try:
            out.append({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(r._mapping).items()})
        except Exception:
            out.append(dict(r))
    return out


@tool
def exec_sql_query(query: str = "", fetch_results: bool = False):
    """Execute a SQL query against the PostgreSQL database.

    Args:
        query (str): The SQL query to execute.
        fetch_results (bool): Whether to fetch results from the query.
    """
    print("?", query)
    try:
        with engine.connect() as conn:
            conn.execution_options(isolation_level="AUTOCOMMIT")
            result = conn.execute(text(query))
            if fetch_results:
                rows = result.fetchall()
                return json.dumps({"status": "ok", "rows": serialize_rows(rows)})
            else:
                return json.dumps({"status": "ok", "rowcount": result.rowcount})

    except SQLAlchemyError as e:
        return json.dumps({"status": "error", "error": str(e)})


if __name__ == "__main__":
    model = ChatOllama(model="qwen2.5:14b")
    tools = [exec_sql_query]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    llm_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

    agent = create_tool_calling_agent(model, tools, llm_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

    print("Welcome to the PostgreSQL CLI tool, type 'exit' to quit.")
    print("Allow me some time to lookup the database schema...")
    
    agent_executor.invoke({"input": "List all tables and their columns in the public schema and memorize them."})
    print("Finished looking up the schema, please ask me a question.")
    while True:
        try:
            user_input = prompt("> ")
            if user_input.lower().strip() == "exit":
                break

            resp = agent_executor.invoke({"input": user_input})
            print("<", resp["output"])
        except (KeyboardInterrupt, EOFError):        
            break

    print("Goodbye!")
    engine.dispose()
