import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
# UPDATED IMPORTS: Migrated to langchain-classic
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from app.rag.index import build_index

def reasoning_node(state):
    # 1. Validation: Check for API Key
    if not os.environ.get("OPENAI_API_KEY"):
        return {
            "hypotheses": ["Error: OPENAI_API_KEY not set. Cannot generate reasoning."]
        }

    try:
        # 2. Initialize LLM and Vector Store
        llm = ChatOpenAI(temperature=0, model="gpt-4o")
        vectorstore = build_index()

        # 3. Create the Chain
        prompt = ChatPromptTemplate.from_template("""Answer the question based on the following context:

<context>
{context}
</context>

Question: {input}
""")
        # Using the classic chain constructors
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectorstore.as_retriever()
        qa_chain = create_retrieval_chain(retriever, document_chain)

        # 4. Formulate the Query
        anomaly = state.get("anomaly", {})
        query = f"""
        An anomaly was detected for issuer {anomaly.get('issuer', 'Unknown')} 
        with severity {anomaly.get('severity', 0)}.
        Features: {anomaly.get('features', {})}

        Identify likely root causes based on the provided runbooks.
        """

        # 5. Invoke Chain
        response = qa_chain.invoke({"input": query})
        result_text = response["answer"]

    except Exception as e:
        result_text = f"Reasoning Engine Error: {str(e)}"

    return {
        "hypotheses": [result_text]
    }