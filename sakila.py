from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
import json
import mysql.connector
import os
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_openai import OpenAI, ChatOpenAI

# Function to get system instructions with the database schema
def get_system_instructions():
    """Provide database schema to help generate SQL statements."""
    schema_path = 'schema.txt'
    if not os.path.exists(schema_path):
        return "Error: schema.txt file not found."
    
    with open(schema_path, 'r') as file:
        schema = file.read()
    
    system_instruction = f"{schema}\n\n."
    return system_instruction

# @! add tool to search for given movie name on internet and provide synopsis using llm provider=google

@tool
def get_movie_synopsis(movie_title: str) -> str:
    """Searches for a movie synopsis using Google Search and an LLM."""
    try:
        search = GoogleSearchAPIWrapper()
        results = search.results(f"{movie_title} movie synopsis", 5)
        
        if results:
            llm = OpenAI(temperature=0)
            # Combine snippets from search results into a single prompt
            snippets = " ".join(result['snippet'] for result in results)
            prompt = f"Provide a concise synopsis for the movie '{movie_title}' based on the following information:\n\n{snippets}"
            
            # Use the LLM to generate a summary
            synopsis = llm.invoke(prompt)
            return synopsis
        else:
            return "Synopsis not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
# @! add tool to verify a given sql against a user prompt llm provider=openai

@tool
def verify_sql_with_prompt(sql_statement: str, user_prompt: str) -> str:
    """Verifies a given SQL statement against a user prompt using an LLM."""
    try:
        llm = OpenAI(temperature=0)
        prompt = f"Verify the SQL statement '{sql_statement}' against the user prompt '{user_prompt}'."
        verification_result = llm.invoke(prompt)
        return verification_result
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Tool to execute SQL queries
@tool
def execute_sql(sql_statement: str) -> str:
    """Execute SQL queries against the database.
    You can also use this to get or identify right entities to query against"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql_statement)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Define tools and ToolNode
tools = [execute_sql, get_movie_synopsis, verify_sql_with_prompt]
tool_node = ToolNode(tools)

# Bind tools to the model
model_with_tools = ChatOpenAI(
    model="gpt-4o", temperature=0
).bind_tools(tools)

# Node to call the system instructions
def call_get_system_instruction(state: MessagesState):
    """Call the get_system_instruction function and store its result."""
    instruction = get_system_instructions()
    return {"messages": [SystemMessage(content=instruction)]}


# Call the model with current state
def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

# Determine next action based on tool calls
def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Workflow definition
workflow = StateGraph(MessagesState)

# Add nodes to the workflow
workflow.add_node("get_system_instruction", call_get_system_instruction)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Define edges and transitions
workflow.add_edge(START, "get_system_instruction")
workflow.add_edge("get_system_instruction", "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Compile the workflow
app = workflow.compile()

# Example usage
for chunk in app.stream(
    {"messages": [("human", "find who rente gleaming jaw moview most, find its ID  and then provide its summary?")]}, stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
