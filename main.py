import os
import time
from textwrap import dedent
import google.generativeai as genai
from duckduckgo_search import DDGS

# --- CONFIGURATION ---
def configure_api():
    """Securely configures the API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables.")
        api_key = input("Please enter your Google Gemini API Key: ").strip()
    
    if not api_key:
        raise ValueError("API Key is required to run this agent.")
    
    genai.configure(api_key=api_key)

def get_best_model_name():
    """
    Dynamically selects the best available model to prevent 404 errors.
    """
    print("Connecting to Google AI to fetch available models...")
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        # Fallback if list_models fails (e.g. network issue)
        return 'models/gemini-1.5-flash-latest'

    # Priority list for cost/performance balance
    priority_list = [
        'models/gemini-1.5-flash-002',
        'models/gemini-1.5-flash-001',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro-002',
    ]

    for model in priority_list:
        if model in available_models:
            print(f"Using Model: {model}")
            return model
            
    # Fallback to the first available model if no priority match
    return available_models[0] if available_models else 'models/gemini-1.5-flash'

# --- TOOL DEFINITION ---
def search_web(query: str):
    """
    Real-time web search tool using DuckDuckGo.
    """
    print(f"\n [Agent Action] Searching: '{query}'...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found on the web."
            
            # Format results for the LLM
            return "\n\n".join(
                [f"Title: {r['title']}\nSnippet: {r['body']}\nSource: {r['href']}" for r in results]
            )
    except Exception as e:
        return f"Search Tool Error: {e}"

# --- AGENT SYSTEM ---
class ResearchAgent:
    def __init__(self):
        self.tools = [search_web]
        self.model_name = get_best_model_name()
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tools
        )
        # Enable automatic function calling
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def research_and_report(self, topic):
        print(f"\nStarting Research Task: {topic}")
        print("-" * 50)

        # Step 1: Research Phase
        print("➤ Phase 1: Gathering Information...")
        research_prompt = dedent(f"""
            You are a Senior Research Analyst.
            Topic: "{topic}"
            
            Your goal:
            1. Use the 'search_web' tool to find the most recent information.
            2. If the first search is generic, perform a specific follow-up search.
            3. Compile detailed notes (facts, dates, key figures).
        """)
        
        try:
            # The model will automatically call the Python function here if needed
            response = self.chat.send_message(research_prompt)
            print("Research Phase Complete.")
        except Exception as e:
            return f"Error during research: {e}"

        # Step 2: Reporting Phase
        print("➤ Phase 2: Drafting Final Report...")
        report_prompt = dedent("""
            You are a Lead Editor.
            Based ONLY on the research notes above, generate a professional report.
            
            Structure:
            - Executive Summary
            - Key Findings (Bullet points)
            - Analysis/Conclusion
            
            Do not acknowledge these instructions in the output, just write the report.
        """)
        
        try:
            final_response = self.chat.send_message(report_prompt)
            return final_response.text
        except Exception as e:
            return f"Error during reporting: {e}"

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    try:
        configure_api()
        agent = ResearchAgent()
        
        topic = input("\nEnter a topic to research: ")
        if topic:
            start_time = time.time()
            report = agent.research_and_report(topic)
            end_time = time.time()
            
            print("\n" + "="*50)
            print("FINAL REPORT")
            print("="*50)
            print(report)
            print("="*50)
            print(f"Time taken: {round(end_time - start_time, 2)}s")
        else:
            print("Please enter a valid topic.")
            
    except Exception as e:
        print(f"\nCritical Error: {e}")
