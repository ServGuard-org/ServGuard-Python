import speedtest

def testar_velocidade():
    st = speedtest.Speedtest()
    st.download()
    st.upload()

    download_speed = st.results.download / 10**6  # em Mbps
    upload_speed = st.results.upload / 10**6  # em Mbps

    print(f"Velocidade de Download: {download_speed:.2f} Mbps")
    print(f"Velocidade de Upload: {upload_speed:.2f} Mbps")

testar_velocidade()
