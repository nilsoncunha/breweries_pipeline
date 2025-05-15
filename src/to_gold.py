import os
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from utils import YAMLReader

builder = (
    SparkSession.builder
    .appName("to_gold")
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

BUCKET_SILVER = os.getenv("BUCKET_SILVER")
BUCKET_GOLD = os.getenv("BUCKET_GOLD")

yaml_file = YAMLReader('app/src/utils_config.yml').read()
folder = yaml_file['folder']

# Ler Silver
df = (
    spark.read
    .format("delta")
    .load(f"s3a://{BUCKET_SILVER}/{folder}")
)

# Agregação
agg = (
    df.groupBy("state", "brewery_type")
    .count()
    .withColumnRenamed("count", "brewery_count")
)

# Salvar Gold
# Aqui foi realizado o coalesce para evitar a criação de pequenos arquivos.
(
    agg.coalesce(1).write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .save(f"s3a://{BUCKET_GOLD}/{folder}")
)

print("\n[INFO] Save data in Gold layer")
spark.stop()
