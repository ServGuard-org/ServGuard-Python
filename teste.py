import capturaDados as cd

nome_computador = cd.capturaNomeComputador()
print(f"O nome do computador é: {nome_computador}")

discos = cd.capturaTodosDiscos()

print(f"Partições de disco: {discos}")
print(discos[1].mountpoint)
for disco in discos:
    uso_disco = cd.capturaUsoDisco(disco.mountpoint)
    print(f"Disco: {disco.device}")
    print(f"Total: {uso_disco['total']} GB")
    print(f"Usado: {uso_disco['usado']} GB")
    print(f"Livre: {uso_disco['livre']} GB")
    print(f"Percentual de uso: {uso_disco['percent']}%")
    print("-" * 50)