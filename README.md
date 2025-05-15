# Breweries Pipeline

Este projeto implementa um pipeline de dados com arquitetura **Medallion (Bronze, Silver, Gold)** 
utilizando **Apache Spark com Delta Lake**, **MinIO como data lake local (S3 compatível)** e **Apache Airflow** como 
orquestrador. Os dados são extraídos da API pública [Open Brewery DB](https://www.openbrewerydb.org/), transformados, 
particionados e agregados, prontos para análise.

---

## 🔧 Tecnologias Utilizadas

- 🐍 Python 3.10
- ⚙️ Apache Spark 3.5.3 + Delta Lake 3.3.1
- ☁️ MinIO (S3 compatível)
- 🌬️ Apache Airflow 2.8 com PostgreSQL
- 🐘 PostgreSQL 13
- 🐳 Docker e Docker Compose

---

## 🧩 Versões e Compatibilidade

| Componente       | Versão Utilizada  | Observações                                                                         |
|------------------|-------------------|-------------------------------------------------------------------------------------|
| **Apache Spark** | `3.5.3`           | Engine de processamento principal                                                   |
| **Scala**        | `2.12`            | Requisito de compatibilidade do Delta Lake                                          |
| **Delta Lake**   | `3.3.1`           | Compatível com Spark 3.5.3 (JARs: `delta-spark`, `delta-storage`, `delta-contribs`) |
| **Hadoop AWS**   | `3.3.5`           | Suporte ao `s3a://` com MinIO                                                       |
| **AWS SDK**      | `2.20.158`        | Requisição de objetos via boto3/spark                                               |
| **Airflow**      | `2.8.1`           | Com `LocalExecutor` e PostgreSQL                                                    |
| **PostgreSQL**   | `13`              | Backend do Airflow                                                                  |
| **MinIO**        | `latest`          | Buckets criados automaticamente via `mc`                                            |

---

### 📁 JARs utilizados

```Dockerfile
# Delta Lake
ADD https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.3.1/delta-spark_2.12-3.3.1.jar .
ADD https://repo1.maven.org/maven2/io/delta/delta-contribs_2.12/3.3.1/delta-contribs_2.12-3.3.1.jar .
ADD https://repo1.maven.org/maven2/io/delta/delta-storage/3.3.1/delta-storage-3.3.1.jar .

# Conexão com MinIO
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.5/hadoop-aws-3.3.5.jar .
ADD https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.20.158/bundle-2.20.158.jar .
```

---

## 📚 Arquitetura Medallion

- **Bronze**: Dados crus da API (1 arquivo por página), salvos no bucket `bronze` no formato JSON.
- **Silver**: Transformação e limpeza, salvos em Delta Lake particionado por `state`, no bucket `silver`.
- **Gold**: Agregação da contagem de cervejarias por `state` e `brewery_type`, também em Delta, no bucket `gold`.

---

## ⚙️ Parametrização com YAML

Aqui trouxe uma opção para deixar mais genérico o código e quando necessário realizar a alteração apenas no YAML
caso fosse necessário modificar o nome das pastas, quantidade por páginas ou o nome do arquivo.

---

## 🚀 Como Executar o Projeto

1. Clone o repositório
```bash
git clone https://github.com/nilsoncunha/breweries_pipeline.git
cd breweries_pipeline
```

2. O comando abaixo irá subir os containers com todos os serviços necessários para a execução do projeto. Inclusive a criação dos buckets no `MinIO`
**_Obs: Antes de executar o comando abaixo, verifique se há containers ativos nas portas necessárias para esse projeto_**

| Serviço       | Porta        |
|---------------|--------------|
| **minio**     | 9000 / 9001  |
| **postgres**  | 5432         |
| **airflow**   | 8080         |

```bash
docker-compose up -d --build
```

3. Quando finalizado, você conseguirá acessar o `Airflow` e o `MinIO` através dos links abaixo.

| Sistema           | URL                    | Credenciais      |
|-------------------|------------------------|------------------|
| **Airflow**       | http://localhost:8080  | admin / admin    |
| **MinIO Console** | http://localhost:9001  | minio / minio123 |

4. Ao acessar o `Airflow` habilite a dag e clique para realizar o `Trigger Dag`. O número de páginas já está configurado nos parâmetros.
Aqui quis demonstrar que poderíamos deixar um parâmetro para pegar a partir de uma página específica e facilitar futuramente um reprocessamento.
O código não está adaptado para pegar apenas uma página, mas sim do número da página informada até a API retornar vazia.

5. Ao realizar a `Trigger Dag` o processo durou cerca de `3 minutos` para completar.
 
## 🗂️ Estrutura do Projeto

```markdown
├── airflow/
│   └── dags/
│       └── breweries_dag.py           # DAG do Airflow com tasks bronze/silver/gold
├── src/
│   ├── to_bronze.py                   # Extração paginada da API + upload pro MinIO
│   ├── to_silver.py                   # Limpeza + Delta partitioned by state
│   ├── to_gold.py                     # Agregação Delta
│   |── utils.py
|   |── utils_config.yml               # Configurações do pipeline
├── .gitignore
├── docker-compose.yaml
│── Dockerfile                         # Spark + Delta configurado
├── README.md
└── requirements.txt
```

## 🛡️ Monitoramento e Alertas - Não implementada

Nesse caso poderia utilizar o `retries` e `retry_delay` (estão comentados no código) para em caso de falha rodar a task novamente.
Outro ponto seria a inclusão de alertas sendo enviado para o e-mail ou Slack para notificar as falhas e com isso 
analisarmos os logs que foram gerados pelo Airflow.
