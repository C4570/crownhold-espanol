"""
Crownhold - Mod de traducción al español (comunidad).

Agrega el español como idioma ADICIONAL de Crownhold (inglés y alemán quedan intactos).
Mete la traducción y un pequeño script (mod_espanol.gd) dentro de Crownhold.exe,
guardando antes una copia del original en mod_es/Crownhold.original.exe.

Uso (en la carpeta mod_es):   python crear_mod_es.py
Desinstalar:                  python crear_mod_es.py --desinstalar
Requiere:                     pip install zstandard
Volvé a correr el script cada vez que el juego se actualice.
"""
import struct, json, os, sys, hashlib, csv, shutil
import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, '..', 'Crownhold.exe')
BACKUP = os.path.join(HERE, 'Crownhold.original.exe')
MAP = os.path.join(HERE, 'es_map.json')
MOD_GD = os.path.join(HERE, 'mod_espanol.gd')
MOD_RES = 'mod_es/mod_espanol.gd'

# ---------- smaz (descompresión de textos de Godot) ----------
RCB = [' ', 'the', 'e', 't', 'a', 'of', 'o', 'and', 'i', 'n', 's', 'e ', 'r', ' th', ' t', 'in', 'he', 'th', 'h', 'he ', 'to', '\r\n', 'l', 's ', 'd', ' a', 'an', 'er', 'c', ' o', 'd ', 'on', ' of', 're', 'of ', 't ', ', ', 'is', 'u', 'at', '   ', 'n ', 'or', 'which', 'f', 'm', 'as', 'it', 'that', '\n', 'was', 'en', '  ', ' w', 'es', ' an', ' i', '\r', 'f ', 'g', 'p', 'nd', ' s', 'nd ', 'ed ', 'w', 'ed', 'http://', 'for', 'te', 'ing', 'y ', 'The', ' c', 'ti', 'r ', 'his', 'st', ' in', 'ar', 'nt', ',', ' to', 'y', 'ng', ' h', 'with', 'le', 'al', 'to ', 'b', 'ou', 'be', 'were', ' b', 'se', 'o ', 'ent', 'ha', 'ng ', 'their', '"', 'hi', 'from', ' f', 'in ', 'de', 'ion', 'me', 'v', '.', 've', 'all', 're ', 'ri', 'ro', 'is ', 'co', 'f t', 'are', 'ea', '. ', 'her', ' m', 'er ', ' p', 'es ', 'by', 'they', 'di', 'ra', 'ic', 'not', 's, ', 'd t', 'at ', 'ce', 'la', 'h ', 'ne', 'as ', 'tio', 'on ', 'n t', 'io', 'we', ' a ', 'om', ', a', 's o', 'ur', 'li', 'll', 'ch', 'had', 'this', 'e t', 'g ', 'e\r\n', ' wh', 'ere', ' co', 'e o', 'a ', 'us', ' d', 'ss', '\n\r\n', '\r\n\r', '="', ' be', ' e', 's a', 'ma', 'one', 't t', 'or ', 'but', 'el', 'so', 'l ', 'e s', 's,', 'no', 'ter', ' wa', 'iv', 'ho', 'e a', ' r', 'hat', 's t', 'ns', 'ch ', 'wh', 'tr', 'ut', '/', 'have', 'ly ', 'ta', ' ha', ' on', 'tha', '-', ' l', 'ati', 'en ', 'pe', ' re', 'there', 'ass', 'si', ' fo', 'wa', 'ec', 'our', 'who', 'its', 'z', 'fo', 'rs', '>', 'ot', 'un', '<', 'im', 'th ', 'nc', 'ate', '><', 'ver', 'ad', ' we', 'ly', 'ee', ' n', 'id', ' cl', 'ac', 'il', '</', 'rt', ' wi', 'div', 'e, ', ' it', 'whi', ' ma', 'ge', 'x', 'e c', 'men', '.com']
def smaz_dec(b):
    out = bytearray(); i = 0
    while i < len(b):
        c = b[i]
        if c == 254: out.append(b[i+1]); i += 2
        elif c == 255: n = b[i+1] + 1; out += b[i+2:i+2+n]; i += 2 + n
        else: out += RCB[c].encode('latin1'); i += 1
    return bytes(out)

# ---------- PCK ----------
def read_pck(f):
    f.seek(-12, 2); sz, magic = struct.unpack('<q4s', f.read(12))
    assert magic == b'GDPC', 'No se encontró el paquete del juego dentro del exe'
    start = f.tell() - 12 - sz
    f.seek(start); hdr = bytearray(f.read(0x70))
    assert hdr[:4] == b'GDPC'
    fmt, vmaj, vmin, vpat, flags = struct.unpack_from('<5I', hdr, 4)
    assert not (flags & 1), 'Paquete cifrado: no soportado'
    base, diro = struct.unpack_from('<QQ', hdr, 24)
    f.seek(start + diro); n = struct.unpack('<I', f.read(4))[0]; ents = []
    for _ in range(n):
        l = struct.unpack('<I', f.read(4))[0]; p = f.read(l).rstrip(b'\0').decode()
        off, s = struct.unpack('<QQ', f.read(16)); md5 = f.read(16); fl = struct.unpack('<I', f.read(4))[0]
        ents.append([p, off, s, md5, fl])
    return start, hdr, base, diro, ents, (vmaj, vmin, vpat)

def get(f, start, base, e):
    f.seek(start + base + e[1]); return f.read(e[2])

def unrscc(d):
    if d[:4] != b'RSCC': return d[4:] if d[:4] == b'RSRC' else d
    mode, bs, total = struct.unpack('<III', d[4:16]); nb = (total + bs - 1) // bs
    sizes = struct.unpack(f'<{nb}I', d[16:16+4*nb]); p = 16 + 4*nb; out = b''
    for i, s in enumerate(sizes):
        rs = bs if i < nb - 1 else total - bs*(nb - 1)
        out += zstandard.ZstdDecompressor().decompress(d[p:p+s], max_output_size=rs); p += s
    return out

# ---------- Recurso binario OptimizedTranslation ----------
class R:
    def __init__(s, d): s.d = d; s.p = 0
    def u32(s): v = struct.unpack_from('<I', s.d, s.p)[0]; s.p += 4; return v
    def u64(s): v = struct.unpack_from('<Q', s.d, s.p)[0]; s.p += 8; return v
    def ustr(s): n = s.u32(); b = s.d[s.p:s.p+n]; s.p += n; return b.rstrip(b'\0').decode()

def parse_tr(d):
    r = R(d); [r.u32() for _ in range(5)]; r.ustr(); r.u64(); flags = r.u32()
    if flags & 2: r.u64()
    r.p += 11*4
    strs = [r.ustr() for _ in range(r.u32())]
    for _ in range(r.u32()): r.ustr(); r.ustr(); r.u64()
    ni = r.u32(); ints = []
    for _ in range(ni): ints.append((r.ustr(), r.u64()))
    r.p = ints[0][1]; r.ustr(); n = r.u32(); props = {}
    for _ in range(n):
        name = strs[r.u32()]; a = r.p; vt = r.u32()
        if vt in (5, 44): v = r.ustr()
        elif vt == 31: ln = r.u32(); v = d[r.p:r.p+ln]; r.p += ln + (4 - ln % 4) % 4
        elif vt == 32: ln = r.u32(); v = list(struct.unpack_from(f'<{ln}i', d, r.p)); r.p += 4*ln
        elif vt == 1: v = None
        else: raise Exception('tipo inesperado %d' % vt)
        props[name] = (vt, a, r.p, v)
    return props

def entries(props):
    bt = props['bucket_table'][3]; s = props['strings'][3]; out = []; i = 0
    while i < len(bt):
        size = bt[i]; i += 2
        for _ in range(size):
            key, off, cs, us = [x & 0xffffffff for x in bt[i:i+4]]
            raw = s[off:off+cs]; t = raw if cs == us else smaz_dec(raw)
            out.append((i, t.rstrip(b'\0').decode('utf-8', 'replace'))); i += 4
    return out

def build_tr(d, props, new_texts):
    bt = list(props['bucket_table'][3]); blob = bytearray()
    for (idx, _), txt in zip(entries(props), new_texts):
        b = txt.encode('utf-8') + b'\0'
        bt[idx+1] = len(blob); bt[idx+2] = len(b); bt[idx+3] = len(b); blob += b
    va, vb = props['bucket_table'][1], props['bucket_table'][2]
    sa, sb = props['strings'][1], props['strings'][2]
    assert vb <= sa
    enc_bt = struct.pack('<II', 32, len(bt)) + struct.pack(f'<{len(bt)}i', *[x if x < 2**31 else x - 2**32 for x in bt])
    pad = (4 - len(blob) % 4) % 4
    enc_s = struct.pack('<II', 31, len(blob)) + bytes(blob) + b'\0'*pad
    return d[:va] + enc_bt + d[vb:sa] + enc_s + d[sb:]

def rscc(body, bs=4096):
    """Empaqueta un recurso como lo hace Godot al exportar (RSCC + bloques zstd)."""
    z = zstandard.ZstdCompressor(level=19)
    blocks = [z.compress(body[i:i+bs]) for i in range(0, len(body), bs)]
    return (b'RSCC' + struct.pack('<III', 2, bs, len(body)) +
            struct.pack('<%dI' % len(blocks), *[len(b) for b in blocks]) + b''.join(blocks) + b'RSCC')

def build_es(ded, de, new_texts):
    body = bytearray(build_tr(ded, de, new_texts))
    vt, a, b, val = de['locale']
    assert val == 'de' and body[a+8:a+10] == b'de'
    body[a+8:a+10] = b'es'                                   # locale "de" -> "es"
    old = b'res://translation.de.translation'
    i = body.index(old); body[i:i+len(old)] = b'res://translation.es.translation'
    r = R(bytes(body)); [r.u32() for _ in range(5)]; r.ustr(); r.u64(); flags = r.u32()
    if flags & 2:                                            # UID propio, distinto del alemán
        uid = struct.unpack_from('<Q', body, r.p)[0]
        struct.pack_into('<Q', body, r.p, (uid ^ 0x5E5E5E5E5E5E) & 0x7FFFFFFFFFFFFFFF)
    return rscc(bytes(body))

def patch_project(data, autoload_key, autoload_path, tr_path):
    """Registra el autoload del mod y la traducción nueva en project.binary."""
    assert data[:4] == b'ECFG'
    n = struct.unpack_from('<I', data, 4)[0]; p = 8; items = []
    for _ in range(n):
        kl = struct.unpack_from('<I', data, p)[0]; k = data[p+4:p+4+kl]; p += 4 + kl
        vl = struct.unpack_from('<I', data, p)[0]; v = data[p+4:p+4+vl]; p += 4 + vl
        items.append([k, v])
    def enc_str(s):
        b = s.encode() + b'\0'; return struct.pack('<I', len(b)) + b + b'\0' * ((4 - len(b) % 4) % 4)
    for it in items:
        if it[0] == b'internationalization/locale/translations':
            v = it[1]; assert struct.unpack_from('<I', v, 0)[0] == 34
            cnt = struct.unpack_from('<I', v, 4)[0]; q = 8; lst = []
            for _ in range(cnt):
                l = struct.unpack_from('<I', v, q)[0]; lst.append(v[q+4:q+4+l].rstrip(b'\0').decode()); q += 4 + l + (4 - l % 4) % 4
            if tr_path not in lst: lst.append(tr_path)
            it[1] = struct.pack('<II', 34, len(lst)) + b''.join(enc_str(x) for x in lst)
    if not any(k == autoload_key.encode() for k, _ in items):
        b = autoload_path.encode()
        items.append([autoload_key.encode(), struct.pack('<II', 4, len(b)) + b + b'\0' * ((4 - len(b) % 4) % 4)])
    out = b'ECFG' + struct.pack('<I', len(items))
    for k, v in items:
        out += struct.pack('<I', len(k)) + k + struct.pack('<I', len(v)) + v
    return out

def pck_info(path):
    with open(path, 'rb') as f:
        start, hdr, base, diro, ents, ver = read_pck(f)
        E = {x[0]: x for x in ents}
        if MOD_RES in E: return True
        return get(f, start, base, E['translation.de.translation'])[:4] == b'RSRC'  # versión vieja del mod

def patch_pe_section(o, start, total):
    """Actualiza el tamaño de la sección 'pck' del .exe (Windows) para que incluya el paquete nuevo."""
    o.seek(0); d = o.read(4096)
    if d[:2] != b'MZ': return
    pe = struct.unpack_from('<I', d, 0x3c)[0]; nsec = struct.unpack_from('<H', d, pe + 6)[0]
    so = pe + 24 + struct.unpack_from('<H', d, pe + 20)[0]
    for i in range(nsec):
        off = so + 40 * i
        if d[off:off+8].rstrip(b'\0') == b'pck' and struct.unpack_from('<I', d, off + 20)[0] == start:
            o.seek(off + 16); o.write(struct.pack('<I', total))

def main():
    if '--desinstalar' in sys.argv:
        if os.path.exists(BACKUP) and pck_info(EXE):
            shutil.copy2(BACKUP, EXE); print('Listo: se restauró el Crownhold.exe original.')
        else:
            print('El juego ya está en su versión original (o no hay copia de seguridad).')
            print('También podés usar en Steam: Propiedades > Archivos instalados > Verificar integridad.')
        return
    if pck_info(EXE):
        if not os.path.exists(BACKUP):
            sys.exit('El juego ya tiene un mod aplicado pero no hay copia del original. '
                     'Verificá la integridad de los archivos en Steam y volvé a correr el script.')
        src = BACKUP; print('El mod ya estaba instalado: se reconstruye a partir de la copia original.')
    else:
        print('Guardando copia del juego original en mod_es (Crownhold.original.exe)...')
        shutil.copy2(EXE, BACKUP); src = BACKUP
    es = json.load(open(MAP, encoding='utf-8'))
    f = open(src, 'rb')
    start, hdr, base, diro, ents, ver = read_pck(f)
    print('Crownhold detectado (Godot %d.%d.%d), %d archivos' % (ver + (len(ents),)))
    E = {e[0]: e for e in ents}
    en = parse_tr(unrscc(get(f, start, base, E['translation.en.translation'])))
    ded = unrscc(get(f, start, base, E['translation.de.translation']))
    de = parse_tr(ded)
    en_e, de_e = entries(en), entries(de)
    assert [a for a, _ in en_e] == [a for a, _ in de_e], 'Estructura de traducciones distinta'
    new = []; falt = []
    for (_, t), (_, tde) in zip(en_e, de_e):
        if t in es: new.append(es[t])
        else: new.append(t); falt.append(t)
    print('Textos: %d, traducidos: %d, sin traducir (quedan en inglés): %d' % (len(new), len(new) - len(falt), len(falt)))
    if falt:
        with open(os.path.join(HERE, 'sin_traducir.csv'), 'w', newline='', encoding='utf-8') as g:
            w = csv.writer(g); w.writerow(['en', 'es']); [w.writerow([t, '']) for t in dict.fromkeys(falt)]
        print('  Lista en sin_traducir.csv (agregalos a es_map.json y volvé a correr)')
    rep = {
        'translation.es.translation': build_es(ded, de, new),
        MOD_RES: open(MOD_GD, 'rb').read(),
        'project.binary': patch_project(get(f, start, base, E['project.binary']),
                                        'autoload/ModEspanol', '*res://' + MOD_RES, 'res://translation.es.translation'),
    }
    for p in rep:                            # archivos nuevos: se agregan al índice
        if p not in E:
            e = [p, 0, 0, b'\0' * 16, 0]; ents.append(e); E[p] = e
    tmp = EXE + '.tmp'
    with open(tmp, 'w+b') as o:
        f.seek(0); left = start
        while left > 0:                      # programa (todo lo anterior al paquete)
            c = f.read(min(left, 1 << 22)); o.write(c); left -= len(c)
        o.write(b'\0' * base)                # cabecera del paquete, se completa al final
        f.seek(start + base); left = diro - base
        while left > 0:                      # datos originales del paquete
            c = f.read(min(left, 1 << 22)); o.write(c); left -= len(c)
        for p, data in rep.items():          # archivos reemplazados
            pos = o.tell() - start; o.write(b'\0' * ((32 - (pos - base) % 32) % 32))
            e = E[p]; e[1] = o.tell() - start - base; e[2] = len(data); e[3] = hashlib.md5(data).digest(); o.write(data)
        pos = o.tell() - start; o.write(b'\0' * ((32 - pos % 32) % 32)); newdir = o.tell() - start
        o.write(struct.pack('<I', len(ents)))
        for p, off, s, md5, fl in ents:
            pb = p.encode(); pb += b'\0' * ((4 - len(pb) % 4) % 4)
            o.write(struct.pack('<I', len(pb)) + pb + struct.pack('<QQ', off, s) + md5 + struct.pack('<I', fl))
        pck_len = o.tell() - start
        o.write(struct.pack('<q', pck_len) + b'GDPC')
        struct.pack_into('<Q', hdr, 32, newdir); o.seek(start); o.write(hdr)
        patch_pe_section(o, start, pck_len + 12)
    f.close()
    try:
        os.replace(tmp, EXE)
    except PermissionError:
        os.remove(tmp); sys.exit('No se pudo reemplazar Crownhold.exe: cerrá el juego y volvé a intentar.')
    print('Listo: Crownhold.exe ahora incluye el español. Elegí "Español" en Ajustes > Idioma.')

if __name__ == '__main__':
    main()
