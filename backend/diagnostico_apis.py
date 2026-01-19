#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de las APIs de IA
"""

import os
import sys

def check_env_vars():
    """Verifica variables de entorno"""
    print("=" * 60)
    print("DIAGNÓSTICO DE APIs DE IA")
    print("=" * 60)

    apis = {
        "OPENAI_API_KEY": "OpenAI GPT-4",
        "GOOGLE_API_KEY": "Google Gemini",
        "ANTHROPIC_API_KEY": "Anthropic Claude",
    }

    print("\n1. VARIABLES DE ENTORNO:")
    print("-" * 40)

    for var, nombre in apis.items():
        value = os.getenv(var)
        if value:
            # Mostrar solo los primeros y últimos caracteres
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"  ✓ {nombre}: Configurado ({masked})")
        else:
            print(f"  ✗ {nombre}: NO CONFIGURADO")

    return apis

def test_openai():
    """Prueba conexión con OpenAI"""
    print("\n2. TEST OPENAI:")
    print("-" * 40)

    if not os.getenv("OPENAI_API_KEY"):
        print("  ⚠ OPENAI_API_KEY no configurada")
        return False

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Responde solo: OK"}],
            max_tokens=10,
        )

        result = response.choices[0].message.content
        print(f"  ✓ OpenAI GPT-4o: OPERATIVO (respuesta: {result})")
        return True

    except Exception as e:
        print(f"  ✗ OpenAI ERROR: {e}")
        return False

def test_gemini():
    """Prueba conexión con Gemini"""
    print("\n3. TEST GEMINI:")
    print("-" * 40)

    if not os.getenv("GOOGLE_API_KEY"):
        print("  ⚠ GOOGLE_API_KEY no configurada")
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content("Responde solo: OK")
        result = response.text.strip()
        print(f"  ✓ Gemini 1.5 Flash: OPERATIVO (respuesta: {result})")
        return True

    except Exception as e:
        print(f"  ✗ Gemini ERROR: {e}")
        return False

def test_anthropic():
    """Prueba conexión con Anthropic"""
    print("\n4. TEST ANTHROPIC:")
    print("-" * 40)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("  ⚠ ANTHROPIC_API_KEY no configurada")
        return False

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Responde solo: OK"}]
        )

        result = response.content[0].text
        print(f"  ✓ Anthropic Claude: OPERATIVO (respuesta: {result})")
        return True

    except Exception as e:
        print(f"  ✗ Anthropic ERROR: {e}")
        return False

def main():
    # Cargar .env si existe
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("(Cargado .env)")
    except:
        pass

    check_env_vars()

    openai_ok = test_openai()
    gemini_ok = test_gemini()
    anthropic_ok = test_anthropic()

    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("=" * 60)

    if openai_ok:
        print("  ✓ OpenAI: OPERATIVO (provider principal)")
    elif gemini_ok:
        print("  ⚠ OpenAI: NO DISPONIBLE")
        print("  ✓ Gemini: OPERATIVO (fallback disponible)")
    else:
        print("  ✗ OpenAI: NO DISPONIBLE")
        print("  ✗ Gemini: NO DISPONIBLE")
        print("  ⚠ CRÍTICO: Sin proveedores IA - solo análisis básico funcionará")

    if anthropic_ok:
        print("  ✓ Anthropic: OPERATIVO")
    else:
        print("  ⚠ Anthropic: NO DISPONIBLE")

    print("\n")

    return 0 if (openai_ok or gemini_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
