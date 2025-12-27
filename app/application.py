# from flask import Flask,render_template,request,session,redirect,url_for
# from app.components.retriever import create_qa_chain
# from dotenv import load_dotenv
# import os


# load_dotenv()
# HF_TOKEN = os.environ.get("HF_TOKEN")

# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# load_dotenv()

# from markupsafe import Markup
# def nl2br(value):
#     return Markup(value.replace("\n" , "<br>\n"))

# app.jinja_env.filters['nl2br'] = nl2br

# @app.route("/" , methods=["GET","POST"])
# def index():
#     if "messages" not in session:
#         session["messages"]=[]

#     if request.method=="POST":
#         user_input = request.form.get("prompt")

#         if user_input:
#             messages = session["messages"]
#             messages.append({"role" : "user" , "content":user_input})
#             session["messages"] = messages

#             try:
#                 qa_chain = create_qa_chain()
#                 if qa_chain is None:
#                     raise Exception("QA chain could not be created (LLM or VectorStore issue)")
#                 response = qa_chain.invoke({"query" : user_input})
#                 result = response.get("result" , "No response")

#                 messages.append({"role" : "assistant" , "content" : result})
#                 session["messages"] = messages

#             except Exception as e:
#                 error_msg = f"Error : {str(e)}"
#                 return render_template("index.html" , messages = session["messages"] , error = error_msg)
            
#         return redirect(url_for("index"))
#     return render_template("index.html" , messages=session.get("messages" , []))

# @app.route("/clear")
# def clear():
#     session.pop("messages" , None)
#     return redirect(url_for("index"))

# if __name__=="__main__":
#     app.run(host="0.0.0.0" , port=5000 , debug=False , use_reloader = False)


# from flask import Flask,render_template,request,session,redirect,url_for
# from app.components.retriever import create_qa_chain
# from dotenv import load_dotenv
# import os
# import logging

# load_dotenv()
# HF_TOKEN = os.environ.get("HF_TOKEN")

# app = Flask(__name__)
# app.secret_key = os.urandom(24)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# from markupsafe import Markup
# def nl2br(value):
#     return Markup(value.replace("\n" , "<br>\n"))

# app.jinja_env.filters['nl2br'] = nl2br

# @app.route("/health")
# def health():
#     """Health check endpoint"""
#     import os
#     from app.config.config import DB_FAISS_PATH
    
#     health_status = {
#         "status": "ok",
#         "checks": {
#             "hf_token": "set" if os.getenv("HF_TOKEN") else "missing",
#             "hf_token_length": len(os.getenv("HF_TOKEN", "")),
#             "vectorstore_path": DB_FAISS_PATH,
#             "vectorstore_exists": os.path.exists(DB_FAISS_PATH),
#             "data_folder_exists": os.path.exists("data/"),
#         }
#     }
    
#     if os.path.exists(DB_FAISS_PATH):
#         try:
#             health_status["checks"]["vectorstore_files"] = os.listdir(DB_FAISS_PATH)
#         except Exception as e:
#             health_status["checks"]["vectorstore_error"] = str(e)
    
#     return health_status

# @app.route("/test-components")
# def test_components():
#     """Test each component"""
#     results = {}
    
#     try:
#         from app.components.vector_store import load_vector_store
#         db = load_vector_store()
#         results['vector_store'] = 'LOADED' if db else 'FAILED'
#     except Exception as e:
#         results['vector_store'] = f'ERROR: {str(e)}'
    
#     try:
#         from app.components.llm import load_llm
#         llm = load_llm()
#         results['llm'] = 'LOADED' if llm else 'FAILED'
#     except Exception as e:
#         results['llm'] = f'ERROR: {str(e)}'
    
#     try:
#         qa_chain = create_qa_chain()
#         results['qa_chain'] = 'LOADED' if qa_chain else 'FAILED'
#     except Exception as e:
#         results['qa_chain'] = f'ERROR: {str(e)}'
    
#     return results

# @app.route("/" , methods=["GET","POST"])
# def index():
#     if "messages" not in session:
#         session["messages"]=[]

#     if request.method=="POST":
#         user_input = request.form.get("prompt")

#         if user_input:
#             messages = session["messages"]
#             messages.append({"role" : "user" , "content":user_input})
#             session["messages"] = messages

#             try:
#                 qa_chain = create_qa_chain()
#                 if qa_chain is None:
#                     raise Exception("QA chain could not be created (LLM or VectorStore issue)")
#                 response = qa_chain({"query" : user_input})
#                 result = response.get("result" , "No response")

#                 messages.append({"role" : "assistant" , "content" : result})
#                 session["messages"] = messages

#             except Exception as e:
#                 logger.error(f"Error: {e}", exc_info=True)
#                 error_msg = f"Error : {str(e)}"
#                 return render_template("index.html" , messages = session["messages"] , error = error_msg)
            
#         return redirect(url_for("index"))
#     return render_template("index.html" , messages=session.get("messages" , []))

# @app.route("/clear")
# def clear():
#     session.pop("messages" , None)
#     return redirect(url_for("index"))

# if __name__=="__main__":
#     app.run(host="0.0.0.0" , port=5000 , debug=False , use_reloader = False)

from flask import Flask, render_template, request, session, redirect, url_for
from app.components.retriever import create_qa_chain
from dotenv import load_dotenv
import os
import logging

load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from markupsafe import Markup
def nl2br(value):
    return Markup(value.replace("\n", "<br>\n"))

app.jinja_env.filters['nl2br'] = nl2br

# Initialize vector store on startup
@app.before_request
def ensure_vectorstore():
    """Ensure vector store is loaded or recreate it"""
    if not hasattr(app, 'vectorstore_checked'):
        logger.info("Checking vector store...")
        try:
            from app.components.vector_store import load_vector_store
            from app.config.config import DB_FAISS_PATH
            
            db = load_vector_store()
            
            if db is None:
                logger.warning("Vector store failed to load, recreating...")
                # Delete old corrupted vector store
                import shutil
                if os.path.exists(DB_FAISS_PATH):
                    shutil.rmtree(DB_FAISS_PATH)
                
                # Recreate vector store
                from app.components.data_loader import process_and_store_pdfs
                process_and_store_pdfs()
                logger.info("Vector store recreated successfully")
            else:
                logger.info("Vector store loaded successfully")
                
        except Exception as e:
            logger.error(f"Error with vector store: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        app.vectorstore_checked = True

@app.route("/health")
def health():
    """Health check endpoint"""
    from app.config.config import DB_FAISS_PATH
    
    health_status = {
        "status": "ok",
        "checks": {
            "hf_token": "set" if os.getenv("HF_TOKEN") else "missing",
            "hf_token_length": len(os.getenv("HF_TOKEN", "")),
            "vectorstore_path": DB_FAISS_PATH,
            "vectorstore_exists": os.path.exists(DB_FAISS_PATH),
            "data_folder_exists": os.path.exists("data/"),
        }
    }
    
    if os.path.exists(DB_FAISS_PATH):
        try:
            health_status["checks"]["vectorstore_files"] = os.listdir(DB_FAISS_PATH)
        except Exception as e:
            health_status["checks"]["vectorstore_error"] = str(e)
    
    return health_status

@app.route("/test-components")
def test_components():
    """Test each component with detailed error info"""
    results = {}
    
    # Test Vector Store
    try:
        logger.info("Testing vector store...")
        from app.components.vector_store import load_vector_store
        db = load_vector_store()
        if db:
            results['vector_store'] = 'LOADED'
            # Try to get some info about the vector store
            try:
                results['vector_store_details'] = {
                    'index_size': db.index.ntotal if hasattr(db, 'index') else 'unknown'
                }
            except:
                pass
        else:
            results['vector_store'] = 'FAILED - returned None'
    except Exception as e:
        results['vector_store'] = f'ERROR: {str(e)}'
        import traceback
        results['vector_store_traceback'] = traceback.format_exc()
    
    # Test LLM
    try:
        logger.info("Testing LLM...")
        from app.components.llm import load_llm
        llm = load_llm()
        results['llm'] = 'LOADED' if llm else 'FAILED - returned None'
    except Exception as e:
        results['llm'] = f'ERROR: {str(e)}'
        import traceback
        results['llm_traceback'] = traceback.format_exc()
    
    # Test QA Chain
    try:
        logger.info("Testing QA chain...")
        qa_chain = create_qa_chain()
        results['qa_chain'] = 'LOADED' if qa_chain else 'FAILED - returned None'
    except Exception as e:
        results['qa_chain'] = f'ERROR: {str(e)}'
        import traceback
        results['qa_chain_traceback'] = traceback.format_exc()
    
    return results

@app.route("/recreate-vectorstore")
def recreate_vectorstore():
    """Manually trigger vector store recreation"""
    try:
        logger.info("Manual vector store recreation triggered")
        from app.config.config import DB_FAISS_PATH
        import shutil
        
        # Delete old vector store
        if os.path.exists(DB_FAISS_PATH):
            shutil.rmtree(DB_FAISS_PATH)
            logger.info("Deleted old vector store")
        
        # Recreate
        from app.components.data_loader import process_and_store_pdfs
        process_and_store_pdfs()
        
        return {"status": "success", "message": "Vector store recreated"}
    except Exception as e:
        logger.error(f"Error recreating vector store: {e}")
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}

@app.route("/debug-vectorstore")
def debug_vectorstore():
    """Detailed vector store debugging"""
    import sys
    from io import StringIO
    
    # Capture all logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    
    # Add handler temporarily
    logger.addHandler(handler)
    
    result = {
        "steps": [],
        "final_status": None,
        "error": None
    }
    
    try:
        result["steps"].append("Starting vector store load test...")
        
        from app.components.embeddings import get_embedding_model
        from app.config.config import DB_FAISS_PATH
        import os
        
        result["steps"].append(f"DB_FAISS_PATH: {DB_FAISS_PATH}")
        result["steps"].append(f"Path exists: {os.path.exists(DB_FAISS_PATH)}")
        
        if os.path.exists(DB_FAISS_PATH):
            files = os.listdir(DB_FAISS_PATH)
            result["steps"].append(f"Files in path: {files}")
        
        result["steps"].append("Getting embedding model...")
        embedding_model = get_embedding_model()
        result["steps"].append("Embedding model loaded")
        
        result["steps"].append("Attempting FAISS.load_local...")
        try:
            from langchain_community.vectorstores import FAISS
            vector_store = FAISS.load_local(
                DB_FAISS_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            result["steps"].append("SUCCESS: Direct load worked!")
            result["final_status"] = "SUCCESS"
            return result
        except Exception as e:
            result["steps"].append(f"Direct load failed: {type(e).__name__}: {str(e)}")
            result["error"] = str(e)
            
            # Try manual load
            result["steps"].append("Attempting manual reconstruction...")
            try:
                import pickle
                import faiss as faiss_lib
                
                index_path = os.path.join(DB_FAISS_PATH, "index.faiss")
                pkl_path = os.path.join(DB_FAISS_PATH, "index.pkl")
                
                result["steps"].append(f"index.faiss exists: {os.path.exists(index_path)}")
                result["steps"].append(f"index.pkl exists: {os.path.exists(pkl_path)}")
                
                result["steps"].append("Loading FAISS index...")
                index = faiss_lib.read_index(index_path)
                result["steps"].append(f"FAISS index loaded - ntotal: {index.ntotal}")
                
                result["steps"].append("Loading pickle...")
                with open(pkl_path, "rb") as f:
                    data = pickle.load(f)
                
                result["steps"].append(f"Pickle loaded - type: {type(data).__name__}")
                
                if isinstance(data, tuple):
                    result["steps"].append(f"Tuple length: {len(data)}")
                    
                    if len(data) >= 2:
                        docstore, index_to_docstore_id = data[0], data[1]
                        result["steps"].append(f"Docstore type: {type(docstore).__name__}")
                        result["steps"].append(f"Index mapping type: {type(index_to_docstore_id).__name__}")
                        
                        result["steps"].append("Creating FAISS object...")
                        vector_store = FAISS(
                            embedding_function=embedding_model.embed_query,
                            index=index,
                            docstore=docstore,
                            index_to_docstore_id=index_to_docstore_id,
                        )
                        result["steps"].append("SUCCESS: Manual reconstruction worked!")
                        result["final_status"] = "SUCCESS"
                        return result
                    
            except Exception as e2:
                result["steps"].append(f"Manual load failed: {type(e2).__name__}: {str(e2)}")
                import traceback
                result["error_traceback"] = traceback.format_exc()
        
        result["final_status"] = "FAILED"
        
    except Exception as e:
        result["error"] = str(e)
        result["final_status"] = "ERROR"
        import traceback
        result["error_traceback"] = traceback.format_exc()
    finally:
        # Remove handler
        logger.removeHandler(handler)
        result["logs"] = log_capture.getvalue()
    
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    if "messages" not in session:
        session["messages"] = []

    if request.method == "POST":
        user_input = request.form.get("prompt")

        if user_input:
            messages = session["messages"]
            messages.append({"role": "user", "content": user_input})
            session["messages"] = messages

            try:
                qa_chain = create_qa_chain()
                if qa_chain is None:
                    raise Exception("QA chain could not be created (LLM or VectorStore issue)")
                response = qa_chain({"query": user_input})
                result = response.get("result", "No response")

                messages.append({"role": "assistant", "content": result})
                session["messages"] = messages

            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                error_msg = f"Error : {str(e)}"
                return render_template("index.html", messages=session["messages"], error=error_msg)

        return redirect(url_for("index"))
    return render_template("index.html", messages=session.get("messages", []))

@app.route("/clear")
def clear():
    session.pop("messages", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)