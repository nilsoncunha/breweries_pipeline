FROM bitnami/spark:3.5.3

USER root

ADD requirements.txt .
ADD Dockerfile .

# Instala bibliotecas Python
RUN pip install --upgrade pip \
    && pip install -r ./requirements.txt

# Define diretório de trabalho para os JARs
WORKDIR /opt/bitnami/spark/jars

# Delta Lake 3.0.0 compatível com Spark 3.5 e Scala 2.12
ADD https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.3.1/delta-spark_2.12-3.3.1.jar .
ADD https://repo1.maven.org/maven2/io/delta/delta-contribs_2.12/3.3.1/delta-contribs_2.12-3.3.1.jar .
ADD https://repo1.maven.org/maven2/io/delta/delta-storage/3.3.1/delta-storage-3.3.1.jar .

# Hadoop AWS + AWS SDK
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.5/hadoop-aws-3.3.5.jar .
ADD https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.20.158/bundle-2.20.158.jar .

# Retorna para o diretório do Spark
WORKDIR /opt/bitnami/spark