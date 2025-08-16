from Agents.weather import get_weather
from Agents.flight_recommendations import search_flights
from Agents.tourism import suggest_attractions
from Agents.public_transport import get_public_transport
from Agents.location_info import get_location_history
from langchain_core.messages import AIMessage
import re

def parse_dates(text: str):
    dates = re.findall(r'\b(\d{2}[/-]\d{2}[/-]\d{4}|\d{4}-\d{2}-\d{2})\b', text)
    return dates[0] if dates else None, dates[1] if len(dates) > 1 else None

def router_node(state):
    print("\n" + "-"*60)
    print("🔄 EXECUTE_STEP NODE")
    print("-"*60)
    print(f"Current step_index: {state.get('step_index', 0)}")
    plan = state["plan"]
    if "error" in plan:
        return {"should_continue": "end"}

    steps = plan.get("steps", [])
    idx = state.get("step_index", 0)
    print(f"Total steps: {len(steps)}")
    if idx >= len(steps):
        print("✅ All steps completed. Ending.")
        return {"should_continue": "end"}

    current_step = steps[idx]
    print(f"🎯 Executing Step {idx + 1} with {len(current_step['tasks'])} task(s)")
    results = state["results"].copy()
    messages = state["messages"].copy()

    for task in current_step["tasks"]:
        task_id = task["id"]
        agent_name = task["agent"]
        print(f"  ➤ Running Task {task_id} → {agent_name}")
        prerequisites = task.get("prerequisites", [])

        # Check if all prerequisites are done
        for pre in prerequisites:
            if pre not in results:
                print(f"  ❌ Blocked: Task {task_id} needs {pre}, but it's not done")
                return {"should_continue": "end"}

        # Run agent logic
        if agent_name == "ParserAgent":
            dest_match = re.search(r"to\s+([a-zA-Z\s]+)", state["user_query"], re.I)
            destination = dest_match.group(1).strip() if dest_match else "Dubai"
            start_date, return_date = parse_dates(state["user_query"])
            parsed = {
                "destination": destination,
                "start_date": start_date,
                "return_date": return_date
            }
            results[task_id] = parsed
            results["parsed_input"] = parsed
            messages.append(AIMessage(content=f"Parsed: {parsed}"))

        elif agent_name == "WeatherAgent":
            dest = results["parsed_input"]["destination"]
            data = get_weather(dest)
            results[task_id] = data
            messages.append(AIMessage(content=f"Weather: {data}"))
            print(f"    ✅ Weather: {data.get('temperature_c', 'N/A')}°C")

        elif agent_name == "FlightAgent":
            parsed = results["parsed_input"]
            origin = "DEL"
            dest = parsed["destination"]
            start = parsed["start_date"]
            return_date = parsed["return_date"]
            data = search_flights(origin, dest, start, return_date)
            results[task_id] = data
            messages.append(AIMessage(content=f"Flights: {len(data)} options"))
            print(f"    ✅ Found {len(data)} flights")

        elif agent_name == "TourismAgent":
            dest = results["parsed_input"]["destination"]
            data = suggest_attractions(dest)
            results[task_id] = data
            messages.append(AIMessage(content=f"Attractions: {len(data)} found"))
            print(f"    ✅ Found {len(data)} attractions")

        elif agent_name == "TransportAgent":
            dest = results["parsed_input"]["destination"]
            data = get_public_transport(dest)
            results[task_id] = data
            messages.append(AIMessage(content=f"Transport: {len(data)} hubs"))
            print(f"    ✅ Found {len(data)} transport hubs")

        # elif agent_name == "HistoryAgent":
        #     # Use top attraction
        #     tourism_task = next((k for k, v in results.items() if isinstance(v, list) and len(v) > 0), None)
        #     if tourism_task:
        #         top_place = results[tourism_task][0]["name"]
        #         print(top_place)
        #         data = get_location_history(top_place)
        #         results[task_id] = {"place": top_place, "history": data}
        #         messages.append(AIMessage(content=f"History: {top_place}"))
        #         print(f"    ✅ Found history for {top_place}")
        elif agent_name == "HistoryAgent":
                print("    → Fetching history for top attraction...")
                tourism_task = None
                for k, v in results.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict) and "name" in v[0]:
                        tourism_task = k
                        break

                if not tourism_task:
                    print("    ❌ No valid attractions found — skipping history")
                    results[task_id] = {"error": "No attractions", "history": "N/A"}
                else:
                    top_place = results[tourism_task][0]["name"]
                    print(f"    🎯 Using: {top_place}")
                    history = get_location_history(top_place)
                    results[task_id] = {"place": top_place, "history": history}

    messages.append(AIMessage(content=f"Completed Step {idx + 1}"))
    print(f"✅ Step {idx + 1} completed. Advancing to next step.")
    return {
        "results": results,
        "messages": messages,
        "step_index": idx + 1,
        "current_step": current_step,
        "should_continue": "end" if (idx + 1) >= len(steps) else "continue"
    }