import yaml
from google import genai

with open("config.yaml") as config_f:
    config = yaml.safe_load(config_f)

def main():
    print("Hello from rag-system-scientific-articles!")

    client = genai.Client(
        vertexai=True,
        project=config["gcp"]["project_id"],
        location=config["gcp"]["location"],
    )
    response = client.models.generate_content(
        model=config["gcp"]["model"],
        contents="Hello!",
    )
    print(response.text)

if __name__ == "__main__":
    main()
