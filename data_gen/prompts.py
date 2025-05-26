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

    1.  **Participants:** The conversation is strictly multi-turn between a "user" and an "agent".
    2.  **User Persona:** The user's persona is: "{persona}". The user's language, motivations, initial requests, and subsequent changes in preference should be entirely consistent with this persona. The user should be seeking assistance from the agent related to the topic in a way that aligns with their persona.
    3.  **Turn Structure & Indexing:**
        * The conversation must be formatted as a list of Python dictionaries, the template is as follows:\n
        {{
            "turn_id": "xxx",
            "speaker": "user" | "agent", 
            "text": "yyy"
        }}
        Fill in the actual data at placeholders 'xxx' and 'yyy' in the template. Use double quotes.
    4.  **Conversation Length:** The conversation should consist of approximately 10-20 turns in total (e.g., 5-10 turns for the user and 5-10 turns for the agent).
    5.  **Content and Details:**
        * The conversation should be rich in relevant details pertaining to the "{topic}", but can contain other information if needed.
        * The agent should be helpful, informative, and responsive, attempting to assist the user with their queries and goals.
    6.  **Change in User Preference:**
        * The conversation MUST include one change in the user's preferences between different turns.
        * This change can be a direct contradiction of an earlier stated preference OR an envolving preference due to new information provided by the agent OR a situational context change revealed by the user.
        * After the user indicates a change in preference, the conversation MUST continue for at least 2-3 more turns per speaker. That is to say, the ending of the conversation should be at least 4-6 turns after the user has expressed a preference change.
    7.  **Concluding Turn:**
        * The conversation MUST end with a final utterance from the "user", NOT the "agent"
        * In this final utterance, the user should ask the agent a question or make a request.
        * This question/request MUST be related to the preference that was changed previously.
        * Crucially, the user should NOT explicitly state or refer to the changed preference itself in this final utterance. The question/request should implicitly reflect the new preference. For example, if the user initially wanted a solo activity and then changed to wanting a group activity, their final question might be "What are the options for larger group bookings?" without saying "Now that I want a group activity...".

    Ensure the generated output is a valid Python list of dictionaries.
    Ensure the generated conversation ends with a user turn.
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