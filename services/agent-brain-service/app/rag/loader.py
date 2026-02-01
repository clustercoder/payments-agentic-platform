import os
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_docs():
    # 1. Get the directory of THIS file (app/rag/loader.py)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Calculate the Service Root (services/agent-brain-service)
    # Go up two levels: app/rag -> app -> agent-brain-service
    service_root = os.path.dirname(os.path.dirname(current_file_dir))
    
    # 3. Construct path to runbooks
    data_path = os.path.join(service_root, "ml", "datasets", "runbooks")

    print(f"DEBUG: Calculated runbooks path: {data_path}")

    # 4. Validation
    if not os.path.exists(data_path):
        print(f"WARNING: Path not found at {data_path}")
        # Try a fallback relative to where the command was run (CWD)
        cwd_path = os.path.join(os.getcwd(), "ml", "datasets", "runbooks")
        if os.path.exists(cwd_path):
             print(f"DEBUG: Found runbooks in CWD: {cwd_path}")
             data_path = cwd_path
        else:
             print("ERROR: Could not find runbooks directory.")
             return []

    # 5. Load
    try:
        loader = DirectoryLoader(data_path, glob="**/*.md")
        docs = loader.load()
        print(f"DEBUG: Loaded {len(docs)} documents.")
    except Exception as e:
        print(f"ERROR: Failed to load docs: {e}")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)