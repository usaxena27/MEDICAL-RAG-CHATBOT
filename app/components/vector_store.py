from langchain_community.vectorstores import FAISS
import os
from app.components.embeddings import get_embedding_model

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import DB_FAISS_PATH

logger = get_logger(__name__)

def load_vector_store():
    try:
        embedding_model = get_embedding_model()

        if os.path.exists(DB_FAISS_PATH):
            logger.info("Loading existing vectorstore...")
            vector_store = FAISS.load_local(
                DB_FAISS_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info("Vectorstore loaded successfully")
            return vector_store
        else:
            logger.warning("No vector store found..")
            return None  # ADDED THIS

    except Exception as e:
        error_message = CustomException("Failed to load vectorstore", e)
        logger.error(str(error_message))
        return None  # ADDED THIS

# Creating new vectorstore function
def save_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise CustomException("No chunks were found..")
        
        logger.info("Generating your new vectorstore")

        embedding_model = get_embedding_model()
        db = FAISS.from_documents(text_chunks, embedding_model)

        logger.info("Saving vectorstore")
        db.save_local(DB_FAISS_PATH)
        logger.info("Vectorstore saved successfully...")

        return db
    
    except Exception as e:
        error_message = CustomException("Failed to create new vectorstore", e)
        logger.error(str(error_message))
        return None 
    
# from langchain_community.vectorstores import FAISS
# import os
# import faiss as faiss_lib
# from app.components.embeddings import get_embedding_model

# from app.common.logger import get_logger
# from app.common.custom_exception import CustomException

# from app.config.config import DB_FAISS_PATH

# logger = get_logger(__name__)

# def load_vector_store():
#     """Load vector store with fallback for Pydantic compatibility issues"""
#     try:
#         logger.info("Step 1: Getting embedding model...")
#         embedding_model = get_embedding_model()
#         logger.info("Step 1: Embedding model loaded successfully")

#         if not os.path.exists(DB_FAISS_PATH):
#             logger.warning(f"No existing vectorstore found at {DB_FAISS_PATH}")
#             return None

#         logger.info(f"Step 2: Loading vectorstore from {DB_FAISS_PATH}")
        
#         # Check files exist
#         index_path = os.path.join(DB_FAISS_PATH, "index.faiss")
#         pkl_path = os.path.join(DB_FAISS_PATH, "index.pkl")
        
#         logger.info(f"Checking files - index.faiss exists: {os.path.exists(index_path)}")
#         logger.info(f"Checking files - index.pkl exists: {os.path.exists(pkl_path)}")
        
#         # Try direct loading first
#         try:
#             logger.info("Step 3: Attempting direct FAISS load...")
#             vector_store = FAISS.load_local(
#                 DB_FAISS_PATH, 
#                 embedding_model,
#                 allow_dangerous_deserialization=True
#             )
#             logger.info("SUCCESS: Vector store loaded successfully (direct method)")
#             return vector_store
#         except (AttributeError, KeyError, TypeError) as e:
#             logger.warning(f"Direct loading failed with error: {type(e).__name__}: {str(e)}")
#             logger.info("Step 4: Trying manual reconstruction...")
        
#         # Manual reconstruction method
#         try:
#             if not os.path.exists(index_path) or not os.path.exists(pkl_path):
#                 logger.error(f"Required files not found in {DB_FAISS_PATH}")
#                 return None
            
#             # Load FAISS index
#             logger.info("Step 4a: Loading FAISS index file...")
#             import faiss as faiss_lib
#             index = faiss_lib.read_index(index_path)
#             logger.info(f"FAISS index loaded - ntotal: {index.ntotal}")
            
#             # Load pickle file
#             logger.info("Step 4b: Loading pickle file...")
#             with open(pkl_path, "rb") as f:
#                 data = pickle.load(f)
            
#             logger.info(f"Pickle loaded - type: {type(data)}, length: {len(data) if isinstance(data, tuple) else 'N/A'}")
            
#             # Handle different pickle formats
#             if isinstance(data, tuple):
#                 if len(data) == 2:
#                     docstore, index_to_docstore_id = data
#                     logger.info("Format: 2-tuple (docstore, index_to_docstore_id)")
#                 elif len(data) == 3:
#                     docstore, index_to_docstore_id, _ = data
#                     logger.info("Format: 3-tuple (with metadata)")
#                 else:
#                     logger.error(f"Unexpected tuple length: {len(data)}")
#                     return None
#             else:
#                 logger.error(f"Unexpected pickle format: {type(data)}")
#                 return None
            
#             logger.info(f"Docstore type: {type(docstore)}")
#             logger.info(f"index_to_docstore_id type: {type(index_to_docstore_id)}, length: {len(index_to_docstore_id)}")
            
#             # Reconstruct FAISS vector store
#             logger.info("Step 4c: Reconstructing FAISS vector store...")
#             from langchain_community.docstore.in_memory import InMemoryDocstore
            
#             # Convert docstore if needed
#             if not isinstance(docstore, InMemoryDocstore):
#                 logger.info("Converting docstore to InMemoryDocstore...")
#                 if hasattr(docstore, '_dict'):
#                     docstore = InMemoryDocstore(docstore._dict)
#                 else:
#                     logger.warning("Docstore has no _dict attribute, trying direct conversion")
#                     docstore = InMemoryDocstore({})
            
#             vector_store = FAISS(
#                 embedding_function=embedding_model.embed_query,
#                 index=index,
#                 docstore=docstore,
#                 index_to_docstore_id=index_to_docstore_id,
#             )
            
#             logger.info("SUCCESS: Vector store reconstructed successfully (manual method)")
#             return vector_store
            
#         except Exception as e:
#             logger.error(f"Manual reconstruction failed: {type(e).__name__}: {str(e)}")
#             import traceback
#             logger.error(traceback.format_exc())
#             return None
            
#     except Exception as e:
#         logger.error(f"Error loading vector store: {type(e).__name__}: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return None

# def save_vector_store(text_chunks):
#     """Save vector store"""
#     try:
#         if not text_chunks:
#             raise CustomException("No text chunks were found..")
        
#         logger.info("Generating your new vectorstore")

#         embedding_model = get_embedding_model()
        
#         # Create FAISS vector store
#         db = FAISS.from_documents(text_chunks, embedding_model)
        
#         logger.info("Saving Vectorstore")
        
#         # Ensure directory exists
#         os.makedirs(DB_FAISS_PATH, exist_ok=True)
        
#         # Save using the standard method
#         db.save_local(DB_FAISS_PATH)
        
#         logger.info(f"Vectorstore saved to {DB_FAISS_PATH}")
        
#         # Verify it can be loaded
#         logger.info("Verifying saved vectorstore...")
#         test_load = load_vector_store()
#         if test_load:
#             logger.info("Vectorstore verification successful")
#         else:
#             logger.warning("Vectorstore saved but verification failed")
        
#         return db
        
#     except Exception as e:
#         logger.error(f"Error creating new vectorstore: {str(e)}")
#         import traceback
#         logger.error(traceback.format_exc())
#         return None