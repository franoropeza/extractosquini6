import requests
from bs4 import BeautifulSoup
import urllib3

# Desactivar advertencias de certificado SSL (común en sitios gov.ar)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def descargar_quini_requests():
    print("1. Configurando sesión HTTP...")
    
    url = "https://apps.loteriasantafe.gov.ar:8443/Extractos/paginas/mostrarQuini6.xhtml"
    
    # Cabeceras para parecer un Chrome real desde Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    session = requests.Session()
    session.headers.update(headers)

    print(f"2. Conectando a {url} ...")
    try:
        # verify=False es clave para evitar errores de SSL en sitios del gobierno
        response = session.get(url, timeout=30, verify=False)
        response.raise_for_status() # Lanza error si no es 200 OK
        print("   -> ¡Conexión exitosa! (Status 200)")
    except Exception as e:
        print(f"Error crítico al conectar: {e}")
        return

    print("3. Buscando enlace en el HTML...")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscamos el div y luego el enlace dentro
    div_extracto = soup.find('div', class_='soloextracto')
    
    if div_extracto:
        enlace = div_extracto.find('a')
        if enlace and enlace.get('href'):
            href_sucio = enlace.get('href')
            # Limpiamos URL
            pdf_url = href_sucio.replace('&amp;', '&')
            if not pdf_url.startswith('http'):
                # Si es ruta relativa, le pegamos el dominio
                pdf_url = "https://apps.loteriasantafe.gov.ar:8443" + pdf_url
            
            print(f"   -> Enlace encontrado: {pdf_url}")
            
            # Descargamos el PDF
            print("4. Descargando PDF...")
            try:
                pdf_response = session.get(pdf_url, timeout=30, verify=False)
                nombre_archivo = "extracto_quini_ultimo.pdf"
                with open(nombre_archivo, 'wb') as f:
                    f.write(pdf_response.content)
                print(f"✅ ¡Archivo guardado!: {nombre_archivo}")
            except Exception as e:
                 print(f"Error descargando el PDF: {e}")
        else:
             print("Error: Se encontró el div, pero no el enlace <a> dentro.")
    else:
        print("Error: No se encontró <div class='soloextracto'> en el HTML recibido.")
        # Debug: imprimir un poco del HTML para ver qué nos devolvió
        print("Contenido parcial recibido:", response.text[:500])

if __name__ == "__main__":
    descargar_quini_requests()
