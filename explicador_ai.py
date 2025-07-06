# explicador_ai.py

from transformers import pipeline

# Cargamos un modelo multilingüe y compacto para explicaciones
summarizer = pipeline("summarization", model="csebuetnlp/mT5_multilingual_XLSum")

def explicar_codigo(code_fragment):
    if len(code_fragment.strip().split()) < 5:
        return "⚠️ Fragmento demasiado corto para generar explicación."

    prompt = (
        "Explica de forma clara y simple lo que hace este código Python:\n\n"
        + code_fragment
    )

    try:
        resumen = summarizer(prompt, max_length=80, min_length=30, do_sample=False)
        return resumen[0]["summary_text"]
    except Exception as e:
        return f"❌ Error al generar explicación: {e}"
