# Crownhold en español 🇪🇸

Traducción al español, hecha por la comunidad, de **[Crownhold](https://store.steampowered.com/app/4579940/Crownhold/)**, el juego incremental de Tobias Mikula, que oficialmente viene solo en inglés y alemán.

- Traduce los **1568 textos** del juego: menús, mejoras, tutoriales, eventos y diálogos.
- Agrega **Español como un idioma más**. El inglés y el alemán quedan intactos.
- Logros de Steam, Steam Cloud y partidas guardadas siguen funcionando igual.
- Probado con la versión **1.0.6** del juego, jugando una partida completa.

> ⚠️ Es un mod **no oficial**. No tiene relación con el desarrollador. Este repo **no incluye archivos del juego**: el script arma la versión traducida a partir de *tu* copia instalada.

---

## Instalación (Windows)

### 1. Instalá Python (si no lo tenés)
Descargalo de <https://www.python.org/downloads/>. Durante la instalación, **marcá la casilla "Add Python to PATH"**.

### 2. Descargá el mod
Arriba en esta página: botón verde **Code → Download ZIP**.

### 3. Copialo en la carpeta del juego
1. En Steam: clic derecho en **Crownhold → Administrar → Explorar archivos locales**.
2. Descomprimí el ZIP ahí adentro y renombrá la carpeta a **`mod_es`**.

Tiene que quedar así:
```
Crownhold\
├── Crownhold.exe
├── ...
└── mod_es\
    ├── instalar.bat
    ├── desinstalar.bat
    ├── crear_mod_es.py
    ├── mod_espanol.gd
    └── es_map.json
```

### 4. Instalá la traducción
Con el juego **cerrado**, hacé doble clic en **`mod_es\instalar.bat`**. Tarda unos segundos.

Antes de tocar nada, el script guarda una copia del juego original en `mod_es\Crownhold.original.exe`.

### 5. Elegí el idioma
Abrí el juego normalmente desde Steam y elegí **Español** en **Ajustes → Idioma**. Aparece como tercera opción, debajo de inglés y alemán.

> No hace falta poner nada en las "Opciones de lanzamiento" de Steam.

---

## Cuando el juego se actualiza
Las actualizaciones de Steam reemplazan `Crownhold.exe`, así que el juego vuelve a quedar solo en inglés y alemán. **Volvé a hacer doble clic en `instalar.bat`**: detecta la versión nueva, actualiza la copia de seguridad y vuelve a aplicar la traducción.

Si la actualización trae textos nuevos que todavía no están traducidos, aparecen en inglés y el script los lista en `sin_traducir.csv`.

## Desinstalar
Hay dos formas:
- Doble clic en **`mod_es\desinstalar.bat`**: restaura el `Crownhold.exe` original.
- En Steam: **Propiedades → Archivos instalados → Verificar integridad de los archivos del juego**.

Después podés borrar la carpeta `mod_es`.

## Problemas comunes

| Problema | Solución |
|---|---|
| `instalar.bat` dice que no encuentra Python | Reinstalá Python marcando "Add Python to PATH" y reiniciá la PC. |
| Dice que no encuentra `Crownhold.exe` | La carpeta `mod_es` tiene que estar **dentro** de la carpeta del juego, al lado de `Crownhold.exe`. |
| "No se pudo reemplazar Crownhold.exe" | Cerrá el juego y volvé a correr `instalar.bat`. |
| No aparece "Español" en el menú | Seguramente el juego se actualizó o Steam verificó los archivos. Volvé a correr `instalar.bat`. |
| Tenía puesto `--main-pack` en Opciones de lanzamiento (versión vieja del mod) | Borralo: este juego no acepta ese parámetro y no abre si está puesto. |

---

## Corregir o mejorar la traducción
Todos los textos están en **`es_map.json`**, con el formato `"texto original en inglés": "traducción"`.

1. Editá la traducción (dejá igual el texto en inglés de la izquierda).
2. Respetá exactamente lo que está entre llaves `{así}`, los códigos como `%d` y las etiquetas `[color=...]`, `[b]`, etc.
3. Las líneas con varias palabras separadas por `|` son listas de términos que el juego resalta en los textos. Mantené la misma cantidad de elementos y usá las mismas palabras que en las traducciones.
4. Volvé a correr `instalar.bat` para probar.

Los *Pull Requests* con correcciones son bienvenidos. Si encontrás un error y no querés editar, abrí un **Issue** con una captura.

**Glosario usado** (para mantener coherencia): Longbowmen → Arqueros · Swordsmen → Espadachines · Militia → Milicia · Breachers → Zapadores · Vanguard Knights → Caballeros de Vanguardia · Onslaught → Embestida · Volley → Descarga · Bleed → Sangrado · Shatter → Quiebre · Breach → Brecha · Barrage → Andanada · Dominion → Dominio · Warrants → Vales · Supplies → Suministros · Steward → Administrador · Run → Partida.

---

## Cómo funciona (para curiosos)
Crownhold está hecho en **Godot 4.7**, y su paquete de datos (`.pck`) va dentro del `.exe`, en una sección llamada `pck`. El ejecutable viene compilado sin soporte para `--main-pack`, así que no se le puede indicar un paquete externo. Por eso el script:

1. Lee el paquete del `.exe` original (o de la copia en `mod_es` si el mod ya estaba instalado).
2. Extrae las traducciones compiladas (`OptimizedTranslation`, con textos comprimidos con *smaz*) y arma una nueva, `translation.es.translation`, con locale `es`. Usa la estructura de hashes del juego y busca cada texto por su original en inglés en `es_map.json`.
3. Agrega `mod_espanol.gd`, un script de texto que Godot compila al arrancar, y lo registra como *autoload* en `project.binary`. El script carga la traducción, agrega "Español" a los selectores de idioma y recuerda la elección en `user://mod_espanol.cfg`.
4. Escribe el paquete nuevo en la sección `pck` del `.exe`. Los archivos originales del juego quedan sin modificar.

## Créditos
- Juego: **Crownhold** © Tobias Mikula. Si te gusta, ¡dejale una reseña en Steam!
- Traducción y herramienta: comunidad.
