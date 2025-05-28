import torch
import random
from pydantic import BaseModel

def prompts_for_elaborating_topic(topic):
    prompt = "Please elaborate what a person would like to talk about under the topic of " + topic + ". "
    return prompt

def prompts_for_expanding_persona(persona, start_time):
    birth_year = str(int(start_time.split('/')[2]) - 18)
    gender_identity = (' transgender ' if random.random() < 0.2 else '') + random.choice(['female', 'male', 'non-binary'])
    racial_identity = random.choice(['Asian', 'South Asian', 'African American', 'Hispanic', 'Indigenous', 'White', 'Jewish', 'Pacific Islander', 'Mixed race'])
    prompt = ("The current version of the persona is short. Keep the same style and pronouns, but expand it with additional information to around five sentences. "
              "Add a name, a gender identity of " + gender_identity + ", and a racial identity of " + racial_identity + ", if any of them is missing from the initial version."
              "Adjust the persona if necessary given the person is born in " + birth_year + ". Here is the persona: " + persona)
    return prompt

def prompts_for_generating_conversations_with_persona_and_topic(topic, persona):
    prompt = f"""
Your task is to generate a synthetic conversation record about the topic: "{topic}".

The conversation must adhere to the following strict requirements:

1. **Participants:** The conversation is strictly multi-turn between a "user" and an "agent".

2. **User Persona:** The user's persona is: "{persona}".
    - The user's language, motivations, and behavior should reflect this persona.
    - The user should not automatically agree with everything the agent says.
    - Their utterances should reflect their personality, values, hesitations, or even frustrations.
    - Use natural phrasing, including filler words or self-corrections, to reflect how real people speak.

3. **Turn Structure & Indexing:**
    - Format the conversation as a list of Python dictionaries, like:
      {{
          "turn_id": 0,
          "speaker": "user",
          "text": "Hello!"
      }}
    - Use valid Python syntax with integers for turn_id and double quotes for strings.

4. **Conversation Length:** The conversation should include 10–20 turns total (typically 5–10 turns per speaker).

5. **Content and Detail:**
    - The conversation should be rich in relevant detail related to "{topic}".
    - The agent should be helpful and informative, trying to support the user's goals.
    - The user should remain consistent with their persona throughout, including when they express confusion, change their mind, or ask questions.

6. **Preference Change Requirements:**
    - The conversation MUST include **exactly one instance** of a **user preference contradiction**.
    - The contradiction must be realistic and grounded in the persona, conversation context, or internal conflict.
    - Use one of the following **six types of contradictory preferences** (pick one per conversation):

        🧠 **Categories of Contradictory Preferences**
        
        1. **Contextual Contradiction:**  
           A preference changes due to situational factors.  
           Example: "I like sweets." → "I don’t like sweets today, I’m sick."
        
        2. **Trade-off Contradiction:**  
           Two incompatible preferences emerge.  
           Example: "I want short answers." → "You didn’t give enough detail."
        
        3. **Topic-Specific Contradiction:**  
           Preference varies across tasks/domains.  
           Example: "Keep answers short." → "Give more details" (on emotional support).
        
        4. **Temporal Contradiction:**  
           A long-term shift in opinion.  
           Example: "I used to like horror." → "Now I find it too stressful."
        
        5. **Ambiguous Intent:**  
           Conflicting signals in user language.  
           Example: "I kinda like fast replies" → "Take your time though."
        
        6. **Meta-Preference:**  
           A rule about how preferences should be handled.  
           Example: "Keep it brief unless I ask for details."

    - Do NOT explicitly name the category in the conversation.
    - Let the preference contradiction emerge naturally from user behavior and wording.

    **Initiation Constraint:**
    - The contradiction must be **initiated or revealed by the user**, not proposed or encouraged by the agent.
    - The agent may offer helpful information, but should not push, persuade, or suggest a change in preference.
    - The user's shift must emerge through their own internal tension, doubt, or reevaluation.

    **Realism Constraint (User):**
    - The user should show realistic behavior: hesitation, self-reflection, emotional conflict, or self-contradiction.
    - Avoid overly smooth or instantly agreeable transitions. Users are allowed to express mixed feelings or uncertainty.

    **Agent Constraint:**
    - After the contradiction, the agent should adjust supportively, but avoid celebrating or reinforcing the change too eagerly.
    - The agent must NOT appear to guide or lead the user to a new preference.

7. **Post-Change Continuity:**
    - After the preference change, continue for at least 2–3 more turns per speaker (4–6 turns total).
    - The agent should adapt to the updated preference, and the user’s utterances should reflect it implicitly.

8. **Concluding Turn:**
    - The final turn must be from the **user**.
    - It must contain a **request or question** that reflects the **new preference**, but does **not** refer explicitly to the change.
    - Example: After switching from solo to group activities, a valid final turn might be:  
      > "Do you think I should invite coworkers too?"  
      — without saying, "Now that I changed my mind..."

Ensure the final output is a **valid Python list of dictionaries**, ends with a **user turn**, and satisfies all constraints above.
"""
    return prompt


def prompts_for_finding_preference_change_and_gen_agent_answers(data):
    prompt = f"""
    Read the following conversation, it consists of multiple turns, each turn is represented as turn_id, speaker, text.
    In this conversation, there is exactly one instance where the user's preference changes between two different user turns. This change could be:
    - "Direct": a direct contradiction to a preference the user expressed in an earlier turn.
    - "Indirect": the preference evolves perhaps due to new information, or the preference changes because of a situational context.
    The user's final turns in the conversation will be relevant to this preference change.

    You have two tasks:

    **Task 1: Identify and Describe the Preference Change**

    1.  Locate the user's turn where the new preference (`curr_pref`) is expressed.
    2.  Locate the *earlier* user's turn where the *original/contrasting* preference (`prev_pref`) was expressed.
    3.  These preferences must be from different user turns (i.e., `curr_turn_id` and `prev_turn_id` must be different). Do not identify preference expressions that change within the same user turn. Do not identify the last turn as a preference change.
    4.  Record this information as a single Python dictionary. Ensure the output for this task is enclosed in a Python code block (```python ... ```).

        The dictionary must follow this structure and use these exact keys:
        {{
            "curr_pref": "A concise summary (3-7 words) of the user's new/changed preference.",
            "curr_turn_id": "The integer turn_id of the user's utterance where the new preference is expressed.",
            "prev_pref": "A concise summary (3-7 words) of the user's original preference that contrasts with the current one.",
            "prev_turn_id": "The integer turn_id of the user's utterance where the original preference was expressed.",
            "type": "A string, either 'Direct' OR 'Indirect',
            "certainty": "A string indicating your confidence in this identification: 'high', 'medium', or 'low'."
        }}

        **Example of the preference change dictionary structure (use actual data from the conversation):**
        ```python
        {{
            "curr_pref": "Wants a gaming laptop",
            "curr_turn_id": 2,
            "prev_pref": "Wants a quiet laptop",
            "prev_turn_id": 0,
            "type": "Indirect",
            "certainty": "high"
        }}
        ```
        (Note: ensure `curr_turn_id` and `prev_turn_id` should be integers from the conversation. And ensure curr_turn_id is NOT the last turn of the conversation)

    **Task 2: Generate Agent Responses**

    Following the *entire* conversation, generate two distinct possible responses from the agent. These two responses should be recorded as a single Python dictionary. Ensure the output for this task is enclosed in a separate Python code block (```python ... ```).

    The dictionary must follow this structure and use these exact keys:
    {{
        "preferred_response": "The agent's response here. This response MUST correctly adapt to the user's identified preference change.",
        "dispreferred_response": "The agent's response here. This response MUST demonstrate a failure to understand or acknowledge the user's preference change. For example, it might respond based on the user's *original* (outdated) preference, express confusion related to the new preference, or ignore the change completely."
    }}

    **Example of the agent responses dictionary structure (fill with generated text):**
    ```python
    {{
        "dispreferred_response": "Okay, so focusing on ultra-quiet models, I have a few fanless options here...",
        "preferred_response": "Understood! So, while gaming laptops do need robust cooling, I can look for models known for more efficient and quieter fan systems, or those with customizable fan profiles. What kind of games are you planning to play?"
    }}
    Now, analyze the following conversation:

    {data}
    """
    return prompt
