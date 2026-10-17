import traceback
from src.config import settings
from src.llm_analysis import generate_analysis, _model_name

print("GROQ_MODEL:", settings.GROQ_MODEL)
print("Resolved model id:", _model_name())

evidence = [
    {"id": "[E1]", "fact": "New T2D treatments in 2026 include GLP-1 receptor agonists and dual agonists.", "source_title": "Diabetes Review", "source_url": "https://example.com", "snippet": "GLP-1 and dual agonists show strong results.", "confidence": 0.94},
    {"id": "[E2]", "fact": "Tirzepatide reduced HbA1c by 2.1% in phase 3 trials.", "source_title": "Clinical Trials Daily", "source_url": "https://example.com/2", "snippet": "Tirzepatide HbA1c reduction 2.1%.", "confidence": 0.92},
]

try:
    result = generate_analysis("latest treatments for type 2 diabetes 2026", evidence)
    print("SUCCESS")
    print("stat rows:", len(result["statistical_data"]))
    for s in result["statistical_data"][:3]:
        print("  ", s)
    print("themes:", len(result["key_themes"]))
    print("synthesis[:300]:", result["synthesis"][:300])
except Exception as e:
    print("FAILED:", type(e).__name__, str(e))
    traceback.print_exc()
