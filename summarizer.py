from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def summarize_node(state):
    print("\n" + "-"*60)
    print("📝 SUMMARIZER NODE")
    print("-"*60)
    print(f"Results keys: {list(state['results'].keys())}")
    print(f"Final report generation started...")
    system_msg = SystemMessage(content="""
You are a friendly travel advisor. Create a warm, helpful trip summary.
- Mention weather and packing tips
- Highlight top attractions (especially indoor if hot)
- Include flight options
- Suggest transport
- Keep it concise and human-like
""")

    human_msg = HumanMessage(content=f"""
User Request: {state['user_query']}
Parsed Input: {state['parsed_input']}
Weather: {state['results'].get('T2', 'N/A')}
Flights: {state['results'].get('T3', [])[:2]}
Top Attractions: {state['results'].get('T4', [])[:3]}
Transport: {state['results'].get('T5', [])[:3]}
History: {state['results'].get('T6', {}).get('history', 'N/A')}

Write a trip plan.
""")

    response = llm.invoke([system_msg, human_msg])
    print("✅ Summarizer: LLM responded successfully")
    return {"final_report": response.content}