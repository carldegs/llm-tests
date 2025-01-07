from openai import OpenAI
from dotenv import load_dotenv
from utils import update_config_file

load_dotenv()

client = OpenAI()

instructions = """
# Context #
You are an admin of UP Diliman. Use your knowledge base to answer questions about UP Diliman policies and procedures.

If the inquiry is about the following items, this is considered TRANSFERABLE:
- weather
- sports
- enrolling to the university

If the user asked non-relevant questions, do not answer.

# Response #
Your response should contain the following
- type: either TRANSFER (if the inquiry is considered TRANSFERABLE) or RESPONSE
- message: the actual message
"""


def setup_assistant():
    assistant = client.beta.assistants.create(
        name="UP Admin Assistant",
        instructions="You are an admin of UP Diliman. Use your knowledge base to answer questions about UP Diliman policies and procedures.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

    update_config_file("assistant_id", assistant.id)
