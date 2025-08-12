import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import logging

# Configuração básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    options = Options()
    options.add_argument("--headless --no-sandbox --disable-dev-shm-usage")
    options.page_load_strategy = 'eager'  # Não espera carregar tudo
    return webdriver.Chrome(options=options)

def scrape_date(date_str, origem, destino):
    driver = setup_driver()
    try:
        url = f"https://b2c.voegol.com.br/compra/busca-parceiros?de={origem}&para={destino}&ida={date_str}&ADT=1"
        driver.get(url)
        
        # Espera otimizada
        try:
            xpath = "//*[contains(@id, 'lbl_origin_1_emission')]"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return []

        # Extrai os voos
        flights = []
        for i in range(1, 4):
            try:
                flight = {
                    "Data": date_str,
                    "Origem": driver.find_element(By.XPATH, f"//*[@id='lbl_origin_{i}_emission']").text,
                    "Destino": driver.find_element(By.XPATH, f"//*[@id='lbl_destination_{i}_emission']").text,
                    "Preço": driver.find_element(By.XPATH, f"//*[@id='lbl_priceValue_{i}_emission']").text
                }
                flights.append(flight)
            except:
                continue
        return flights
    except Exception as e:
        logging.error(f"Erro em {date_str}: {str(e)}")
        return []
    finally:
        driver.quit()

def main():
    origem = "FOR"
    destino = "RIO"
    data_ida = "05-02-2026"
    data_ida_max = "20-02-2026"
    
    # Gera lista de datas
    start = datetime.strptime(data_ida, "%d-%m-%Y")
    end = datetime.strptime(data_ida_max, "%d-%m-%Y")
    date_list = [(start + timedelta(days=x)).strftime("%d-%m-%Y") for x in range((end-start).days + 1)]
    
    # Processa em paralelo
    all_flights = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_date = {executor.submit(scrape_date, date, origem, destino): date for date in date_list}
        for future in concurrent.futures.as_completed(future_to_date):
            all_flights.extend(future.result())

    # Salva resultados
    if all_flights:
        df = pd.DataFrame(all_flights)
        filename = f"voos_gol_otimizado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"\nDados salvos em {filename}")
        print(f"Total de voos: {len(all_flights)}")
        print(df.head())

if __name__ == "__main__":
    main()