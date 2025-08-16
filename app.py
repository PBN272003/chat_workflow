from graph_builder import app
from langchain_core.messages import HumanMessage
import traceback
# if __name__ == "__main__":
#     query = input("✈️ Plan your trip: \n"
#                  "e.g., 'Plan a 5-day trip to Dubai from 04-10-2025 to 04-15-2025'\n> ")

#     result = app.invoke({
#         "user_query": query,
#         "messages": [HumanMessage(content=query)],
#         "results": {},
#         "plan": {},
#         "should_continue": "continue"
#     })

#     print("\n" + "="*60)
#     print("✅ YOUR TRIP PLAN")
#     print("="*60)
#     print(result["final_report"])
# app.py


if __name__ == "__main__":
    # Get user input
    query = input("✈️ Plan your trip: \n> ").strip()

    # Log initial input
    print("\n" + "="*60)
    print("📥 INITIAL INPUT")
    print("="*60)
    print(f"User Query: {query}")

    # Initialize full state
    initial_state = {
        "user_query": query,
        "messages": [HumanMessage(content=query)],
        "parsed_input": None,
        "plan": {},
        "current_step": None,
        "results": {},
        "final_report": None,
        "should_continue": "continue",
        "step_index": 0  # Critical: must be initialized!
    }

    print("(Initial state prepared and sent to graph)")

    # Invoke the graph with higher recursion limit for debugging
    try:
        result = app.invoke(
            initial_state,
            config={"recursion_limit": 50}  # Prevents early cutoff
        )
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR during graph invocation: {str(e)}")
        traceback.print_exc()
        exit()

    # Final output
    print("\n" + "="*60)
    print("✅ FINAL REPORT")
    print("="*60)
    if result.get("final_report"):
        print(result["final_report"])
    else:
        print("⚠️ No final report generated. Check earlier logs.")

    print("\n" + "="*60)
    print("📊 FINAL STATE SNAPSHOT")
    print("="*60)
    for k, v in result.items():
        if k == "messages":
            print(f"{k}: [{len(v)} messages]")
        elif k == "results":
            print(f"{k}: {list(v.keys())}")
        else:
            print(f"{k}: {v}")

    print("\n🎉 Trip planning complete!\n")