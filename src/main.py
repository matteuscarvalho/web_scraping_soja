import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

def scrape_soybean_prices(date):
    url = f"https://www.noticiasagricolas.com.br/cotacoes/soja/soja-bolsa-de-chicago-cme-group/{date}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o site para a data {date}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('div', class_='table-content')

    if not table:
        print(f"Tabela não encontrada para a data {date}.")
        return None

    rows = []
    for row in table.find_all('tr')[1:]: 
        cells = [cell.text.strip() for cell in row.find_all('td')]
        if len(cells) == 4:
            cells.insert(0, date) 
            rows.append(cells)

    return rows

def save_to_csv(rows, month_dir, month):
    filename = os.path.join(month_dir, f"soja_precos_{month}.csv")

    file_exists = os.path.exists(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Data', 'Contrato - Mês', 'Fechamento (US$ / Bushel)', 'Variação (cents/US$)', 'Variação (%)'])
        
        writer.writerows(rows)

    print(f"Dados salvos em {filename}")

def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)

    dates = []
    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta

    return dates

def process_date(date, base_dir):
    month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    month_dir = os.path.join(base_dir, month)

    if not os.path.exists(month_dir):
        os.makedirs(month_dir)

    result = scrape_soybean_prices(date)
    if result:
        save_to_csv(result, month_dir, month)

if __name__ == "__main__":
    start_date = input("Digite a data de início (DD/MM/AAAA): ")
    end_date = input("Digite a data final (DD/MM/AAAA): ")

    start_date = datetime.strptime(start_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%d/%m/%Y").strftime("%Y-%m-%d")

    date_range = generate_date_range(start_date, end_date)
    base_dir = 'data'

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda date: process_date(date, base_dir), date_range)

    print("Coleta de dados concluída!")
