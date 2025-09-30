import json

from prompt_toolkit import prompt
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain.schema import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

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
   - Assume the `public` schema if none is specified by user.  
   - Do not guess, assume, or invent table/column names.
   - Always verify existence of tables and columns using `exec_sql_query` tool (see below).   
3. Tool Use: 
   - Tool do not support psql commands like "\\d" or "\\dt", it only supports valid SQL query.
   - Tool do not support multiple SQL statements, use single SQL statement per tool call.
   - To execute a query, call `exec_sql_query`.   
   - Input: `query` (SQL string) and `fetch_results` (boolean, default is False). 
   - For write/update statements, omit `fetch_results`.
   - For select statements, always inlcude `fetch_results=True` to gather results.
   - Always split multiple SQL statements into multiple `exec_sql_query` calls.
4. Response Format:
   - Always prefer table output.
   - Always include column headers to the table output.
   - Adjust table columns width so the output is readable and nicely formatted.
5. Behavior:
   - Do not provide speculative answers, fact check using SQL queries with `exec_sql_query` tool. 
   - Keep answers accurate, concise, and SQL-backed.
"""

bootstrap_prompt = """
Examine the public schema of current database using the `exec_sql_query` tool.:
* Examine following resources: tables, views, and columns.
* Use resources schema for generating, planning, and executing of SQL queries.
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
    print("+", query)
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
    memory = InMemorySaver()
    tools = [exec_sql_query]

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
        checkpointer=memory,
    )

    config = RunnableConfig()
    config["configurable"] = {"thread_id": "1"}

    print("Welcome to the PostgreSQL CLI tool, type 'exit' to quit.")
    print("<", "Allow me some time to lookup the database schema...")

    agent.invoke({"messages": [HumanMessage(content=bootstrap_prompt)]}, config)
    print("<", "Finished looking up the schema, please ask me a question!")

    while True:
        try:
            user_input = prompt("> ")
            if user_input.lower().strip() == "exit":
                break

            resp = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config)
            print("<", resp["messages"][-1].text())

        except (KeyboardInterrupt, EOFError):
            break

    print("Goodbye!")
    engine.dispose()
