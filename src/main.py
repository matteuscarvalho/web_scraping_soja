import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta

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

def get_date_input(prompt):
    while True:
        date = input(prompt)
        try:
            day, month, year = map(int, date.split('/'))
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            print("Data inválida. Use o formato DD/MM/AAAA.")

def generate_date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)

    dates = []
    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta

    return dates

if __name__ == "__main__":
    start_date = get_date_input("Digite a data de início (DD/MM/AAAA): ")
    end_date = get_date_input("Digite a data final (DD/MM/AAAA): ")

    date_range = generate_date_range(start_date, end_date)

    base_dir = 'data'
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for date in date_range:
        print(f"Coletando dados para {date}...")

        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")

        month_dir = os.path.join(base_dir, month)

        if not os.path.exists(month_dir):
            os.makedirs(month_dir)

        result = scrape_soybean_prices(date)
        if result:
            save_to_csv(result, month_dir, month)
