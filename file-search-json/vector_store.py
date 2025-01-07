from openai import OpenAI
from utils import load_config_file, update_config_file
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def setup_vector_store():
    vector_store = client.beta.vector_stores.create(name="UP Admin Files")
    file_paths = ["dataset/UPD_Faculty_Manual.pdf"]
    file_streams = [open(path, "rb") for path in file_paths]

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )

    print(file_batch.status)
    print(file_batch.file_counts)

    update_config_file("vector_store_id", vector_store.id)


def delete_vector_store():
    config = load_config_file()
    vector_store_id = config.get("vector_store_id")
    if vector_store_id:
        client.beta.vector_stores.delete(vector_store_id)
        print(f"Deleted vector store {vector_store_id}")
    else:
        print("No vector store to delete")
