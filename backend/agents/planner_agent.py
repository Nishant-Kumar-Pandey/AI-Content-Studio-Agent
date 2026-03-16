from agents.script_agent import generate_script
from agents.thumbnail_agent import generate_thumbnail
from agents.caption_agent import generate_caption
from agents.hashtag_agent import generate_hashtags

def create_content_plan(topic: str) -> dict:
    """
    Planner Agent: Orchestrates the execution of specialized agents to generate a complete content package.
    """
    print(f"🧠 Planner Agent: Analyzing topic '{topic}' and orchestrating sub-agents...")
    
    # In a more advanced ADK setup, this agent would use an LLM to dynamically generate 
    # the execution plan. Here we follow the predefined workflow.
    
    script = generate_script(topic)
    thumbnail = generate_thumbnail(topic)
    caption = generate_caption(topic)
    hashtags = generate_hashtags(topic)
    
    print("✅ Planner Agent: Content package generation complete.")
    
    return {
        "script": script,
        "thumbnail": thumbnail,
        "caption": caption,
        "hashtags": hashtags
    }
