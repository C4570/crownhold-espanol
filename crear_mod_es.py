"""
Crownhold - Mod de traducción al español (comunidad).

Genera Crownhold_ES.pck a partir del Crownhold.exe instalado, sin modificar el juego.
El español ocupa el lugar del alemán ("Deutsch" pasa a llamarse "Español" en el menú).

Uso (en la carpeta mod_es):   python crear_mod_es.py
Requiere:                     pip install zstandard
Después, en Steam: Crownhold > Propiedades > Opciones de lanzamiento:
    --main-pack mod_es/Crownhold_ES.pck
Volvé a correr el script cada vez que el juego se actualice.
"""
import struct, json, os, sys, hashlib, csv
import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, '..', 'Crownhold.exe')
OUT = os.path.join(HERE, 'Crownhold_ES.pck')
MAP = os.path.join(HERE, 'es_map.json')

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
    body = d[:va] + enc_bt + d[vb:sa] + enc_s + d[sb:]
    return b'RSRC' + body

# ---------- Parche de nombres de idioma en scripts compilados ----------
def patch_gdc(data, repl):
    assert data[:4] == b'GDSC'
    ver, size = struct.unpack('<II', data[4:12])
    raw = zstandard.ZstdDecompressor().decompress(data[12:], max_output_size=size) if size else data[12:]
    def enc(s):
        b = s.encode('utf-8'); return struct.pack('<II', 4, len(b)) + b + b'\0'*((4 - len(b) % 4) % 4)
    for a, b in repl:
        ea, eb = enc(a), enc(b); assert len(ea) == len(eb)
        n = raw.count(ea)
        if n == 0: print('  aviso: no se encontró', a); continue
        raw = raw.replace(ea, eb)
    comp = zstandard.ZstdCompressor(level=19).compress(raw) if size else raw
    return b'GDSC' + struct.pack('<II', ver, len(raw) if size else 0) + comp

def main():
    es = json.load(open(MAP, encoding='utf-8'))
    f = open(EXE, 'rb')
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
    rep = {'translation.de.translation': build_tr(ded, de, new)}
    if 'ui/panels/settings_menu.gdc' in E:
        rep['ui/panels/settings_menu.gdc'] = patch_gdc(get(f, start, base, E['ui/panels/settings_menu.gdc']),
            [('Deutsch', 'Español'), ('Englisch', 'Inglés')])
    if 'scenes/language_intro.gdc' in E:
        rep['scenes/language_intro.gdc'] = patch_gdc(get(f, start, base, E['scenes/language_intro.gdc']),
            [('DEUTSCH', 'ESPAÑOL')])
    tmp = OUT + '.tmp'
    with open(tmp, 'wb') as o:
        o.write(b'\0' * base)  # cabecera, se completa al final
        f.seek(start + base); left = diro - base
        while left > 0:
            c = f.read(min(left, 1 << 22)); o.write(c); left -= len(c)
        for p, data in rep.items():
            pos = o.tell(); pad = (32 - (pos - base) % 32) % 32; o.write(b'\0' * pad)
            e = E[p]; e[1] = o.tell() - base; e[2] = len(data); e[3] = hashlib.md5(data).digest(); o.write(data)
        pos = o.tell(); o.write(b'\0' * ((32 - pos % 32) % 32)); newdir = o.tell()
        o.write(struct.pack('<I', len(ents)))
        for p, off, s, md5, fl in ents:
            pb = p.encode(); pb += b'\0' * ((4 - len(pb) % 4) % 4)
            o.write(struct.pack('<I', len(pb)) + pb + struct.pack('<QQ', off, s) + md5 + struct.pack('<I', fl))
        struct.pack_into('<Q', hdr, 32, newdir); o.seek(0); o.write(hdr)
    os.replace(tmp, OUT)
    print('Listo:', OUT, '(%.1f MB)' % (os.path.getsize(OUT) / 1e6))

if __name__ == '__main__':
    main()
