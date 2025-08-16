from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json
from agents_metadata import AGENT_LIST

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

planner_prompt = PromptTemplate.from_template(
    """
You are a travel planning coordinator. Create a detailed plan to fulfill the user's request.

User Request: {user_query}

Available Agents:
{% for agent in agent_list %}
- {{ agent['name'] }}: {{ agent['description'] }}
{% endfor %}

Instructions:
1. Break the goal into Tasks. For each Task:
   - id: T1, T2, etc.
   - goal: Clear instruction (e.g., "Check weather in Dubai")
   - agent: Which agent to use
   - prerequisites: List of task IDs that must finish first
2. Group Tasks into Steps (parallelizable).
3. Output ONLY JSON:
{{
  "steps": [
    {{
      "id": 1,
      "tasks": [
        {{
          "id": "T1",
          "goal": "Parse input",
          "agent": "ParserAgent",
          "prerequisites": []
        }},
        {{
          "id": "T2",
          "goal": "Check weather",
          "agent": "WeatherAgent",
          "prerequisites": []
        }}
      ]
    }}
  ]
}}

If impossible, return: {{"error": "reason"}}
"""
)

# We'll manually render the Jinja-like template
def create_plan_prompt(user_query: str) -> str:
    agent_block = "\n".join([
        f"- {a['name']}: {a['description']}" for a in AGENT_LIST
    ])
    return planner_prompt.template.replace(
        "{% for agent in agent_list %}\n- {{ agent['name'] }}: {{ agent['description'] }}\n{% endfor %}",
        agent_block
    ).replace("{user_query}", user_query)

chain = llm

# def plan_step(state):
#     prompt = create_plan_prompt(state["user_query"])
#     try:
#         response = chain.invoke(prompt)
#         content = response.content.strip()
#         if content.startswith("```json"):
#             content = content[7:content.rfind("```")]
#         plan = json.loads(content)
#         return {
#             "plan": plan,
#             "step_index": 0,
#             "current_step": plan["steps"][0] if "steps" in plan else None,
#             "should_continue": "continue" if "error" not in plan else "end"
#         }
#     except Exception as e:
#         return {
#             "plan": {"error": str(e)},
#             "should_continue": "end"
#         }
def plan_step(state):
    print("\n" + "-"*60)
    print("🧠 PLANNER NODE")
    print("-"*60)
    print(f"Input user_query: {state['user_query']}")

    try:
        response = chain.invoke(create_plan_prompt(state["user_query"]))
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:content.rfind("```")]
        
        print(f"LLM Raw Output:\n{content}\n")

        plan = json.loads(content)

        if not plan.get("steps"):
            print("❌ Planner: No steps generated in plan")
            return {
                "plan": {"error": "No steps"},
                "should_continue": "end"
            }

        print(f"✅ Planner: Generated {len(plan['steps'])} steps")
        for i, step in enumerate(plan["steps"]):
            print(f"  Step {i+1}: {len(step['tasks'])} tasks")

        return {
            "plan": plan,
            "step_index": 0,
            "current_step": plan["steps"][0],
            "should_continue": "continue"
        }

    except Exception as e:
        print(f"❌ Planner Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "plan": {"error": str(e)},
            "should_continue": "end"
        }