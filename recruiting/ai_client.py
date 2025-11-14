import os, json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SCHEMA = {
  "type": "object",
  "properties": {
    "full_name": {"type": "string"},
    "emails": {"type": "array", "items": {"type": "string"}},
    "phones": {"type": "array", "items": {"type": "string"}},
    "skills": {
      "type": "object",
      "properties": {
        "hard": {"type": "array", "items": {"type": "string"}},
        "soft": {"type": "array", "items": {"type": "string"}}
      }
    },
    "education": {"type": "array"},
    "experience": {"type": "array"},
    "links": {"type": "array"},
    "languages": {"type": "array"},
  },
  "required": ["full_name", "emails", "skills"]
}

SYSTEM_MESSAGE = """
Eres un parser ATS experto.
Extrae información de un CV en español o inglés.
Nunca inventes datos. Si no existe, deja arrays vacíos o string vacío.
Responde SOLO en JSON siguiendo el esquema.
"""

def parse_cv_text(cv_text: str):
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": f"Esquema:\n{json.dumps(SCHEMA)}\n\nCV:\n{cv_text[:20000]}"}
    ]

    result = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.1
    )

    content = result.choices[0].message.content
    return json.loads(content)
