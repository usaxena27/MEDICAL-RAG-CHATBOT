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


from flask import Flask,render_template,request,session,redirect,url_for
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
    return Markup(value.replace("\n" , "<br>\n"))

app.jinja_env.filters['nl2br'] = nl2br

@app.route("/health")
def health():
    """Health check endpoint"""
    import os
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
    """Test each component"""
    results = {}
    
    try:
        from app.components.vector_store import load_vector_store
        db = load_vector_store()
        results['vector_store'] = 'LOADED' if db else 'FAILED'
    except Exception as e:
        results['vector_store'] = f'ERROR: {str(e)}'
    
    try:
        from app.components.llm import load_llm
        llm = load_llm()
        results['llm'] = 'LOADED' if llm else 'FAILED'
    except Exception as e:
        results['llm'] = f'ERROR: {str(e)}'
    
    try:
        qa_chain = create_qa_chain()
        results['qa_chain'] = 'LOADED' if qa_chain else 'FAILED'
    except Exception as e:
        results['qa_chain'] = f'ERROR: {str(e)}'
    
    return results

@app.route("/" , methods=["GET","POST"])
def index():
    if "messages" not in session:
        session["messages"]=[]

    if request.method=="POST":
        user_input = request.form.get("prompt")

        if user_input:
            messages = session["messages"]
            messages.append({"role" : "user" , "content":user_input})
            session["messages"] = messages

            try:
                qa_chain = create_qa_chain()
                if qa_chain is None:
                    raise Exception("QA chain could not be created (LLM or VectorStore issue)")
                response = qa_chain({"query" : user_input})
                result = response.get("result" , "No response")

                messages.append({"role" : "assistant" , "content" : result})
                session["messages"] = messages

            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                error_msg = f"Error : {str(e)}"
                return render_template("index.html" , messages = session["messages"] , error = error_msg)
            
        return redirect(url_for("index"))
    return render_template("index.html" , messages=session.get("messages" , []))

@app.route("/clear")
def clear():
    session.pop("messages" , None)
    return redirect(url_for("index"))

if __name__=="__main__":
    app.run(host="0.0.0.0" , port=5000 , debug=False , use_reloader = False)