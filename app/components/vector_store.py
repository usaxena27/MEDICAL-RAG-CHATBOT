# from langchain_community.vectorstores import FAISS
# import os
# from app.components.embeddings import get_embedding_model

# from app.common.logger import get_logger
# from app.common.custom_exception import CustomException

# from app.config.config import DB_FAISS_PATH

# logger = get_logger(__name__)

# def load_vector_store():
#     try:
#         embedding_model = get_embedding_model()

#         if os.path.exists(DB_FAISS_PATH):
#             logger.info("Loading existing vectorstore...")
#             return FAISS.load_local(
#                 DB_FAISS_PATH,
#                 embedding_model,
#                 allow_dangerous_deserialization=True
#             )
#         else:
#             logger.warning("No vectore store found..")

#     except Exception as e:
#         error_message = CustomException("Failed to load vectorstore" , e)
#         logger.error(str(error_message))

# # Creating new vectorstore function
# def save_vector_store(text_chunks):
#     try:
#         if not text_chunks:
#             raise CustomException("No chunks were found..")
        
#         logger.info("Generating your new vectorstore")

#         embedding_model = get_embedding_model()

#         db = FAISS.from_documents(text_chunks,embedding_model)

#         logger.info("Saving vectorstoree")

#         db.save_local(DB_FAISS_PATH)

#         logger.info("Vectostore saved sucesfulyy...")

#         return db
    
#     except Exception as e:
#         error_message = CustomException("Failed to craete new vectorstore " , e)
#         logger.error(str(error_message))
    
from langchain_community.vectorstores import FAISS
import os
import pickle
import faiss as faiss_lib
from app.components.embeddings import get_embedding_model

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

from app.config.config import DB_FAISS_PATH

logger = get_logger(__name__)

def load_vector_store():
    """Load vector store with fallback for Pydantic compatibility issues"""
    try:
        embedding_model = get_embedding_model()

        if not os.path.exists(DB_FAISS_PATH):
            logger.warning(f"No existing vectorstore found at {DB_FAISS_PATH}")
            return None

        logger.info(f"Loading existing vectorstore from {DB_FAISS_PATH}")
        
        # Try direct loading first
        try:
            vector_store = FAISS.load_local(
                DB_FAISS_PATH, 
                embedding_model,
                allow_dangerous_deserialization=True
            )
            logger.info("Vector store loaded successfully (direct method)")
            return vector_store
        except (AttributeError, KeyError, TypeError) as e:
            logger.warning(f"Direct loading failed: {str(e)}, trying manual reconstruction...")
        
        # Manual reconstruction method for Pydantic issues
        try:
            index_path = os.path.join(DB_FAISS_PATH, "index.faiss")
            pkl_path = os.path.join(DB_FAISS_PATH, "index.pkl")
            
            if not os.path.exists(index_path) or not os.path.exists(pkl_path):
                logger.error(f"Required files not found in {DB_FAISS_PATH}")
                return None
            
            # Load FAISS index
            index = faiss_lib.read_index(index_path)
            logger.info("FAISS index file loaded")
            
            # Load pickle file with custom unpickler
            with open(pkl_path, "rb") as f:
                try:
                    # Try to load with protocol 5 (newest)
                    data = pickle.load(f)
                except Exception:
                    # Fallback: try with older protocol
                    f.seek(0)
                    import pickle5
                    data = pickle5.load(f)
            
            logger.info("Pickle file loaded")
            
            # Handle different pickle formats
            if isinstance(data, tuple):
                if len(data) == 2:
                    docstore, index_to_docstore_id = data
                elif len(data) == 3:
                    # Some versions include metadata
                    docstore, index_to_docstore_id, _ = data
                else:
                    logger.error(f"Unexpected tuple length: {len(data)}")
                    return None
            else:
                logger.error(f"Unexpected pickle format: {type(data)}")
                return None
            
            # Reconstruct FAISS vector store manually
            from langchain_community.docstore.in_memory import InMemoryDocstore
            
            # Convert docstore to InMemoryDocstore if needed
            if not isinstance(docstore, InMemoryDocstore):
                docstore = InMemoryDocstore(docstore._dict if hasattr(docstore, '_dict') else {})
            
            vector_store = FAISS(
                embedding_function=embedding_model.embed_query,
                index=index,
                docstore=docstore,
                index_to_docstore_id=index_to_docstore_id,
            )
            
            logger.info("Vector store reconstructed successfully (manual method)")
            return vector_store
            
        except Exception as e:
            logger.error(f"Manual reconstruction failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def save_vector_store(text_chunks):
    """Save vector store"""
    try:
        if not text_chunks:
            raise CustomException("No text chunks were found..")
        
        logger.info("Generating your new vectorstore")

        embedding_model = get_embedding_model()
        
        # Create FAISS vector store
        db = FAISS.from_documents(text_chunks, embedding_model)
        
        logger.info("Saving Vectorstore")
        
        # Ensure directory exists
        os.makedirs(DB_FAISS_PATH, exist_ok=True)
        
        # Save using the standard method
        db.save_local(DB_FAISS_PATH)
        
        logger.info(f"Vectorstore saved to {DB_FAISS_PATH}")
        
        # Verify it can be loaded
        logger.info("Verifying saved vectorstore...")
        test_load = load_vector_store()
        if test_load:
            logger.info("Vectorstore verification successful")
        else:
            logger.warning("Vectorstore saved but verification failed")
        
        return db
        
    except Exception as e:
        logger.error(f"Error creating new vectorstore: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None