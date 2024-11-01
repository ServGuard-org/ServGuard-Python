import speedtest
import threading

# Função para medir o download e armazenar no dicionário
def medir_download(resultados):
    st = speedtest.Speedtest()
    download_speed = st.download() / 10**6  # Convertendo para Mbps
    resultados["download"] = download_speed

# Função para medir o upload e armazenar no dicionário
def medir_upload(resultados):
    st = speedtest.Speedtest()
    upload_speed = st.upload() / 10**6  # Convertendo para Mbps
    resultados["upload"] = upload_speed

# Dicionário local para armazenar os resultados
resultados = {}

# Criação das threads, passando o dicionário como argumento
thread_download = threading.Thread(target=medir_download, args=(resultados,))
thread_upload = threading.Thread(target=medir_upload, args=(resultados,))

# Iniciar as threads
thread_download.start()
thread_upload.start()

# Aguardar ambas as threads terminarem
thread_download.join()
thread_upload.join()

# Imprimir o dicionário com os resultados
print(resultados)
