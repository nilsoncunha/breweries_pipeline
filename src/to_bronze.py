import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--page_number", type=str)
args = parser.parse_args()

import boto3
import json
import os
import requests
import time
from utils import YAMLReader
from datetime import datetime

BASE_URL = os.getenv("URL_API")
BUCKET_BRONZE = os.getenv("BUCKET_BRONZE")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT_SPARK")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

yaml_file = YAMLReader('app/src/utils_config.yml').read()
per_page = yaml_file['quantity_per_page']
folder = yaml_file['folder']
file_name = yaml_file['file_name']

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)


def extract_data() -> None:
    page = int(args.page_number)
    qtd_for_sleep= 1

    # Como não conseguimos saber o número de páginas (pode aumentar ou reduzir) a ideia foi trazer o iterador
    # dando a liberdade de pegar todas as páginas que retornarem valor.
    while True:
        url = f"{BASE_URL}?per_page={per_page}&page={page}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            page_data = response.json()

            if not page_data:
                print(f"[INFO] Página {page} vazia.")
                break

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{folder}/{file_name}_{page}.json"

            s3.put_object(
                Bucket=f"{BUCKET_BRONZE}",
                Key=filename,
                Body=json.dumps(page_data, indent=2),
                ContentType="application/json"
            )

            print(f"[INFO] Página {page} salva em {BUCKET_BRONZE}/{filename}")
            page += 1

            # Criado uma pausa para não requisitar a API por muito tempo.
            qtd_for_sleep += 1
            if qtd_for_sleep % 10 == 0:
                time.sleep(1)

        except requests.RequestException as e:
            print(f"[ERROR] Falha na página {page}: {e}")
            break

if __name__ == "__main__":
    extract_data()