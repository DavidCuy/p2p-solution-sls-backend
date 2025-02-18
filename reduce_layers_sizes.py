from pathlib import Path
from shutil import rmtree

work_path = Path(r".")

for path in work_path.glob("**/*-info/"):
    if path.is_dir():
        rmtree(path)

# si descomenta el siguente codigo considere lo siguiente
# La carpeta "pycache" en Python se utiliza para almacenar archivos de caché de bytecode compilados para
# mejorar el rendimiento de la ejecución de los módulos de Python. Estos archivos de caché
# contienen el bytecode de los módulos compilados previamente y se utilizan para evitar la recompilación
# cada vez que se ejecuta el código. Esto mejora la velocidad de importación de módulos y la eficiencia
# de la ejecución del programa en general. Los archivos en la carpeta "pycache" se generan automáticamente y normalmente
# no se deben editar o eliminar manualmente.
