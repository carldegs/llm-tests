from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

from utils import load_config_file
from vector_store import setup_vector_store
from assistant import setup_assistant
from typing_extensions import override
from openai import AssistantEventHandler, OpenAI

load_dotenv()

client = OpenAI()

config = load_config_file()

if not config.get("assistant_id"):
    print("Setting up assistant...")
    setup_assistant()

if not config.get("vector_store_id"):
    print("Setting up vector store...")
    setup_vector_store()

assistant = client.beta.assistants.update(
    assistant_id=config.get("assistant_id"),
    tool_resources={"file_search": {
        "vector_store_ids": [config.get("vector_store_id")]}},
)


class Response(BaseModel):
    type: str
    message: str


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        # create a completion to show the message as json
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": """
                  Parse the data provided as JSON with the following fields
                  - type: either TRANSFER (if the inquiry is considered TRANSFERABLE) or MESSAGE
                  - message: the actual message
                 """},
                {"role": "user", "content": message_content.value},
            ],
            response_format=Response
        )

        print(f"\nassistant > {completion.choices[0].message.parsed}")


thread = client.beta.threads.create(
    messages=[
        {
            "role": "user",
            "content": "What is my salary grade as an Assistant Prof?",
            # "content": "What's the Social Sciences and Law Cluster?",
            # "content": "What is the weather in UP Diliman?",
            # "content": "I want to enroll in UP Diliman.",
        }
    ]
)

with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
