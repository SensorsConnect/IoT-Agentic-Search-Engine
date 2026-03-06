import os
import logging
from graph_init import initialize_graph

# Initialize the graph
graph = initialize_graph()

# Use PostgreSQL checkpointer if POSTGRES_URL is a postgres:// URL, otherwise use SQLite
POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

if POSTGRES_URL and POSTGRES_URL.startswith(("postgresql://", "postgres://")):
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg import Connection

    conn = Connection.connect(POSTGRES_URL, autocommit=True, prepare_threshold=0)
    memory = PostgresSaver(conn)
    memory.setup()
    logging.info("Using PostgreSQL checkpointer for conversation persistence")
else:
    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3
    db = sqlite3.connect("checkpoints.db", check_same_thread=False)
    memory = SqliteSaver(db)
    logging.warning("Using SQLite file checkpointer (not recommended for production)")

# Compile the graph
runnable = graph.compile(checkpointer=memory)
