from graph_init import initialize_graph
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


db = sqlite3.connect(":memory:", check_same_thread=False)
memory = SqliteSaver(db)
# Initialize the graph
graph = initialize_graph()

# Compile the graph
runnable = graph.compile(checkpointer=memory)

# You can add code here to execute the graph or further actions.
# thread = {"configurable": {"thread_id": "a"}}


# human_message = HumanMessage(content="I want to rent a car")
# messages = [human_message]

# result = runnable.invoke({"messages":messages}, thread)

# print(result)

# print(result["response"])