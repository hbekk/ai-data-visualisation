import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from models.database import vector_collection as collection

def fetch_embeddings_from_db():

    cursor = collection.find({}, {
        "natural_query": 1,
        "BSON-Float32-Embedding": 1,
        "isText": 1
    })

    embeddings = []
    labels = []
    colors = []

    for doc in cursor:
        embedding = doc.get("BSON-Float32-Embedding")
        if embedding:
            embeddings.append(np.array(embedding, dtype=np.float32))  
            labels.append(doc.get("natural_query", "")[:60])  
            colors.append("green" if doc.get("isText") else "purple")  
    
    return np.array(embeddings), labels, colors

def perform_pca(embeddings):
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)
    return reduced_embeddings

def plot_embeddings(reduced_embeddings, labels, colors):
    plt.figure(figsize=(12, 8))
    plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=colors, alpha=0.7)

    label_count = len(labels)
    
    for i in range(label_count):
        if i % 2 == 0:  
            x, y = reduced_embeddings[i, 0], reduced_embeddings[i, 1]
            
            plt.annotate(labels[i], 
                         (x, y), 
                         fontsize=8, 
                         textcoords="offset points", 
                         xytext=(0, 9),  
                         ha='center', 
                         color='black')

    plt.title("PCA of Vector Embeddings")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.grid(True)
    plt.show()

def show_embedding():
    embeddings, labels, colors = fetch_embeddings_from_db()
    
    if embeddings.size == 0:
        print("No embeddings found.")
        return

    reduced_embeddings = perform_pca(embeddings)
    plot_embeddings(reduced_embeddings, labels, colors)

if __name__ == "__main__":
    show_embedding()
