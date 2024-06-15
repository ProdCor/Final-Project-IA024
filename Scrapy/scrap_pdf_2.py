import os
import json
from PyPDF2 import PdfReader

def pdf_to_json(folder_path):
    data = {}  # Usando um dicionário para armazenar os dados
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(f"Extraindo texto de: {filename}")  # Log para saber qual arquivo está sendo processado
            file_path = os.path.join(folder_path, filename)
            reader = PdfReader(file_path)
            text_content = []
            for page in reader.pages:
                text_extract = page.extract_text()
                if text_extract:  # Garantir que apenas texto não nulo seja adicionado
                    text_content.append(text_extract)
            title_key = filename.replace('.pdf', '')  # Chave do dicionário
            data[title_key] = "\n".join(text_content)  # Atribuindo texto ao título correspondente

    # Salvando o dicionário em JSON com codificação UTF-8 para suportar caracteres especiais
    output_json_path = os.path.join(folder_path, "output_legislation_2.json")
    with open(output_json_path, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Substitua 'path_to_pdf_folder' pelo caminho do diretório dos seus PDFs
pdf_to_json('../input/Raw Text/Legislation/')
