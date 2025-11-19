# Traducción dirigida por sintaxis — Ejemplo en Python

## Descripción breve
En este repositorio se entrega un ejemplo práctico en **Python** que implementa una ETDS (Esquema de Traducción Dirigida por Sintaxis), una **tabla de símbolos** con manejo de ámbitos y un **generador de código en tres direcciones (TAC)** que representa el AST de declaraciones/definiciones (AST_D).

En este caso lo que se hizo fue:
- Definir una gramática simple (tipos básicos, declaraciones de variables, definiciones de funciones, asignaciones, retornos y expresiones aritméticas).
- Implementar el lexer y parser con **PLY** (lex/yacc para Python).
- Integrar acciones semánticas en las producciones para construir el AST y poblar la tabla de símbolos.
- Generar código intermedio (TAC) recorriendo el AST y produciendo quads `(op, arg1, arg2, res)`.

## Archivos incluidos
- `sdt_tac.py` — Código fuente principal. Aquí es donde **acá lo que hacemos es que** se define el AST, la tabla de símbolos y el generador TAC.
- `README.md` — Este archivo con instrucciones y explicación.

## Cómo usarlo
1. Clonar este repositorio o descargar los archivos.
2. Instalar la dependencia:
```bash
pip install ply
```
3. Ejecutar el ejemplo:
```bash
python sdt_tac.py
```

Por esta razón verás en la salida:
- La impresión de la tabla de símbolos (scopes con variables y funciones).
- Los quads generados (TAC) para las funciones definidas.

## Notas sobre la ETDS y la tabla de símbolos
- La ETDS está implementada como acciones en las reglas del parser: cuando se reconoce una `var_decl` se inserta en la tabla de símbolos; cuando se reconoce una `func_decl` se crea la entrada de función y se abre un nuevo ámbito para parámetros y variables locales.
- La tabla de símbolos usa una pila de scopes. Esto quiere decir que al entrar en una función se crea un nuevo scope y al salir se elimina. Esto permite manejar variables locales y parámetros sin colisiones con el scope global.
- En este ejemplo los offsets se asignan incrementalmente por inserción (útil si luego se quiere mapear a un registro o frame pointer).

## Limitaciones y mejoras posibles
- Las llamadas a funciones y el paso de parámetros están simplificados: no generan quads de `call`, ni manejo de records de activación. Si quieres, puedo ampliar el generador para:
  - emitir `param`/`call`/`ret` y manejar temporales para valores de retorno,
  - generar offsets relativos a `fp` para acceso a variables,
  - realizar chequeo de tipos estricto,
  - o adaptar exactamente la gramática de tu repositorio.
- El manejo de errores y tipos es básico; en un compilador real se agregarían más comprobaciones y mejores mensajes.

## Ejemplo rápido (lo que hace el ejemplo)
En el script `sdt_tac.py` hay un `sample` con dos funciones: `add` y `main`. Al ejecutar, **en este caso lo que se hizo fue** parsear ese texto, construir el AST, poblar la tabla de símbolos y producir TAC.

## Licencia
Código de ejemplo — úsalo y adáptalo. Si lo subes a GitHub, puedes cambiar la licencia según prefieras.

---

Si quieres, preparo el repositorio ya con:
- más tests,
- integración con `setup.py` o `pyproject.toml`,
- ejemplos de entrada/salida,
- o adaptar todo exactamente a la gramática del repositorio que mencionaste.
