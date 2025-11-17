from playwright.sync_api import sync_playwright
import time

def descargar_pdf_con_api_request():
    with sync_playwright() as p:
        print("1. Iniciando navegador...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        url_resultados = "https://www.loteriasantafe.gov.ar/index.php/resultados/quini-6?view=resultados"
        print(f"2. Navegando a la página principal...")
        
        try:
            page.goto(url_resultados, timeout=20000, wait_until="load")
        except Exception as e:
            print(f"Error al cargar la página: {e}")
            browser.close()
            return

        print("3. Página cargada. Buscando el 'iframe'...")
        try:
            frame_resultados = page.frame_locator('iframe[src*="Extractos/paginas"]')
            frame_resultados.locator("body").wait_for(timeout=20000)
            print("   -> ¡Iframe de resultados encontrado!")
        except Exception as e:
            print(f"Error: No se pudo encontrar el <iframe>. {e}")
            browser.close()
            return

        print("4. Buscando el enlace de descarga (dentro del iframe)...")
        selector_link = 'div.soloextracto > a' 
        try:
            enlace = frame_resultados.locator(selector_link)
            enlace.wait_for(state="visible", timeout=10000)
            print("   -> ¡Enlace 'Ver extracto oficial' encontrado!")
        except Exception as e:
            print(f"Error: No se encontró el enlace DENTRO del iframe. {e}")
            browser.close()
            return

        # --- ¡LA SOLUCIÓN DEFINITIVA! ---
        
        print("5. Extrayendo la URL del enlace...")
        pdf_url_cruda = enlace.get_attribute("href")
        pdf_url = pdf_url_cruda.replace("&amp;", "&")
        print(f"   -> URL Limpia: {pdf_url}")

        print("6. Usando el contexto de API para descargar el archivo (sin navegador)...")
        
        try:
            # 6a. Usamos el contexto de 'request' del navegador (para compartir cookies, si fuera necesario)
            api_context = context.request
            
            # 6b. Hacemos una petición GET directa a la URL del PDF
            response = api_context.get(pdf_url)
            
            if not response.ok:
                print(f"Error: La petición GET al PDF falló con estado {response.status}")
                browser.close()
                return

            # 6c. Obtenemos los bytes "crudos" del PDF
            pdf_bytes = response.body()

            # 7. Guardamos los bytes en un archivo
            nombre_archivo = "extracto_quini_ultimo.pdf"
            with open(nombre_archivo, "wb") as f:
                f.write(pdf_bytes)

            print("---" * 10)
            print(f"✅ ¡Éxito! Archivo guardado (correctamente) como: {nombre_archivo}")
            print("---" * 10)

        except Exception as e:
            print(f"Hubo un error al descargar los bytes del PDF: {e}")

        browser.close()

if __name__ == "__main__":
    descargar_pdf_con_api_request()