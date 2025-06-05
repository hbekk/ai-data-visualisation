from models.embeddings import get_embedding, generate_vector, vector_collection


"""
VECTOR EMBEDDING TEMPLATE:

"natural_query": query[0],  
"mongo_query": query[1],    
"BSON-Float32-Embedding": bson_f32_emb,
"isText": query[3],
"chartType": query[4],

queries = [
    [
        "Vis OBJECT verdiene på X", 
        {
            "timestamp": {
                "$gte": "X TIME_OF_DAY START",
                "$lte": "X TIME_OF_DAY END"
            },
            "metadata.name": {
                "$in": "OBJECT"
            },
        },
        None, ## Placeholder for embedding
        True, ## isText (For response)
        None, ## Placeholder for chart type
    ],

"""


# EMBED AND ADD QUERY TO VECTOR DB
def embed_query():
    queries = [
    # Minimum Value Queries (English)
    [
        "What was the standard deviation on x",
        {
            "timestamp": {
                "$gte": "X TIME_OF_DAY START",
                "$lte": "X TIME_OF_DAY END"
            },
            "metadata.name": {
                "$in": "OBJECT"
            }
        },
        None,
        True,
        None,
    ],
    
]

    # Extract natural queries
    natural_queries = [query[0] for query in queries]
    
    # Get embeddings for the natural queries
    float32_embeddings = get_embedding(natural_queries, precision="float32")

    # Generate BSON vector embeddings
    bson_float32_embeddings = [generate_vector(f32_emb) for f32_emb in float32_embeddings]

    # Create documents with the embedding and MongoDB query
    docs = []
    for (bson_f32_emb, query) in zip(bson_float32_embeddings, queries):
        doc = {
            "natural_query": query[0],  
            "mongo_query": query[1],    
            "BSON-Float32-Embedding": bson_f32_emb,
            "isText": query[3],
            "chartType": query[4]
        }
        docs.append(doc)
    
    # Insert documents into the vector collection
    vector_collection.insert_many(docs)  
    
    print("Query stored.")

if __name__ == "__main__":
    embed_query()
