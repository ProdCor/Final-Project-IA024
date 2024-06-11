import os
import json
from PyPDF2 import PdfReader

def pdf_to_json(folder_path):
    data = []
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
            data.append({
                "titulo": filename.replace('.pdf', ''),
                "texto": "\n".join(text_content)
            })

    # Usando a codificação UTF-8 ao salvar o arquivo para suportar caracteres especiais
    output_json_path = os.path.join(folder_path, "output_legislation.json")
    with open(output_json_path, "w", encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Substitua 'path_to_pdf_folder' pelo caminho do diretório dos seus PDFs
pdf_to_json('../input/Raw Text/Legislation/')


