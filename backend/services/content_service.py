from agents.planner_agent import create_content_plan

def generate_content_package(topic: str) -> dict:
    """
    Coordinates the Planner Agent and aggregates the results from the sub-agents into the final JSON response.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")
        
    print(f"Content Service: Initiating package generation for topic: '{topic}'")
    # Execute the planner agent plan flow
    result = create_content_plan(topic)
    
    return result
