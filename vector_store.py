
# import os
# import uuid
# import json
# from typing import List

# from google.cloud import aiplatform
# from google.cloud import storage
# from sentence_transformers import SentenceTransformer

# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# # Initialize Vertex AI
# PROJECT_ID = os.getenv("GCP_PROJECT_ID")
# LOCATION = os.getenv("GCP_REGION", "us-central1")
# BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")

# aiplatform.init(project=PROJECT_ID, location=LOCATION)

# class VertexVectorStore:
#     def __init__(self):
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")
#         self.index = None
#         self.index_endpoint = None
#         self.deployed_index_id = None

#     def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
#         return self.model.encode(texts).tolist()

#     def _upload_to_gcs(self, data: List[dict], destination_blob_name: str):
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(BUCKET_NAME)
#         blob = bucket.blob(destination_blob_name)
#         blob.upload_from_string(
#             data="\n".join(json.dumps(record) for record in data),
#             content_type="application/json"
#         )
#         return f"gs://{BUCKET_NAME}/{destination_blob_name}"

#     def create_index(self, texts: List[str], index_display_name: str):
#         embeddings = self._generate_embeddings(texts)
#         data = [
#             {
#                 "id": str(uuid.uuid4()),
#                 "embedding": embedding
#             }
#             for embedding in embeddings
#         ]
#         gcs_uri = self._upload_to_gcs(data, f"{index_display_name}_data.json")

#         self.index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
#             display_name=index_display_name,
#             contents_delta_uri=gcs_uri,
#             dimensions=len(embeddings[0]),
#             approximate_neighbors_count=100
#         )
#         self.index.wait()

#         self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
#             display_name=f"{index_display_name}_endpoint",
#             public_endpoint_enabled=True
#         )
#         self.index_endpoint.wait()

#         self.deployed_index_id = f"{index_display_name}_deployed"
#         self.index_endpoint.deploy_index(
#             index=self.index,
#             deployed_index_id=self.deployed_index_id
#         )

#     def search(self, query: str, k: int = 3) -> List[str]:
#         if not self.index_endpoint or not self.deployed_index_id:
#             raise ValueError("Index and endpoint must be created and deployed before searching.")

#         query_embedding = self._generate_embeddings([query])[0]
#         response = self.index_endpoint.find_neighbors(
#             deployed_index_id=self.deployed_index_id,
#             queries=[query_embedding],
#             num_neighbors=k
#         )

#         # Extract and return the IDs of the nearest neighbors
#         neighbors = response[0].neighbors
#         return [neighbor.datapoint.datapoint_id for neighbor in neighbors]




##################################################
###########################################
####################################
############################
##################
# # below code is to store the pdf in local memory


# enhanced_vector_store.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
from collections import defaultdict

class VectorStore:
    def __init__(self):
        self.chunks = []  # List of dicts: {"text": ..., "metadata": {...}}
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)
        self.chunk_embeddings = []
        print("✅ Vector model loaded.")

    def _semantic_chunk(self, text, max_words=300, overlap=50):
        # Split by paragraphs
        raw_chunks = re.split(r"\n\s*\n", text)
        refined_chunks = []
        for chunk in raw_chunks:
            words = chunk.split()
            if len(words) <= max_words:
                refined_chunks.append(chunk)
            else:
                # Overlapping sliding window
                for i in range(0, len(words), max_words - overlap):
                    sub_chunk = " ".join(words[i:i + max_words])
                    refined_chunks.append(sub_chunk)
        return refined_chunks

    def add_texts(self, full_text, metadata_base):
        chunks = self._semantic_chunk(full_text)
        embeddings = self.model.encode(chunks)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "chunk_index": i,
                **metadata_base
            }
            self.chunks.append({"text": chunk, "metadata": metadata})
            self.chunk_embeddings.append(embedding)
        self.index.add(np.array(embeddings).astype("float32"))

    def search(self, query, k=5):
        if not self.chunks:
            raise ValueError("Vector store is empty. Upload a PDF first.")
        query_vec = self.model.encode([query])
        D, I = self.index.search(np.array(query_vec).astype("float32"), k)

        results = []
        for i in I[0]:
            if i < len(self.chunks):
                results.append(self.chunks[i])
        return results

    def hybrid_search(self, query, k=5):
        # First filter chunks with simple keyword matching
        keyword_filtered = [c for c in self.chunks if query.lower() in c["text"].lower()]

        if len(keyword_filtered) >= k:
            return keyword_filtered[:k]

        # Fallback to vector search
        return self.search(query, k=k)