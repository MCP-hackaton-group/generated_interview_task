from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import os
import json
import uuid
from openai import AzureOpenAI

load_dotenv()
azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "PromptAgent"

client = AzureOpenAI(
    api_key=azure_openai_key,
    api_version="2024-12-01-preview",
    azure_endpoint=azure_endpoint
)

conversations = {}
SYSTEM_PROMPT = """
You are a warm, friendly assistant helping hiring managers create job requirements for technical assignments. Your goal is to collect key information in just TWO conversation rounds:

1. Skills required for the role (must-have and nice-to-have)
2. Role description (title, seniority level, focus areas)
3. Assignment details (difficulty, time required, evaluation criteria)

CRITICAL INSTRUCTION: You will ONLY engage in 2 rounds of conversation before generating the final JSON output.

Round 1: After initial message, ask your MOST important questions (maximum 3)
Round 2: After their response, generate the FINAL JSON output with all collected information, making reasonable assumptions for anything missing

CONVERSATIONAL STYLE:
- Be warm, friendly, and conversational - not robotic
- Use a casual, encouraging tone
- Keep responses brief and focused

QUESTION GUIDELINES:
- Ask a STRICT MAXIMUM of 3 questions per response 
- Prioritize the most crucial missing information
- Be specific but gentle in your questions
- Avoid "interrogation" style questioning

EFFICIENCY GUIDELINES:
- Intelligently extract information that's already provided
- Infer reasonable defaults whenever possible
- Remember previous answers - never ask for information already given
- After 2 rounds, you MUST generate the JSON even with incomplete information

Once you have sufficient information, or after the second round of questions, format your response as a valid JSON object with this structure:
{
  "managerPrompt": {
    "version": "1.0",
    "generatedOn": "Current date"
  },
  "role": {
    "title": "Job title",
    "level": "Seniority level", 
    "focus": ["area1", "area2"],
    "description": "Detailed role description"
  },
  "requirements": {
    "skills": {
      "must_have": ["skill1", "skill2", "skill3"],
      "nice_to_have": ["skill4", "skill5"]
    }
  },
  "assignment_preferences": {
    "difficulty": "Easy/Medium/Hard",
    "estimated_hours": "X-Y",
    "areas_to_test": ["area1", "area2"]
  }
}

Only return JSON when you have sufficient information to create a reasonably complete structure. You can make reasonable assumptions to fill gaps.
"""

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/prompt", methods=["POST"])
def prompt():
    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "")
    
    if not user_msg:
        return jsonify({"error": "Missing 'message' in body"}), 400
    
    if not session_id or session_id not in conversations:
        session_id = str(uuid.uuid4())
        conversations[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        memory_prompt = """
        Information collected so far:
        - Role: Not specified
        - Level: Not specified
        - Focus areas: Not specified
        - Must-have skills: Not specified
        - Nice-to-have skills: Not specified
        - Difficulty: Not specified
        - Estimated hours: Not specified
        - Areas to test: Not specified
        - Conversation round: 0
        """
        conversations[session_id].append({"role": "system", "content": memory_prompt})
    
    conversations[session_id].append({"role": "user", "content": user_msg})
    
    try:
        update_conversation_memory(session_id, user_msg)
        
        round_number = get_conversation_round(session_id)
        
        if round_number >= 2:
            force_completion_prompt = """
            IMPORTANT: This is the second round of the conversation. You MUST now generate the final JSON output 
            with all collected information so far, making reasonable assumptions for any missing details.
            Do not ask any more questions. Format your response as a valid JSON object only with the following structure:
            
            {
              "managerPrompt": {
                "version": "1.0",
                "generatedOn": "Current date"
              },
              "role": {
                "title": "Job title", 
                "level": "Seniority level",
                "focus": ["area1", "area2"], 
                "description": "Detailed role description"
              },
              "requirements": {
                "skills": {
                  "must_have": ["skill1", "skill2"],
                  "nice_to_have": ["skill3", "skill4"]
                }
              },
              "assignment_preferences": {
                "difficulty": "Easy/Medium/Hard",
                "estimated_hours": "X-Y",
                "areas_to_test": ["area1", "area2"]
              }
            }
            """
            conversations[session_id].append({"role": "system", "content": force_completion_prompt})
        
        increment_conversation_round(session_id)
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=conversations[session_id],
            max_completion_tokens=1024,
            temperature=0.7,  
        )
        
        assistant_msg = response.choices[0].message.content
        
        conversations[session_id].append({"role": "assistant", "content": assistant_msg})
        
        is_complete = False
        if assistant_msg.strip().startswith('{'):
            try:
                json_data = json.loads(assistant_msg.strip())
                if "managerPrompt" in json_data and "role" in json_data and "requirements" in json_data and "assignment_preferences" in json_data:
                    is_complete = True
            except json.JSONDecodeError:
                pass
        
        if round_number >= 2 and not is_complete:
            final_json = generate_json_from_memory(session_id)
            conversations[session_id].append({"role": "system", "content": "Generating final JSON with available information."})
            conversations[session_id].append({"role": "assistant", "content": json.dumps(final_json, indent=2)})
            return jsonify({
                "answer": json.dumps(final_json, indent=2),
                "session_id": session_id,
                "complete": True
            }), 200
        
        return jsonify({
            "answer": assistant_msg,
            "session_id": session_id,
            "complete": is_complete,
            "round": round_number
        }), 200
        
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

def get_conversation_round(session_id):
    """Get the current conversation round number"""
    if session_id not in conversations:
        return 0
    
    for msg in conversations[session_id]:
        if msg["role"] == "system" and "Information collected so far:" in msg["content"]:
            round_line = [line for line in msg["content"].split("\n") if "Conversation round:" in line]
            if round_line:
                try:
                    return int(round_line[0].split(":")[1].strip())
                except (ValueError, IndexError):
                    return 0
    return 0

def increment_conversation_round(session_id):
    """Increment the conversation round counter"""
    if session_id not in conversations:
        return
    
    memory_index = None
    for i, msg in enumerate(conversations[session_id]):
        if msg["role"] == "system" and "Information collected so far:" in msg["content"]:
            memory_index = i
            break
    
    if memory_index is None:
        return
    
    memory_content = conversations[session_id][memory_index]["content"]
    current_round = get_conversation_round(session_id)
    new_round = current_round + 1
    
    if "Conversation round:" in memory_content:
        memory_content = memory_content.replace(
            f"Conversation round: {current_round}",
            f"Conversation round: {new_round}"
        )
        conversations[session_id][memory_index]["content"] = memory_content

def generate_json_from_memory(session_id):
    """Generate a JSON structure based on the information collected so far"""
    if session_id not in conversations:
        return {
            "managerPrompt": {
                "version": "1.0",
                "generatedOn": "2025-05-14"
            },
            "role": {
                "title": "Developer",
                "level": "Mid-level",
                "focus": ["general"],
                "description": "Software development position"
            },
            "requirements": {
                "skills": {
                    "must_have": ["programming"],
                    "nice_to_have": []
                }
            },
            "assignment_preferences": {
                "difficulty": "Medium",
                "estimated_hours": "3-4",
                "areas_to_test": ["coding"]
            }
        }
    
    memory_content = None
    for msg in conversations[session_id]:
        if msg["role"] == "system" and "Information collected so far:" in msg["content"]:
            memory_content = msg["content"]
            break
    
    if not memory_content:
        return {
            "managerPrompt": {
                "version": "1.0",
                "generatedOn": "2025-05-14"
            },
            "role": {
                "title": "Developer",
                "level": "Mid-level",
                "focus": ["general"],
                "description": "Software development position"
            },
            "requirements": {
                "skills": {
                    "must_have": ["programming"],
                    "nice_to_have": []
                }
            },
            "assignment_preferences": {
                "difficulty": "Medium",
                "estimated_hours": "3-4",
                "areas_to_test": ["coding"]
            }
        }
    
    memory_lines = memory_content.strip().split("\n")
    memory_info = {}
    
    for line in memory_lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            key = key.strip("- ")
            memory_info[key] = value
    
    role_title = memory_info.get("Role", "Not specified")
    if role_title == "Not specified":
        role_title = "Developer"  
    
    level = memory_info.get("Level", "Not specified")
    if level == "Not specified":
        level = "Mid-level"  
    
    focus_areas = memory_info.get("Focus areas", "Not specified")
    if focus_areas == "Not specified":
        focus_areas_list = ["general"]
    else:
        focus_areas_list = [area.strip() for area in focus_areas.split(",")]
    
    must_have_skills = memory_info.get("Must-have skills", "Not specified")
    if must_have_skills == "Not specified":
        must_have_list = ["programming"]
    else:
        must_have_list = [skill.strip() for skill in must_have_skills.split(",")]
    
    nice_to_have_skills = memory_info.get("Nice-to-have skills", "Not specified")
    if nice_to_have_skills == "Not specified":
        nice_to_have_list = []
    else:
        nice_to_have_list = [skill.strip() for skill in nice_to_have_skills.split(",")]
    
    difficulty = memory_info.get("Difficulty", "Not specified")
    if difficulty == "Not specified":
        difficulty = "Medium"
    
    estimated_hours = memory_info.get("Estimated hours", "Not specified")
    if estimated_hours == "Not specified":
        estimated_hours = "3-4"
    
    areas_to_test = memory_info.get("Areas to test", "Not specified")
    if areas_to_test == "Not specified":
        areas_to_test_list = ["code quality", "functionality"]
    else:
        areas_to_test_list = [area.strip() for area in areas_to_test.split(",")]
    
    description = f"We are looking for a {level} {role_title} "
    if focus_areas != "Not specified":
        description += f"with expertise in {focus_areas}. "
    else:
        description += "to join our development team. "
    
    if must_have_skills != "Not specified":
        description += f"Key skills required include {must_have_skills}. "
    
    if nice_to_have_skills != "Not specified":
        description += f"Additionally, knowledge of {nice_to_have_skills} would be beneficial."
    
    # Get current date
    from datetime import datetime
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    result_json = {
        "Here's the structured information I've gathered:"
        "managerPrompt": {
            "version": "1.0",
            "generatedOn": current_date
        },
        "role": {
            "title": role_title,
            "level": level,
            "focus": focus_areas_list,
            "description": description
        },
        "requirements": {
            "skills": {
                "must_have": must_have_list,
                "nice_to_have": nice_to_have_list
            }
        },
        "assignment_preferences": {
            "difficulty": difficulty,
            "estimated_hours": estimated_hours,
            "areas_to_test": areas_to_test_list
        }
    }
    
    return result_json

def update_conversation_memory(session_id, user_msg):
    """Update the conversation memory with new information from the user message"""
    if session_id not in conversations:
        return
    
    memory_index = None
    for i, msg in enumerate(conversations[session_id]):
        if msg["role"] == "system" and "Information collected so far:" in msg["content"]:
            memory_index = i
            break
    
    if memory_index is None:
        return
    
    memory_content = conversations[session_id][memory_index]["content"]
    
    if "title" in user_msg.lower() or "position" in user_msg.lower() or "developer" in user_msg.lower():
        role_keywords = ["developer", "engineer", "designer", "architect", "devops", "manager", "lead"]
        for keyword in role_keywords:
            if keyword in user_msg.lower():
                if "- Role: Not specified" in memory_content:
                    memory_content = memory_content.replace("- Role: Not specified", f"- Role: Likely {keyword.capitalize()}")
    
    level_keywords = {
        "junior": ["junior", "entry", "beginner", "jr"],
        "mid-level": ["mid", "intermediate", "regular"],
        "senior": ["senior", "experienced", "expert", "sr", "lead"]
    }
    
    for level, keywords in level_keywords.items():
        for keyword in keywords:
            if keyword in user_msg.lower():
                if "- Level: Not specified" in memory_content:
                    memory_content = memory_content.replace("- Level: Not specified", f"- Level: {level.capitalize()}")
    
    # Extract focus areas
    focus_areas = {
        "frontend": ["frontend", "front-end", "ui", "react", "angular", "vue", "javascript", "typescript", "web", "css", "html"],
        "backend": ["backend", "back-end", "server", "api", "database", "node", "python", "java", "php", "service"],
        "fullstack": ["fullstack", "full-stack", "full stack", "both frontend and backend"],
        "devops": ["devops", "ci/cd", "deployment", "kubernetes", "docker", "ops", "pipeline", "cloud"],
        "mobile": ["mobile", "ios", "android", "react native", "flutter", "app", "swift"],
        "data": ["data science", "machine learning", "ml", "ai", "analytics", "data engineering", "big data"],
        "security": ["security", "infosec", "cybersecurity", "penetration testing", "encryption"]
    }
    
    detected_areas = []
    for area, keywords in focus_areas.items():
        for keyword in keywords:
            if keyword in user_msg.lower() and area not in detected_areas:
                detected_areas.append(area)
    
    if detected_areas and "- Focus areas: Not specified" in memory_content:
        memory_content = memory_content.replace("- Focus areas: Not specified", f"- Focus areas: {', '.join(detected_areas)}")
    
    # Extract skills
    tech_skills = [
        "javascript", "typescript", "python", "java", "c#", "go", "rust", "php", "ruby",
        "react", "angular", "vue", "svelte", "node", "express", "django", "spring", "asp.net",
        "sql", "nosql", "mongodb", "postgres", "mysql", "oracle", "redis",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
        "rest", "graphql", "microservices", "serverless", "oauth", "jwt",
        "git", "github", "gitlab", "bitbucket", "ci/cd"
    ]
    
    detected_skills = []
    for skill in tech_skills:
        if skill in user_msg.lower() and skill not in detected_skills:
            detected_skills.append(skill)
    
    # Check for must-have vs nice-to-have context
    nice_to_have_context = ["nice to have", "preferred", "bonus", "plus", "additionally", "would be good", "beneficial", "optional"]
    must_have_context = ["must have", "required", "essential", "necessary", "need", "looking for", "should have"]
    
    nice_to_have = False
    for context in nice_to_have_context:
        if context in user_msg.lower():
            nice_to_have = True
            break
    
    must_have = False
    for context in must_have_context:
        if context in user_msg.lower():
            must_have = True
            break
    
    # If clearly specified as nice-to-have
    if nice_to_have and not must_have and detected_skills and "- Nice-to-have skills: Not specified" in memory_content:
        memory_content = memory_content.replace("- Nice-to-have skills: Not specified", f"- Nice-to-have skills: {', '.join(detected_skills)}")
    # Default to must-have if not clearly specified
    elif detected_skills and "- Must-have skills: Not specified" in memory_content:
        memory_content = memory_content.replace("- Must-have skills: Not specified", f"- Must-have skills: {', '.join(detected_skills)}")
        
    # Extract areas to test
    test_areas = {
        "code quality": ["code quality", "clean code", "readability", "maintainability", "style"],
        "functionality": ["functionality", "features", "working", "correct", "behavior"],
        "performance": ["performance", "speed", "efficiency", "optimization", "load"],
        "security": ["security", "secure coding", "vulnerabilities", "protection"],
        "architecture": ["architecture", "design", "structure", "patterns"],
        "testing": ["testing", "unit tests", "test coverage", "automated tests"],
        "documentation": ["documentation", "comments", "readme"]
    }
    
    detected_test_areas = []
    for area, keywords in test_areas.items():
        for keyword in keywords:
            if keyword in user_msg.lower() and area not in detected_test_areas:
                detected_test_areas.append(area)
    
    if detected_test_areas and "- Areas to test: Not specified" in memory_content:
        memory_content = memory_content.replace("- Areas to test: Not specified", f"- Areas to test: {', '.join(detected_test_areas)}")
    
    # Extract difficulty
    difficulty_keywords = {
        "easy": ["easy", "simple", "basic", "beginner"],
        "medium": ["medium", "moderate", "intermediate"],
        "hard": ["hard", "difficult", "complex", "challenging", "advanced"]
    }
    
    for difficulty, keywords in difficulty_keywords.items():
        for keyword in keywords:
            if keyword in user_msg.lower():
                if "- Difficulty: Not specified" in memory_content:
                    memory_content = memory_content.replace("- Difficulty: Not specified", f"- Difficulty: {difficulty.capitalize()}")
    
    # Extract estimated hours
    import re
    hours_pattern = r'(\d+)[\s-]*(?:to|-)[\s-]*(\d+)\s*(?:hour|hr)'
    single_hour_pattern = r'(\d+)\s*(?:hour|hr)'
    
    hours_match = re.search(hours_pattern, user_msg.lower())
    if hours_match:
        min_hours = hours_match.group(1)
        max_hours = hours_match.group(2)
        if "- Estimated hours: Not specified" in memory_content:
            memory_content = memory_content.replace("- Estimated hours: Not specified", f"- Estimated hours: {min_hours}-{max_hours}")
    else:
        single_match = re.search(single_hour_pattern, user_msg.lower())
        if single_match:
            hours = single_match.group(1)
            if "- Estimated hours: Not specified" in memory_content:
                memory_content = memory_content.replace("- Estimated hours: Not specified", f"- Estimated hours: {hours}")
    
    # Update the memory in the conversation
    conversations[session_id][memory_index]["content"] = memory_content
        
# Add a new endpoint to check conversation status
@app.route("/conversation/<session_id>", methods=["GET"]) 
def get_conversation(session_id):
    if session_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
        
    return jsonify({
        "session_id": session_id,
        "messages": conversations[session_id][1:] # Exclude system prompt
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
