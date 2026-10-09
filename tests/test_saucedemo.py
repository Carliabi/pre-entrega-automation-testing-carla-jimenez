import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import hacer_login


@pytest.fixture
def driver():
    # Opciones de Chrome: desactivo el aviso de contraseñas que tapaba el carrito
    opciones = webdriver.ChromeOptions()
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    opciones.add_argument("--incognito")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.maximize_window()

    yield driver

    driver.quit()


def test_01_login(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    url_actual = driver.current_url
    titulo_pagina = driver.title
    titulo_seccion = driver.find_element(By.CLASS_NAME, "title").text

    assert "/inventory.html" in url_actual, f'ERROR: URL esperada con "/inventory.html", obtenida: {url_actual}'
    assert titulo_pagina == "Swag Labs", f'ERROR: Título de ventana esperado "Swag Labs", obtenido: {titulo_pagina}'
    assert titulo_seccion == "Products", f'ERROR: Título de sección esperado "Products", obtenido: {titulo_seccion}'

def test_02_verificar_catalogo(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    titulo_pagina = driver.title
    titulo_seccion = driver.find_element(By.CLASS_NAME, "title").text

    assert titulo_pagina == "Swag Labs", f'ERROR: Título de ventana esperado "Swag Labs", obtenido: {titulo_pagina}'
    assert titulo_seccion == "Products", f'ERROR: Título de sección esperado "Products", obtenido: {titulo_seccion}'

def test_03_productos_visibles(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    inventory_item = driver.find_elements(By.CLASS_NAME, "inventory_item")
    assert len(inventory_item) > 0, "ERROR: No se encontraron productos visibles"

    primero = inventory_item[0]
    nombre = primero.find_element(By.CLASS_NAME, "inventory_item_name").text
    precio = primero.find_element(By.CLASS_NAME, "inventory_item_price").text
    print(f"Primer producto: {nombre} - {precio}")

    assert nombre != "", "ERROR: El primer producto no tiene nombre"
    assert precio.startswith("$"), f'ERROR: Precio esperado con "$", obtenido: {precio}'

def test_04_validar_interfaz(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    menu_button = driver.find_element(By.ID, "react-burger-menu-btn")
    filtro = driver.find_element(By.CLASS_NAME, "product_sort_container")

    assert menu_button.is_displayed(), "ERROR: Menú no está visible"
    assert filtro.is_displayed(), "ERROR: Filtro no está visible"


def test_05_agregar_producto_al_carrito(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    first_item = driver.find_elements(By.CLASS_NAME, "inventory_item")[0]
    boton_agregar = first_item.find_element(By.TAG_NAME, "button")
    boton_agregar.click()

    # Espera explícita 
    espera.until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, ".inventory_item button"), "Remove"
    ))

    texto_boton = driver.find_element(By.CSS_SELECTOR, ".inventory_item button").text
    assert texto_boton.capitalize() == "Remove", f'ERROR: el botón no cambió a "Remove", obtenido: {texto_boton}'

def test_06_verificar_contador_carrito(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    # Agrego el primer producto
    driver.find_elements(By.CLASS_NAME, "inventory_item")[0].find_element(By.TAG_NAME, "button").click()

    # Espera explícita
    contador_carrito = espera.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge"))
    ).text

    assert contador_carrito == "1", f"ERROR: Se esperaba 1, obtuvo {contador_carrito}"


def test_07_navegar_carrito(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    #  Agrego el primer producto
    driver.find_elements(By.CLASS_NAME, "inventory_item")[0].find_element(By.TAG_NAME, "button").click()

    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()

    # Espera explícita
    espera.until(EC.url_contains("/cart.html"))

    assert "/cart.html" in driver.current_url, "ERROR: No se redirigió a /cart.html"


def test_08_comprobar_producto_en_el_carrito(driver):
    hacer_login(driver)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.url_contains("/inventory.html"))

    # Guardo el nombre del primer producto y lo agrego
    first_item = driver.find_elements(By.CLASS_NAME, "inventory_item")[0]
    nombre_producto = first_item.find_element(By.CLASS_NAME, "inventory_item_name").text
    first_item.find_element(By.TAG_NAME, "button").click()

    # Voy al carrito
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    espera.until(EC.url_contains("/cart.html"))

    producto_nombre_en_carrito = driver.find_element(By.CLASS_NAME, "inventory_item_name").text

    assert producto_nombre_en_carrito == nombre_producto, f'ERROR: Producto esperado "{nombre_producto}", en el carrito: "{producto_nombre_en_carrito}"'
    