import database as db
import capturaDados as cd
import slackWebhook as sentinel
import os
import time
from dotenv import load_dotenv, set_key

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
# Setando globalmente o caminho até o arquivo .env e,
# A chave para buscar o id da empresa dona desta máquina:
caminho_env = '.env'
chave_empresa = 'ID_EMPRESA'

def main():

    print("""
  █████████                                   █████████                                     █████
 ███░░░░░███                                 ███░░░░░███                                   ░░███ 
░███    ░░░   ██████  ████████  █████ █████ ███     ░░░  █████ ████  ██████   ████████   ███████ 
░░█████████  ███░░███░░███░░███░░███ ░░███ ░███         ░░███ ░███  ░░░░░███ ░░███░░███ ███░░███ 
 ░░░░░░░░███░███████  ░███ ░░░  ░███  ░███ ░███    █████ ░███ ░███   ███████  ░███ ░░░ ░███ ░███ 
 ███    ░███░███░░░   ░███      ░░███ ███  ░░███  ░░███  ░███ ░███  ███░░███  ░███     ░███ ░███ 
░░█████████ ░░██████  █████      ░░█████    ░░█████████  ░░████████░░████████ █████    ░░████████
 ░░░░░░░░░   ░░░░░░  ░░░░░        ░░░░░      ░░░░░░░░░    ░░░░░░░░  ░░░░░░░░ ░░░░░      ░░░░░░░░ 
    """)
    time.sleep(2.5)
    # Buscando o ID da empresa no .env
    idEmpresa = os.getenv(chave_empresa)

    # Se não houver ID no .env, executa a configuração inicial
    if idEmpresa is None:
        mac = cd.capturaMAC()
        # Verifica se a máquina já está cadastrada no banco de dados
        # existe recebe o valor de uma expressão booleana, algo como:
        # "O tamanho do retorno deste select é maior que 0?", ou então:
        # "Esta máquina com esse MACAddress? existe no banco de dados?"
        existe = len(db.executarSelect(f"SELECT * FROM Maquina WHERE MACAddress = '{mac}';")) > 0

        if not existe:
            # Configuração inicial, obtém e seta ID da empresa no .env e cadastra a máquina
            setupInicial(mac)
            capturarDados(idEmpresa, mac)
        elif existe:
            # Caso a máquina exista no BD,
            idEmpresa = db.executarSelect(f"SELECT fkEmpresa FROM Maquina WHERE MACAddress = '{mac}';")[0][0]
            # Pega o id da empresa dona,
            # seta o id da empresa no .env
            set_key(caminho_env, chave_empresa, str(idEmpresa))
            # e, inicia a captura de dados
            capturarDados(idEmpresa, mac)
    elif idEmpresa.isdigit():
        # caso exista e for um número mesmo,
        # captura o MAC Address
        mac = cd.capturaMAC()

        existe = len(db.executarSelect(f"SELECT * FROM Maquina WHERE MACAddress = '{mac}';")) > 0
        if existe:
             # e, inicia a captura de dados
            capturarDados(idEmpresa, mac)
        elif not existe:
            cadastrarMaquina(idEmpresa, mac)
            capturarDados(idEmpresa, mac)


def setupInicial(mac):
    # Função que faz o setup inicial da máquina:
    print('''Olá! Parece que essa Máquina ainda não está cadastrada...
          Faremos a configuração inicial agora...''')

    idEmpresa = None

    # Loop até que um ID de empresa válido seja fornecido
    while True:
        idEmpresa = input("Informe o id da empresa dona desta máquina: ")

        # Verificar se o ID fornecido é numérico
        if not idEmpresa.isdigit():
            print("Por favor, insira um número válido.")
            continue

        # Verificar se o ID existe no banco de dados
        empresa = db.executarSelect(f"SELECT * FROM Empresa WHERE idEmpresa = {idEmpresa};")
        if len(empresa) > 0:
            resposta = input(f"\033[3mEmpresa: {empresa[0][1]} \033[0mlocalizada. Deseja prosseguir? [S/N]: ")
            if resposta.upper() == "S":
                print(f"\033[3mVinculando com a empresa {empresa[0][1]}...\033[0m")
                cadastrarMaquina(idEmpresa, mac)
                break
            elif resposta.upper() == "N":
                print("...")
                continue
            else:
                print("Insira uma resposta válida...")
                continue
        else:
            print("ID não encontrado na nossa base de dados! Tente novamente.")

    # Salvar o ID da empresa no arquivo .env
    # "str(idEmpresa)" garante que é uma string para colocar no .env, para evitar erros.
    set_key(caminho_env, chave_empresa, str(idEmpresa))

def cadastrarMaquina(idEmpresa, mac):
    # Capturando informações da máquina
    modeloCPU = cd.capturaModeloCPU()
    qtdNucleosFisicos = cd.capturaQtdNucleos(logicos=False)
    qtdNucleosLogicos = cd.capturaQtdNucleos(logicos=True)
    capacidadeRAM = cd.capturaQtdRAM()
    nomeMaquina = cd.capturaNomeComputador()

    # Executando a inserção da máquina no banco de dados
    query = f"""
        INSERT INTO Maquina 
        (nome, fkEmpresa, modeloCPU, qtdNucleosFisicos, qtdNucleosLogicos, capacidadeRAM, MACAddress)
        VALUES ('{nomeMaquina}', {idEmpresa}, '{modeloCPU}', {qtdNucleosFisicos}, {qtdNucleosLogicos}, {capacidadeRAM}, '{mac}');
        """
    db.executarQuery(query)
    # Chama a função que inscreve a máquina nas capturas
    inscreverCapturas(mac)

def inscreverCapturas(mac):
    print("Inscrevendo máquina nos monitoramentos de: CPU, RAM, Disco (Usado), Disco (Livre)...")

    # Obtendo o id de recurso para cada um dos recursos que monitoramos:
    idRecursoCPU = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'usoCPU';")[0][0]
    idRecursoRAM = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'usoRAM';")[0][0]
    idRecursoerroPCTEnt = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'erroPacotesEntrada';")[0][0]
    idRecursoerroPCTSaida = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'erroPacotesSaida';")[0][0]
    idRecursoDescartePCTEnt = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'descartePacotesEntrada';")[0][0]
    idRecursoDescartePCTSaida = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'descartePacotesSaida';")[0][0]
    idRecursoMBRecebidos = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'megabytesRecebidos';")[0][0]
    idRecursoMBEnviados = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'megabytesEnviados';")[0][0]
    idRecursoPCTEnviados = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'pacotesEnviados';")[0][0]
    idRecursoPCTRecebidos = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'pacotesRecebidos';")[0][0]

    # Setando uma lista para fazer de forma mais rápida a inscrição
    listaRecursos = [idRecursoCPU, idRecursoRAM, idRecursoerroPCTEnt, idRecursoerroPCTSaida, idRecursoDescartePCTEnt, idRecursoDescartePCTSaida, idRecursoMBRecebidos, idRecursoMBEnviados, idRecursoPCTEnviados, idRecursoPCTRecebidos]

    # obtendo o id da máquina através do MAC Address
    idMaquina = db.executarSelect(f"SELECT idMaquina FROM Maquina WHERE MACAddress = '{mac}'")[0][0]

    # Inserindo a inscrição da máquina para capturar cada recurso
    for recurso in listaRecursos:
        query = f"INSERT INTO MaquinaRecurso (fkMaquina, fkRecurso) VALUES ({idMaquina}, {recurso})"
        db.executarQuery(query)

    discos = cd.capturaTodosDiscos()
    for disco in discos:
        pontoMontagem = disco.mountpoint
        usoDisco = cd.capturaUsoDisco(pontoMontagem)
        query = None
        if os.name == 'nt':
            query = f"INSERT INTO Volume (fkMaquina, pontoMontagem, capacidade) VALUES ({idMaquina}, '{disco.mountpoint}\\', {usoDisco['total']})"
        elif os.name == 'posix':
            query = f"INSERT INTO Volume (fkMaquina, pontoMontagem, capacidade) VALUES ({idMaquina}, '{disco.mountpoint}', {usoDisco['total']})"
        if query:
            db.executarQuery(query)

def capturarDados(idEmpresa, mac):
    # Função principal do sistema, captura de dados

    # Obtendo o id de recurso de cada componente
    idRecursoCPU = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'usoCPU';")[0][0]
    idRecursoRAM = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'usoRAM';")[0][0]
    idRecursoDescartePCTEnt = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'descartePacotesEntrada';")[0][0]
    idRecursoDescartePCTSai = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'descartePacotesSaida';")[0][0]
    idRecursoerroPCTEnt = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'erroPacotesEntrada';")[0][0]
    idRecursoerroPCTSai = db.executarSelect("SELECT idRecurso FROM Recurso WHERE nome = 'erroPacotesSaida';")[0][0]


    # Obtendo o id da máquina no BD
    idMaquina = db.executarSelect(f"SELECT idMaquina FROM Maquina WHERE MACAddress = '{mac}';")[0][0]

    # Verificando se max existe antes de acessar
    # Uma vez que o máximo de cada recurso deve ser definido pelo usuário via dashboard
    maxCPU = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoCPU}")
    maxCPU = maxCPU[0][0] if maxCPU else None  # Usando None se não houver resultado

    maxRAM = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoRAM}")
    maxRAM = maxRAM[0][0] if maxRAM else None

    maxDescaPCTEnt = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoDescartePCTEnt}")
    maxDescaPCTEnt = maxDescaPCTEnt[0][0] if maxDescaPCTEnt else None

    maxDescaPCTSai = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoDescartePCTSai}")
    maxDescaPCTSai = maxDescaPCTSai[0][0] if maxDescaPCTSai else None

    maxerroPCTEnt = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoerroPCTEnt}")
    maxerroPCTEnt = maxerroPCTEnt[0][0] if maxerroPCTEnt else None

    maxerroPCTSai = db.executarSelect(f"SELECT max FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoerroPCTSai}")
    maxerroPCTSai = maxerroPCTSai[0][0] if maxerroPCTSai else None

    # Obtendo os ids de relacionamento da máquina com cada recurso, para usar mais a frente
    idMaquinaRecursoCPU = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoCPU};")[0][0]
    idMaquinaRecursoRAM = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoRAM};")[0][0]
    idMaquinaRecursoDescartePCTEnt = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoDescartePCTEnt};")[0][0]
    idMaquinaRecursoDescartePCTSai = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoDescartePCTSai};")[0][0]
    idMaquinaRecursoerroPCTEnt = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoerroPCTEnt};")[0][0]
    idMaquinaRecursoerroPCTSai = db.executarSelect(f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = {idMaquina} AND fkRecurso = {idRecursoerroPCTSai};")[0][0]

    # Capturando todos os discos da máquina
    discos = cd.capturaTodosDiscos()

    # Contador para diferenciar a captura de disco
    counter = 0

    nomeMaquina = db.executarSelect(f"SELECT nome FROM Maquina WHERE idMaquina = {idMaquina};")[0][0]

    while True:
        usoCPU = cd.capturaUsoCPU()
        isAlertaCPU = 00
        if maxCPU:
            if usoCPU >= maxCPU:
                print(f"ALERTA!!!!!!!! USO CPU CHEGOU A: {usoCPU}")
                isAlertaCPU = 1
                print(sentinel.enviar(f"*Alerta!* :rotating_light: \n\n Uso de CPU da máquina:\n- id: *_{idMaquina}_* \n- Hostname: *_{nomeMaquina}_* \nChegou a: *_{usoCPU}%_*"))
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro, isAlerta) VALUES ({idMaquinaRecursoCPU}, {usoCPU}, {isAlertaCPU});"
        db.executarQuery(query)

        usoRAM = cd.capturaUsoRAM()
        isAlertaRAM = 0
        if maxRAM:
            if usoRAM >= maxRAM:
                print(f"ALERTA!!!!!!!! USO RAM CHEGOU A: {usoRAM}")
                print(sentinel.enviar(f"*Alerta!* :rotating_light: \n\n Uso de RAM da máquina:\n- id: *_{idMaquina}_* \n- Hostname: *_{nomeMaquina}_* \nChegou a: *_{usoRAM}%_*"))
                isAlertaRAM = 1
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro, isAlerta) VALUES ({idMaquinaRecursoRAM}, {usoRAM}, {isAlertaRAM});"
        db.executarQuery(query)

        # Capturando descarte de pacotes
        descarteEnt = cd.capturaDescarteEnt()
        descarteSai = cd.capturaDescarteSai()
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro) VALUES ({idMaquinaRecursoDescartePCTEnt}, {descarteEnt});"
        db.executarQuery(query)
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro) VALUES ({idMaquinaRecursoDescartePCTSai}, {descarteSai});"
        db.executarQuery(query)

        # Capturando erro de pacotes
        erroEnt = cd.capturaErrEnt()
        erroSai = cd.capturaErrSai()
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro) VALUES ({idMaquinaRecursoerroPCTEnt}, {erroEnt});"
        db.executarQuery(query)
        query = f"INSERT INTO Captura (fkMaquinaRecurso, registro) VALUES ({idMaquinaRecursoerroPCTSai}, {erroSai});"
        db.executarQuery(query)

        # Só insere novos dados de disco caso seja a primeira vez desde que o sistema foi iniciado OU
        # Se o resto de contador / 60 for 0, ou seja,
        # dado um time.sleep de 30s, isso é:
        # monitoramento a cada 30 minutos
        if counter == 0 or counter % 60 == 0:
            for disco in discos:

                pontoMontagem = disco.mountpoint
                dadosDisco = cd.capturaUsoDisco(pontoMontagem)
                usadoDisco = dadosDisco['usado']

                idDisco = None
                if os.name == 'nt':
                    query = f"SELECT idVolume FROM Volume WHERE fkMaquina = {idMaquina} AND pontoMontagem = '{pontoMontagem}\\';"
                elif os.name == 'posix':
                    query = f"SELECT idVolume FROM Volume WHERE fkMaquina = {idMaquina} AND pontoMontagem = '{pontoMontagem}';"
                idDisco = db.executarSelect(query)[0][0]

                # Inserindo uso de disco usado
                query = f"INSERT INTO CapturaVolume (fkVolume, usado) VALUES ({idDisco}, {usadoDisco})"
                db.executarQuery(query)

        counter += 1

        # Pausa por 30 segundos
        time.sleep(30)


if __name__ == "__main__":
    main()
