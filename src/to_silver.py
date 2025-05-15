import os
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from utils import YAMLReader

builder = (
    SparkSession.builder
    .appName("to_silver")
    .config("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT_SPARK"))
    .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY"))
    .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY"))
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.debug.maxToStringFields", "200")
)

spark = configure_spark_with_delta_pip(builder).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

BUCKET_BRONZE = os.getenv("BUCKET_BRONZE")
BUCKET_SILVER = os.getenv("BUCKET_SILVER")

yaml_file = YAMLReader('app/src/utils_config.yml').read()
folder = yaml_file['folder']

# Caminho para os arquivos JSON (bronze)
bronze_path =  f"s3a://{BUCKET_BRONZE}/{folder}/*.json"

# Ler todos os arquivos de página
df = (
    spark.read
    .option("multiline", "true")
    .json(bronze_path)
)

# Salvar em formato Delta particionado por estado
# Aqui foi realizado o coalesce para evitar a criação de pequenos arquivos.
silver_output = f"s3a://{BUCKET_SILVER}/{folder}"
df.coalesce(1).write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("state") \
    .save(silver_output)

print("\n[INFO] Save data in Silver layer")

spark.stop()
