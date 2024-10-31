import capturaDados as cd
import database as db

idMaquinaRecursoTotal = db.executarSelect(
        f"SELECT idMaquinaRecurso FROM MaquinaRecurso WHERE fkMaquina = 2 AND fkRecurso = 3;")

print(idMaquinaRecursoTotal)