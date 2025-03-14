import os
from bs4 import BeautifulSoup

def test_read_html(file_path):
    """Testa a leitura do arquivo HTML com diferentes encodings"""
    try:
        # Tenta primeiro com windows-1252
        with open(file_path, 'r', encoding='windows-1252') as f:
            content = f.read()
            print("Leitura bem sucedida com windows-1252")
            
            # Parse o HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Procura tabelas
            tables = soup.find_all('table')
            print(f"Encontradas {len(tables)} tabelas")
            
            # Procura células com classe 'sl'
            sl_cells = soup.find_all('td', class_='sl')
            print(f"Encontradas {len(sl_cells)} células com classe 'sl'")
            
            # Verifica alguns horários
            for cell in sl_cells:
                row = cell.parent
                if row:
                    cols = row.find_all('td')
                    if len(cols) >= 9:
                        horario = cols[8].get_text().strip()
                        print(f"Horário encontrado: {horario}")
            
    except UnicodeDecodeError:
        print("Falha com windows-1252, tentando utf-8")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("Leitura bem sucedida com utf-8")
        except UnicodeDecodeError:
            print("Falha na leitura com ambos encodings")

if __name__ == "__main__":
    test_read_html("download.html")
