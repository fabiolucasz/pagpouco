import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do navegador
options = Options()
#options.add_argument("--headless")  # Executa em modo headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")

# Inicializar o WebDriver
driver = webdriver.Chrome(options=options)

try:
    # Acessar a URL
    origem = "FOR"
    destino = "RIO"
    data_ida = "05-02-2026"
    url = f"https://b2c.voegol.com.br/compra/busca-parceiros?de={origem}&para={destino}&ida={data_ida}&ADT=1&ADL=0&CHD=0&INF=0&pv=br&tipo=DF&gclid=Cj0KCQjwndHEBhDVARIsAGh0g3AVSPDokhuYBa4BECbApkty4hZk0hEm7ZEq5B6-4OYoFXYjKyKuS8kaAmdREALw_wcB"
    driver.get(url)

    wait = WebDriverWait(driver, 20)
    table = wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='idAppRoot']/b2c-flow/main/b2c-select-flight/section/div[3]/section/form"))

    )

    data = []

    for top_3 in range(1, 4):

        valor_origem = driver.find_element(By.XPATH, f"//*[@id='lbl_origin_{top_3}_emission']")
        valor_destino = driver.find_element(By.XPATH, f"//*[@id='lbl_destination_{top_3}_emission']")
        valor_duracao = driver.find_element(By.XPATH, f"//*[@id='lbl_duration_{top_3}_emission']")
        valor_operador = driver.find_element(By.XPATH, f"//*[@id='lbl_segment_{top_3}_emission']")
        valor_preco = driver.find_element(By.XPATH, f"//*[@id='lbl_priceValue_{top_3}_emission']")

        data.append({"Origem": valor_origem.text, "Destino": valor_destino.text, "Duração": valor_duracao.text, "Operador": valor_operador.text, "Preço": valor_preco.text})

    df = pd.DataFrame(data)
    df.to_csv("voos_gol.csv", index=False)

    print(df)


except Exception as e:
    print(f"Erro ao processar a página: {e}")
finally:
    driver.quit()
    
