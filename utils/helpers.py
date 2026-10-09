from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.saucedemo.com"
USUARIO_VALIDO = "standard_user"
CLAVE_VALIDA = "secret_sauce"


def hacer_login(driver, usuario="standard_user", clave="secret_sauce"):
    # Abre saucedemo e inicia sesión con las credenciales.
    driver.get(URL)
    espera = WebDriverWait(driver, 10)
    espera.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(clave)
    driver.find_element(By.ID, "login-button").click()