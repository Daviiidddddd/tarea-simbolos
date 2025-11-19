# Traducción dirigida por sintaxis — David Castellanos

## Descripción breve
En este repositorio se entrega un ejemplo práctico en **Python** que implementa una ETDS (Esquema de Traducción Dirigida por Sintaxis), una **tabla de símbolos** con manejo de ámbitos y un **generador de código en tres direcciones (TAC)** que representa el AST de declaraciones/definiciones (AST_D).

En este caso lo que se hizo fue;
- Definir una gramática simple (tipos básicos, declaraciones de variables, definiciones de funciones, asignaciones, retornos y expresiones aritméticas).
- Implementar el lexer y parser con **PLY** (lex/yacc para Python).
- Integrar acciones semánticas en las producciones para construir el AST y poblar la tabla de símbolos.
- Generar código intermedio (TAC) recorriendo el AST y produciendo quads `(op, arg1, arg2, res)`.

## Archivos includios
- `sdt_tac.py` — Código fuente principal. Aquí es donde **acá lo que hacemos es que** se define el AST, la tabla de símbolos y el generador TAC.
- `README.md` — Este archivo con instrucciones y explicación.



Por esta razón se ve en la salida:
- La impresión de la tabla de símbolos (scopes con variables y funciones).
- Los quads generados (TAC) para las funciones definidas.

## Notas sobre la ETS y la tabla de símbolos
- La ETDS está implementada como acciones en las reglas del parser: cuando se reconoce una `var_decl` se inserta en la tabla de símbolos; cuando se reconoce una `func_decl` se crea la entrada de función y se abre un nuevo ámbito para parámetros y variables locales.
- La tabla de símbolos usa una pila de scopes. Esto quiere decir que al entrar en una función se crea un nuevo scope y al salir se elimina. Esto permite manejar variables locales y parámetros sin colisiones con el scope global.
- En este ejemplo los offsets se asignan incrementalmente por inserción (útil si luego se quiere mapear a un registro o frame pointer).

## Cosas q deberiamos tener en cuenta
- Las llamadas a funciones y el paso de parámetros están simplificados: no generan quads de `call`, ni manejo de records de activación. Si quieres, puedo ampliar el generador para:
  - emitir `param`/`call`/`ret` y manejar temporales para valores de retorno,


## Que hace basicamente
En el script `sdt_tac.py` hay un `sample` con dos funciones: `add` y `main`. Al ejecutar, **en este caso lo que se hizo fue** parsear ese texto, construir el AST, poblar la tabla de símbolos y producir TAC.

## Fin
