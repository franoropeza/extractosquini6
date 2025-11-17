from playwright.sync_api import sync_playwright

def descargar_quini_directo_apps():
    with sync_playwright() as p:
        print("1. Iniciando navegador...")
        # HEADLESS=TRUE es obligatorio para GitHub Actions
        browser = p.chromium.launch(headless=True)
        
        # Configuramos contexto relajado (ignoramos errores de certificado SSL por el puerto 8443)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # --- LA URL DIRECTA QUE ENCONTRASTE ---
        url_apps = "https://apps.loteriasantafe.gov.ar:8443/Extractos/paginas/mostrarQuini6.xhtml"
        
        print(f"2. Conectando directamente al servidor de aplicaciones: {url_apps}")
        
        try:
            # Usamos timeout alto (60s) porque el puerto 8443 a veces es lento al iniciar
            page.goto(url_apps, timeout=60000, wait_until="domcontentloaded")
            print("   -> Conexión establecida.")
            
        except Exception as e:
            print(f"Error crítico al conectar: {e}")
            browser.close()
            return

        # --- EXTRACCIÓN DEL ENLACE ---
        print("3. Buscando el botón de descarga...")
        
        # Selector directo. Al ser la página de la app, el div debería estar ahí.
        selector = 'div.soloextracto > a'
        
        try:
            page.wait_for_selector(selector, timeout=30000)
            enlace = page.locator(selector)
            
            # Obtenemos la URL sucia
            pdf_url_cruda = enlace.get_attribute("href")
            if not pdf_url_cruda:
                raise Exception("Se encontró el botón pero no tiene enlace (href).")
                
            # Limpiamos la URL (quitamos los &amp;)
            pdf_url = pdf_url_cruda.replace("&amp;", "&")
            print(f"   -> URL del PDF encontrada: {pdf_url}")

        except Exception as e:
            print(f"Error buscando el elemento en la página: {e}")
            # Si falla, sacamos una foto para ver qué respondió el servidor
            # (Esto no se verá en GitHub Actions pero ayuda si lo corres local)
            # page.screenshot(path="debug_apps_error.png")
            browser.close()
            return

        # --- DESCARGA DEL ARCHIVO ---
        print("4. Descargando el archivo PDF...")
        try:
            # Usamos el contexto de API para bajarlo rápido
            api_context = context.request
            response = api_context.get(pdf_url)
            
            if not response.ok:
                print(f"Error en la descarga: Servidor respondió {response.status}")
                browser.close()
                return

            pdf_bytes = response.body()
            
            # Validación simple de tamaño
            if len(pdf_bytes) < 1000:
                print("Advertencia: El archivo descargado es sospechosamente pequeño.")

            nombre_archivo = "extracto_quini_ultimo.pdf"
            with open(nombre_archivo, "wb") as f:
                f.write(pdf_bytes)

            print(f"✅ ¡Misión Cumplida! Archivo guardado: {nombre_archivo}")

        except Exception as e:
            print(f"Error técnico durante la descarga: {e}")

        browser.close()

if __name__ == "__main__":
    descargar_quini_directo_apps()
