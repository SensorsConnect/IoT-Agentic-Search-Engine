import os
import logging
from graph_init import initialize_graph

# Initialize the graph
graph = initialize_graph()

# Use PostgreSQL checkpointer if POSTGRES_URL is a postgres:// URL, otherwise use SQLite
POSTGRES_URL = os.environ.get("POSTGRES_URL", "")

if POSTGRES_URL and POSTGRES_URL.startswith(("postgresql://", "postgres://")):
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg_pool import ConnectionPool

    pool = ConnectionPool(
        conninfo=POSTGRES_URL,
        min_size=1,
        max_size=5,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
        max_idle=60,
        reconnect_timeout=30,
        open=True,
    )
    memory = PostgresSaver(pool)
    memory.setup()

    # One-time cleanup: clear stale checkpoints after schema migration
    try:
        with pool.connection() as conn_:
            conn_.execute("DELETE FROM checkpoints")
            conn_.execute("DELETE FROM checkpoint_writes")
            conn_.execute("DELETE FROM checkpoint_blobs")
        logging.info("Cleared stale LangGraph checkpoints for schema migration")
    except Exception as e:
        logging.warning(f"Could not clear old checkpoints: {e}")

    logging.info("Using PostgreSQL checkpointer for conversation persistence")
else:
    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3
    db = sqlite3.connect("checkpoints.db", check_same_thread=False)
    memory = SqliteSaver(db)
    logging.warning("Using SQLite file checkpointer (not recommended for production)")

# Compile the graph
runnable = graph.compile(checkpointer=memory)
