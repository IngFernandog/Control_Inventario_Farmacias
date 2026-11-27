# Control_Inventario_Farmacias
Sistema en Python para controlar el inventario de medicamentos, consultar próximos vencimientos y gestionar solicitudes entre sedes de una red de farmacias.

## Estado del desarrollo

Implementadas las partes de Fernando y Harold: modelo del dominio, hash propio
por encadenamiento enlazado, AVL, BST iterativo de contraste, pruebas y operaciones
de EXP-01 y EXP-03. Se usa únicamente la biblioteca estándar de Python 3.10 o superior.

Los módulos de heap, cola, grafo, gestor, carga, menú y medidor general todavía
están pendientes. Los CSV actuales solo contienen encabezados. La aplicación
integral y las mediciones finales requieren esas partes.

## Ejecución de pruebas

Desde la raíz del repositorio:

```bash
python -m unittest discover -s tests -v
```

También se pueden ejecutar directamente `python tests/test_hash.py` y
`python tests/test_avl.py`. Los imports de los módulos propios usan el paquete
`src`, por ejemplo `from src.modelos import Lote`.

## Modelo y reglas de integración

```python
Medicamento(id_medicamento, denominacion)
Sede(id)
Lote(id_lote, id_medicamento, sede, vencimiento, cantidad, activo=True)
Movimiento(id_op, id_lote, delta, saldo_anterior, saldo_posterior)
Solicitud(id, sede, medicamento, cantidad, orden)
```

- Los IDs y textos se normalizan quitando espacios exteriores; no se aceptan vacíos.
- `vencimiento` es `datetime.date`; la carga convierte el texto AAAA-MM-DD.
- El lote conserva fijos ID, medicamento, sede y vencimiento. Sus setters validan
  cantidad entera no negativa y estado booleano. `True` no es una cantidad válida.
- Medicamento, sede, solicitud y movimiento son registros inmutables.
- El gestor valida las referencias a medicamentos y sedes existentes, los IDs
  repetidos, las salidas y la coherencia entre índices antes de aplicar cambios.
- Los intentos inválidos se registran en la bitácora del gestor. `Movimiento`
  representa exclusivamente una operación aplicada y sus saldos coherentes.
- El gestor asigna y conserva la secuencia original de alta para el heap. Esta
  secuencia no es el ID del lote ni el orden de la solicitud.
- Hash, AVL y heap deben almacenar el mismo objeto `Lote`. El gestor es la capa
  responsable de modificar cantidad/estado y asegurar la presencia en el heap
  cuando repone o reactiva un lote elegible.
- Las alertas se calculan para pares medicamento-sede con lotes registrados,
  incluidos agotados e inactivos, sumando solo cantidades de lotes activos.
- Atender una solicitud FIFO no modifica el inventario automáticamente; la salida
  se registra como una operación explícita.

## Hash de medicamentos y lotes

`HashMedicamentos[T]` usa cubetas con nodos enlazados y función hash polinómica
determinista. Rechaza duplicados con `ValueError`, sin cambiar el registro original.
`buscar(id)` devuelve el objeto canónico o `None`. No admite `None` como registro.
Crece al superar carga 0.75; conserva identidad y cantidad durante el rehashing.

```python
from datetime import date
from src.modelos import Medicamento, Lote
from src.hash import HashMedicamentos
from src.avl import ArbolLotes

medicamentos = HashMedicamentos[Medicamento]()
lotes = HashMedicamentos[Lote]()
arbol = ArbolLotes()
medicamentos.insertar("M1", Medicamento("M1", "Medicamento simulado"))
lote = Lote("L1", "M1", "A", date(2027, 1, 10), 5)
lotes.insertar(lote.id_lote, lote)
arbol.insertar(lote)
assert arbol.buscar(lote.clave) is lotes.buscar("L1")
```

## AVL de lotes

`ArbolLotes.insertar(lote)` ordena por `(lote.vencimiento, lote.id_lote)` y rechaza
claves duplicadas. La unicidad global del ID se controla primero en el hash del
gestor. `buscar((fecha, id))` devuelve el mismo lote o `None`; `en_orden()` devuelve
todos los lotes, incluidos los agotados/inactivos, que conservan su posición.
`validar_balance()` comprueba orden global, alturas reales y factores de balance.

Ambos árboles experimentales usan altura 0 para vacío y 1 para una hoja.
El AVL inserta y busca en O(log n), lista en O(n) y ocupa O(n) memoria.
El hash tiene búsqueda esperada O(1), peor caso O(n) y memoria O(m+n).

## Contrato de los experimentos

`experimentos/comparar_hash.py` expone:

- `construir_hash(medicamentos)` y `construir_lista(medicamentos)` para preparar índices.
- `buscar_hash(indice, ids)` y `buscar_lista(lista, ids)` para medir consultas
  equivalentes, presentes y ausentes, en el mismo orden. Devuelven los mismos objetos.
- La tabla experimental usa capacidad `2*n+1`, con carga próxima a 0.5. Registrar
  capacidad, cantidad y factor de carga para cada tamaño; separar carga y búsqueda.

`experimentos/comparar_avl.py` expone `construir_avl(lotes)` y `construir_bst(lotes)`.
Ambas devuelven un árbol con `altura`, `buscar(clave)` y `en_orden()`.
`BSTLotes` usa ciclos en inserción, búsqueda, inorden y altura, sin modificar el
límite de recursión. Sus entradas ordenadas forman una cadena y su construcción
cuesta O(n²). El AVL utiliza balanceo y puede usar recursividad.

Ejemplo de comprobación previo a la medición:

```python
from datetime import date, timedelta
from src.modelos import Lote
from experimentos.comparar_avl import construir_avl, construir_bst

lotes = [Lote(f"L{i:05d}", "M1", "A", date(2027, 1, 1) + timedelta(days=i), 5)
         for i in range(100)]
avl = construir_avl(lotes)
bst = construir_bst(lotes)
assert avl.en_orden() == bst.en_orden()
assert avl.validar_balance()
assert bst.altura == 100
```

Fernandito integra estas operaciones en `experimentos/medir.py`: datos de
100/1 000/10 000, calentamiento y al menos diez repeticiones por variante,
`perf_counter`, pasadas separadas de `tracemalloc`, mediana y dispersión.
Preparar las entradas fuera del cronómetro y crear estructuras nuevas por
repetición. Consultar alturas/inórdenes fuera del tiempo de construcción.
Conservar resultados crudos y metadatos del entorno; evitar medir impresión o
generación de datos. Los ejemplos anteriores verifican comportamiento, no son
resultados de rendimiento.

## Distribución de responsabilidades

| Autor | Archivos de código |
| --- | --- |
| Fernando | `src/modelos.py`, `src/hash.py`, `tests/test_hash.py`, `experimentos/comparar_hash.py` y README |
| Harold | `src/avl.py`, `tests/test_avl.py`, `experimentos/comparar_avl.py` |
| Inmundo | `src/heap.py`, `tests/test_heap.py`, `experimentos/comparar_heap.py` |
| Marciano | `src/cola.py`, `src/grafo.py`, `tests/test_red_cola.py` |
| Garrido | `src/gestor.py`, `tests/test_gestor.py` |
| Fernandito | `main.py`, `src/datos.py`, `tests/test_consola.py`, `experimentos/medir.py` y CSV |

Marciano explica teóricamente lista/matriz del grafo. Se mantienen los tres
experimentos principales del contrato. Informe, presentación, acta y fichas de
evidencia se completan con resultados reales conforme al reparto del equipo.
