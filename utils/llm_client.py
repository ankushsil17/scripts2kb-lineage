import json
import openai


def call_llm(prompt: str, schema: dict, config, model_override: str = None) -> dict:
    client = openai.OpenAI(api_key=config.openai_api_key)
    model = model_override or config.model_primary
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Return only valid JSON matching the provided schema. No markdown, no commentary."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    text = response.choices[0].message.content.strip()
    return json.loads(text)


def call_llm_text(prompt: str, config, model_override: str = None) -> str:
    client = openai.OpenAI(api_key=config.openai_api_key)
    model = model_override or config.model_primary
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a technical assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
