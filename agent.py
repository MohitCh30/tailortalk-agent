from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from drive_tool import search_drive_files, get_drive_service
import os
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv('GROQ_API_KEY'),
    temperature=0
)

chat_history = []

SYSTEM_PROMPT = """You are a Google Drive file assistant. 
When user asks to find files, respond with ONLY a Drive API query string, nothing else.
Examples:
- User: find PDFs -> mimeType = 'application/pdf'
- User: find files named report -> name contains 'report'
- User: find images -> mimeType contains 'image'
- User: find invoice documents -> fullText contains 'invoice'
Just output the raw query string, no explanation."""

def chat(message: str) -> str:
    global chat_history
    
    # Step 1: LLM generates Drive query
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + chat_history + [HumanMessage(content=message)]
    query_response = llm.invoke(messages)
    drive_query = query_response.content.strip()
    
    print(f"Drive query: {drive_query}")
    
    # Step 2: Execute Drive search
    search_result = search_drive_files.invoke(drive_query)
    
    print(f"Search result: {search_result}")
    
    # Step 3: LLM formats response
    format_messages = [
        SystemMessage(content="You are a helpful file assistant. Present the search results clearly and conversationally."),
        HumanMessage(content=f"User asked: {message}\n\nSearch results: {search_result}\n\nPresent these results helpfully.")
    ]
    final_response = llm.invoke(format_messages)
    
    chat_history.append(HumanMessage(content=message))
    chat_history.append(AIMessage(content=final_response.content))
    
    return final_response.content