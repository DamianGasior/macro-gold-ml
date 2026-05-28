import chromadb

client = chromadb.PersistentClient(path="src/llm/rag/chroma_db")
collection = client.get_collection("gold_rag")

# Ile chunków jest w bazie?
print(collection.count())

# Podejrzyj pierwsze 3 chunki (tekst + metadane + ID)
result = collection.peek(limit=3)
print(result)
