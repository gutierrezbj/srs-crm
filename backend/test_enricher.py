#!/usr/bin/env python3
"""
Script de diagnóstico para el AdjudicatarioEnricher.
Prueba el scraping de PLACSP y muestra qué datos se extraen.

USO:
    cd /var/www/srs-crm/backend
    python3 test_enricher.py "URL_DE_PLACSP"

EJEMPLO:
    python3 test_enricher.py "https://contrataciondelestado.es/wps/poc?uri=deeplink:detalle_licitacion&idEvl=abc123"

Para obtener una URL válida:
    1. Ir a https://contrataciondelestado.es
    2. Buscar una licitación con estado "Adjudicada" o "Resuelta"
    3. Copiar la URL de la página de detalle
"""

import asyncio
import logging
import sys
import os

# Añadir el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scrape_placsp():
    """Prueba el scraping directo de una página PLACSP"""
    from app.spotter.adjudicatario_enricher import AdjudicatarioEnricher
    import httpx
    from bs4 import BeautifulSoup

    enricher = AdjudicatarioEnricher()

    # Si se pasa URL como argumento, usarla
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"\n{'='*60}")
        print(f"PROBANDO URL: {url}")
        print('='*60)

        # 1. Primero, descargar y mostrar estructura HTML
        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": enricher.USER_AGENT},
                    follow_redirects=True
                )

                print(f"\n1. HTTP Status: {response.status_code}")
                print(f"   URL Final: {response.url}")
                print(f"   Content-Length: {len(response.text)} caracteres")

                if response.status_code != 200:
                    print(f"   ERROR: Respuesta no exitosa")
                    return

                soup = BeautifulSoup(response.text, 'html.parser')

                # 2. Mostrar título de la página
                title = soup.find('title')
                print(f"\n2. Título página: {title.get_text() if title else 'Sin título'}")

                # 3. Buscar tablas con datos
                tables = soup.find_all('table')
                print(f"\n3. Tablas encontradas: {len(tables)}")

                # 4. Buscar filas con labels conocidos
                print("\n4. Buscando campos conocidos en filas de tabla:")
                campos_encontrados = {}
                labels_buscados = [
                    'adjudicatario', 'contratista', 'expediente', 'objeto',
                    'importe', 'estado', 'cpv', 'órgano', 'lugar'
                ]

                for row in soup.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        for buscar in labels_buscados:
                            if buscar in label and value:
                                campos_encontrados[label[:40]] = value[:80]
                                print(f"   ✓ {label[:40]}: {value[:80]}")
                                break

                if not campos_encontrados:
                    print("   ⚠ No se encontraron campos en tablas")

                    # Mostrar primeras filas para debug
                    print("\n   Primeras 10 filas de tabla encontradas:")
                    for i, row in enumerate(soup.find_all('tr')[:10]):
                        cells = row.find_all(['td', 'th'])
                        if cells:
                            print(f"   [{i}] {[c.get_text(strip=True)[:30] for c in cells[:3]]}")

                # 5. Buscar enlaces a documentos
                print("\n5. Enlaces a documentos (XML/PDF/HTML):")
                docs_encontrados = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)

                    if any(ext in href.lower() for ext in ['.xml', '.pdf', '.html']):
                        doc_type = 'XML' if '.xml' in href.lower() else 'PDF' if '.pdf' in href.lower() else 'HTML'
                        docs_encontrados.append((doc_type, text[:50], href[:80]))
                        print(f"   [{doc_type}] {text[:50]}")

                if not docs_encontrados:
                    print("   ⚠ No se encontraron enlaces a documentos")

                    # Buscar por imágenes de iconos
                    print("\n   Buscando iconos de documentos:")
                    for link in soup.find_all('a', href=True):
                        img = link.find('img')
                        if img:
                            alt = img.get('alt', '')
                            src = img.get('src', '')
                            if any(x in alt.lower() or x in src.lower() for x in ['xml', 'pdf', 'doc']):
                                print(f"   Icono: alt='{alt}', href={link.get('href')[:60]}")

                # 6. Buscar divs con clases relevantes
                print("\n6. Divs con clases relevantes:")
                for div in soup.find_all('div', class_=True):
                    classes = ' '.join(div.get('class', []))
                    if any(x in classes.lower() for x in ['campo', 'field', 'dato', 'valor', 'detalle']):
                        print(f"   div.{classes}: {div.get_text(strip=True)[:60]}")

        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()

        # 7. Ahora probar el método _scrape_placsp del enricher
        print(f"\n{'='*60}")
        print("7. PROBANDO MÉTODO _scrape_placsp()")
        print('='*60)

        try:
            datos = await enricher._scrape_placsp(url)

            if datos:
                print(f"\n   ✓ Datos extraídos ({len(datos)} campos):")
                for key, value in sorted(datos.items()):
                    if value:
                        valor_str = str(value)[:60] if not isinstance(value, list) else f"[{len(value)} items]"
                        print(f"     - {key}: {valor_str}")
            else:
                print("\n   ✗ No se extrajeron datos")

        except Exception as e:
            print(f"\n   ERROR en _scrape_placsp: {e}")
            import traceback
            traceback.print_exc()

        # 8. Probar enriquecimiento completo
        print(f"\n{'='*60}")
        print("8. PROBANDO ENRIQUECIMIENTO COMPLETO")
        print('='*60)

        try:
            from app.spotter.adjudicatario_enricher import enriquecer_adjudicatario

            # Usar datos de prueba
            resultado = await enriquecer_adjudicatario(
                nombre="EMPRESA TEST",
                nif="A00000000",
                url_licitacion=url
            )

            if resultado:
                print(f"\n   Resultado ({resultado.get('fuente', 'sin fuente')}, confianza: {resultado.get('confianza', '?')}):")
                campos_con_valor = {k: v for k, v in resultado.items() if v and k not in ['nombre', 'nif', 'fecha_enriquecimiento']}

                if campos_con_valor:
                    for key, value in sorted(campos_con_valor.items()):
                        valor_str = str(value)[:60] if not isinstance(value, (list, dict)) else f"[{type(value).__name__}]"
                        print(f"     - {key}: {valor_str}")
                else:
                    print("     ⚠ Solo datos básicos (nombre, nif)")
            else:
                print("\n   ✗ Sin resultado")

        except Exception as e:
            print(f"\n   ERROR en enriquecimiento: {e}")
            import traceback
            traceback.print_exc()

    else:
        print("\nUso: python test_enricher.py <URL_PLACSP>")
        print("\nEjemplo:")
        print("  python test_enricher.py 'https://contrataciondelestado.es/wps/poc?uri=deeplink:detalle_licitacion&idEvl=abc123'")
        print("\nPara obtener una URL de prueba:")
        print("  1. Ve a https://contrataciondelestado.es")
        print("  2. Busca una licitación con estado 'Adjudicada' o 'Resuelta'")
        print("  3. Copia la URL de la página de detalle")


async def main():
    """Punto de entrada principal"""
    print("="*60)
    print("DIAGNÓSTICO DEL ADJUDICATARIO ENRICHER")
    print("="*60)

    # Verificar imports
    try:
        from app.spotter.adjudicatario_enricher import AdjudicatarioEnricher
        print("✓ Import adjudicatario_enricher OK")
    except ImportError as e:
        print(f"✗ Error importando adjudicatario_enricher: {e}")
        sys.exit(1)

    try:
        import httpx
        print("✓ Import httpx OK")
    except ImportError:
        print("✗ httpx no instalado")
        sys.exit(1)

    try:
        from bs4 import BeautifulSoup
        print("✓ Import BeautifulSoup OK")
    except ImportError:
        print("✗ beautifulsoup4 no instalado")
        sys.exit(1)

    try:
        import pdfplumber
        print("✓ Import pdfplumber OK")
    except ImportError:
        print("⚠ pdfplumber no instalado (extracción PDF deshabilitada)")

    await test_scrape_placsp()


if __name__ == "__main__":
    asyncio.run(main())
