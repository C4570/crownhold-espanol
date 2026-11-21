# Crownhold en español 🇪🇸

Traducción al español, hecha por la comunidad, de **[Crownhold](https://store.steampowered.com/app/4579940/Crownhold/)**, el juego incremental de Tobias Mikula, que oficialmente viene solo en inglés y alemán.

- Traduce los **1568 textos** del juego: menús, mejoras, tutoriales, eventos y diálogos.
- **No modifica ningún archivo del juego.** Genera un paquete aparte (`Crownhold_ES.pck`) que el juego carga cuando se lo indicás desde Steam.
- Logros de Steam, guardado en la nube y partidas guardadas siguen funcionando igual.

> ⚠️ Es un mod **no oficial**. No tiene relación con el desarrollador. Este repo **no incluye archivos del juego**: el script arma el paquete a partir de *tu* copia instalada.

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
    ├── crear_mod_es.py
    └── es_map.json
```

### 4. Generá el paquete en español
Hacé doble clic en **`mod_es\instalar.bat`**. Tarda unos segundos y crea `mod_es\Crownhold_ES.pck` (~90 MB).

### 5. Configurá Steam
Clic derecho en **Crownhold → Propiedades → General → Opciones de lanzamiento** y pegá:
```
--main-pack mod_es/Crownhold_ES.pck
```

### 6. Elegí el idioma
Abrí el juego y elegí **Español** en el selector de idioma del primer inicio o en **Ajustes → Idioma**.

> El español reemplaza el lugar del alemán: con el mod activo, la opción "Deutsch" pasa a ser "Español".

---

## Cuando el juego se actualiza
Después de cada actualización de Crownhold, **volvé a hacer doble clic en `instalar.bat`**. Así el paquete se arma desde la versión nueva del juego.

Si la actualización trae textos nuevos que todavía no están traducidos, aparecen en inglés y el script los lista en `sin_traducir.csv`.

## Desinstalar
1. Borrá el texto de **Opciones de lanzamiento** en Steam.
2. Borrá la carpeta `mod_es`.

## Problemas comunes

| Problema | Solución |
|---|---|
| `instalar.bat` dice que no encuentra Python | Reinstalá Python marcando "Add Python to PATH" y reiniciá la PC. |
| Dice que no encuentra `Crownhold.exe` | La carpeta `mod_es` tiene que estar **dentro** de la carpeta del juego, al lado de `Crownhold.exe`. |
| El juego sigue en inglés/alemán | Revisá la opción de lanzamiento y elegí "Español" en Ajustes → Idioma. |
| El juego no abre con la opción de lanzamiento | Probá con la ruta completa: `--main-pack "C:\Program Files (x86)\Steam\steamapps\common\Crownhold\mod_es\Crownhold_ES.pck"` |
| Después de una actualización algo anda raro | Volvé a correr `instalar.bat`. |

---

## Corregir o mejorar la traducción
Todos los textos están en **`es_map.json`**, con el formato `"texto original en inglés": "traducción"`.

1. Editá la traducción (dejá igual el texto en inglés de la izquierda).
2. Respetá exactamente lo que está entre llaves `{así}`, los códigos como `%d` y las etiquetas `[color=...]`, `[b]`, etc.
3. Volvé a correr `instalar.bat` para probar.

Los *Pull Requests* con correcciones son bienvenidos. Si encontrás un error y no querés editar, abrí un **Issue** con una captura.

**Glosario usado** (para mantener coherencia): Longbowmen → Arqueros · Swordsmen → Espadachines · Militia → Milicia · Breachers → Zapadores · Vanguard Knights → Caballeros de Vanguardia · Onslaught → Embestida · Volley → Descarga · Bleed → Sangrado · Shatter → Quiebre · Breach → Brecha · Barrage → Andanada · Dominion → Dominio · Warrants → Vales · Supplies → Suministros · Steward → Administrador · Run → Partida.

---

## Cómo funciona (para curiosos)
Crownhold está hecho en **Godot 4.7** y tiene su paquete de datos (`.pck`) metido adentro del `.exe`. El script:

1. Lee el paquete embebido del `.exe`.
2. Extrae las traducciones compiladas (`OptimizedTranslation`, con textos comprimidos con *smaz*).
3. Reconstruye el recurso del alemán (`translation.de.translation`) con los textos en español, buscando cada uno por su texto en inglés en `es_map.json`.
4. Cambia en los scripts compilados del menú de idioma los nombres "Deutsch"/"DEUTSCH"/"Englisch" por "Español"/"ESPAÑOL"/"Inglés".
5. Escribe un `.pck` nuevo con esos 3 archivos reemplazados. Los demás archivos quedan idénticos.

Godot carga ese paquete en lugar del embebido gracias al parámetro `--main-pack`.

## Créditos
- Juego: **Crownhold** © Tobias Mikula. Si te gusta, ¡dejale una reseña en Steam!
- Traducción y herramienta: comunidad.
