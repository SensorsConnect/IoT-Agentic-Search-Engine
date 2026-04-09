
from vector_database import vector_search, vector_db_push_batch

# Verify the index exists (skip rebuild if already done)
vector_db_push_batch()

# Run a search — returns top 3 matching service type names
results = vector_search("I need a coffee shop", limit=3)
print(results)
# ['coffee shop', 'convenience store', 'deli shop']

results = vector_search("looking for a pharmacy", limit=3)
print(results)
# ['pharmacy', 'convenience store', 'gourmet grocery store']

results = vector_search("I want pizza", limit=3)
print(results)
# ['pizza restaurant', 'delivery chinese restaurant', 'deli shop']

results = vector_search("I need a doctor", limit=3)
print(results)
# ['medical clinic', 'medical center', 'optometrist']

results = vector_search("gym to work out", limit=3)
print(results)
