import os, json
from preprocessing.chroma import Chroma
from langchain_openai.embeddings import OpenAIEmbeddings
from concurrent.futures import ThreadPoolExecutor, as_completed

def main():
    from dotenv import load_dotenv
    load_dotenv(".env")

    #Crear Objeto de coneccion de ChromaDB
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", 
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    chroma = Chroma(embeddings=embeddings)
    print("ChromaDB reseted")
    print("Checking ChromaDB health...")
    print("ChromaDb List Collections: ", chroma.client.list_collections())
    for collection in chroma.client.list_collections():
        print("Deleting collection: ", collection.name)
        chroma.client.delete_collection(name=collection.name)
    if chroma.check_health():
        print("ChromaDB is healthy")
    else:
        print("ChromaDB is not healthy")
        return
    
    collection_name = "test_collection"
    collection = chroma.get_or_create_collection(collection_name)
    
    with open("data/atenuadores.json", "r", encoding="utf-8") as f:
        documents = json.load(f)
    print("len(documents): ", documents[0])
    num_cpus = os.cpu_count()
    with ThreadPoolExecutor(max_workers=num_cpus) as executor:
        results = executor.map(chroma.add_document, documents, [collection]*len(documents))

        for status in results:
            print(f"Registro {status}")

if __name__ == "__main__":
    main()

