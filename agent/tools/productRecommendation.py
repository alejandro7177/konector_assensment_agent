import os, json, re
import openai

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(".env")
    client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt_system = ""
    with open("agent/prompts/generateFilterDB.md", "r", encoding="utf-8") as f:
        prompt_system = f.read()

    raw = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": "I want a robust actuator for hazardous environments with an Duty Cycle of less than 200"}
        ]
    )

    match = re.search(
        r"```json\s*(.*?)```", 
        raw.choices[0].message.content, 
        re.DOTALL
    )
    if match:
        json_text = match.group(1)
    else:
        json_text = raw

    response = json.loads(json_text)
    print(json.dumps(response, indent=2))