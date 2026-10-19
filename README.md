# Sistema de Gestión de Farmacia (Farmacia QCI)

Aplicación de escritorio para el control de una farmacia: inventario de
artículos, ventas con carrito y sistema de puntos, clientes, compras a
proveedores y usuarios con roles.

Construida con Python, `customtkinter` (interfaz) y MySQL
(`mysql-connector-python`).

## Módulos

| Módulo | Descripción |
|---|---|
| `app.py` | Login, menú superior y pestañas según el rol del usuario. |
| `conexion.py` | Conexión a MySQL (`ConexionDB`). |
| `DB/` | Acceso a datos, una clase por entidad. |
| `UI/` | Interfaces gráficas, una por módulo. |
| `bd_farmacia.sql` | Script de creación de la base de datos y datos de ejemplo. |

### Pestañas

- **Usuarios**: alta, edición y baja de usuarios (solo `admin`).
- **Clientes**: alta y edición de clientes, con puntos de fidelidad.
- **Ventas**: punto de venta con carrito, cálculo de puntos y canje de
  promociones por 50 puntos.
- **Detalle Ventas**: consulta de ventas y sus artículos (`admin` y `gerente`).
- **Artículos**: catálogo, precios y stock.
- **Almacén**: consulta y ajuste de inventario (`admin` y `gerente`).
- **Compras**: registro de compras a proveedores (`admin` y `gerente`).

## Roles

| Rol | Acceso |
|---|---|
| `admin` | Todos los módulos. |
| `gerente` | Clientes, ventas, detalle de ventas, artículos, almacén y compras. |
| `cajero` | Clientes, ventas y artículos. |

## Requisitos

- Python 3.10 o superior.
- MySQL 8 (o MariaDB compatible).
- Dependencias de `requirements.txt`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crear la base de datos e importar los datos de ejemplo:

```bash
mysql -u root -p < bd_farmacia.sql
```

El script crea la base `farmacia_qci`, que es la que usa la aplicación.
Si tu MySQL tiene contraseña, ajusta `conexion.py` (parámetros por defecto)
o `DB_CONFIG` en `app.py`.

## Ejecución

```bash
python app.py
```

### Cuentas de ejemplo

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `123` | admin |
| `gerente` | `123` | gerente |
| `cajero` | `123` | cajero |

## Estructura

```
Sistema_Gestion_Farmacia/
├── app.py              # Login y ventana principal
├── conexion.py         # Conexión a MySQL
├── bd_farmacia.sql     # Esquema y datos de ejemplo
├── DB/
│   ├── dbArticulos.py
│   ├── dbClientes.py
│   ├── dbCompras.py
│   ├── dbDetalleVentas.py   # stub no usado
│   ├── dbUsuario.py
│   └── dbVentas.py
└── UI/
    ├── almacen.py
    ├── articulos.py
    ├── clientes.py
    ├── compras.py
    ├── detalle_venta.py
    ├── usuarios.py
    └── ventas.py
```

## Limitaciones conocidas

- Las contraseñas de los usuarios se guardan en **texto plano** en la base de
  datos y se comparan directamente en el `SELECT` del login. No usar en
  producción sin migrar a un hash con sal (por ejemplo `bcrypt`).
- Las credenciales de MySQL están vacías por defecto en `conexion.py` y en
  `DB_CONFIG` de `app.py`; cámbialas según tu instalación.
- `actualizar_usuario` construye el `SET` de la consulta con las claves del
  diccionario recibido. Los valores van parametrizados, pero las claves no:
  solo deben provenir de campos controlados por la interfaz.
- `eliminar_usuario`, `eliminar_cliente` y `eliminar_articulo` borran el
  registro y **renumeran los IDs** de toda la tabla. Puede fallar si otras
  tablas referencian esos IDs y rompe las referencias existentes.
- `canjear_puntos` resta sin comprobar el saldo; si se canjean varias
  promociones con los mismos 50 puntos, el saldo puede quedar negativo.
- Al rechazar un canje de promoción, los puntos se reinician solo en la
  interfaz; el descuento real (50 puntos por promoción) se aplica al
  finalizar la venta.
- `DB/dbDetalleVentas.py` es un stub sin uso; el detalle real está en
  `DB/dbVentas.py` y `UI/detalle_venta.py`.
- No hay pruebas automatizadas; la verificación es manual con MySQL y GUI.

## Créditos

Desarrollo original: AlexSo11.
