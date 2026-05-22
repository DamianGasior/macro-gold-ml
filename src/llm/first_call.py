from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()  # automatycznie czyta OPENAI_API_KEY z .env

response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=200,
    messages=[
        {
            "role": "system",
            "content": """Jesteś inwestorem o horyzoncie średnio i długoterminowym.
Inwestujesz w ETF który ma pokrycie w złocie, ale do celów historycznych możesz odnosić się do ogólnej ceny złota.

Zasady:
- Starasz się znaleźć podobne sytuacje w przeszłości
- Odnosisz się do realnych wydarzeń w przeszłości i teraźniejszości
- Nie ograniczaj się do źródeł angielskich, korzystaj również ze źródeł rosyjskich, chińskich i z Ameryki Południowej
- Zamiast halucynować powiedz: 'nie znam odpowiedzi'
- Odpowiadaj po polsku, do 3 zdań""",
        },
        {"role": "user", "content": "Czy teraz warto kupić złoto?"},
    ],
)

print(f"print calego reposne type :\n {type(response)}")
print(f"print calego reposne:\n {response}")

print(f"print wybranej linii w response:\n {response.choices[0].message.content}")
print("\n--- Użycie tokenów ---")
print(f"Wysłane: {response.usage.prompt_tokens}")
print(f"Odebrane: {response.usage.completion_tokens}")
print(f"Razem: {response.usage.total_tokens}")
