from pyspark.sql import SparkSession

if __name__ == '__main__':

    # cria sessão Spark
    spark = SparkSession.builder.appName("Streaming").getOrCreate()

    # cria schema de acordo com estrutura do arquivo de dados json
    schema = "nome STRING, postagem STRING, data INT"

    # cria df com dados do arquivo json
    df = spark.readStream.json("/home/rafael/download/streaming/monitoring", schema=schema)

    # local onde será salvo o estado do processo
    diretorio = "/home/rafael/download/streaming/output"

    # imprime os dados de processamento no console e gera estado do processo na pasta informada na variável diretorio
    stcalConsole = df.writeStream.format("console").outputMode("append").trigger(processingTime="5 second")\
        .option("checkpointlocation", diretorio).start()

    # estabelece conexão com BD para gravação dos dados de output após processamento do streaming
    def atualizaBD(dataframe, batchId):
        dataframe.write.format("jdbc").option("url", "jdbc:postgresql://localhost:5432/posts").option("dbtable", "posts")\
            .option("user", "postgres").option("password", "123456").option("driver", "org.postgresql.Driver").mode("append").save()

    stcalDB = df.writeStream.foreachBatch(atualizaBD).outputMode("append").trigger(processingTime="5 second")\
        .option("checkpointlocation", diretorio).start()

    # fica aguardando o término do processo por algum evento
    stcalConsole.awaitTermination()
    stcalDB.awaitTermination()