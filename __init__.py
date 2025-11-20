"""
Mini tipler serileştirmek için basit encode/decode fonksiyonları.

Format özellikleri:
- Bool:  True  -> "+1", False -> "+0"
- None:  "_" (alt çizgi)
- Sayılar: int/float olduğu gibi
- String:
    * İçinde boşluk varsa: "tırnaklı"
    * Yoksa: çıplak haliyle
- Liste: [a,b,c]
- Sözlük: {key:val, key2:val2}
- Satır sonu yorumları: tırnak dışındaki '#' ile başlar
"""

import re


def encode_mt(value):
    """
    Python değerini (dict/list/primitive) minicem metin formatına çevirir.

    Parametreler
    -----------
    value : Any
        Serileştirilecek Python objesi.

    Dönüş
    -----
    str
        Tek satırlık minicem gösterimi.
    """
    # Bool'lar için kompakt gösterim
    if isinstance(value, bool):
        return "+1" if value else "+0"

    # None için tek karakter
    if value is None:
        return "_"

    # Sayılar (int / float)
    if isinstance(value, (int, float)):
        return str(value)

    # String değerler
    if isinstance(value, str):
        # İçinde boşluk varsa tırnakla
        return f'"{value}"' if " " in value else value

    # Liste -> her zaman inline: [a,b,c]
    if isinstance(value, list):
        inner = ",".join(encode_mt(v) for v in value)
        return "[" + inner + "]"

    # Sözlük -> her zaman inline: {key:val, key2:val2}
    if isinstance(value, dict):
        parts = [f"{k}:{encode_mt(v)}" for k, v in value.items()]
        return "{" + ", ".join(parts) + "}"

    # Bilinmeyen tipler stringe düşsün
    return str(value)


def decode_mt(text):
    """
    Minicem metin formatını tekrar Python objesine çevirir.

    - Tek satırlık inline yapı: { ... } veya [ ... ]
    - Birden fazla satır: basit YAML benzeri blok formatı
    - Satır sonu yorumları: # işaretinden sonrası yok sayılır
      (ama tırnak içindeki # korunur)

    Parametreler
    -----------
    text : str
        Minicem ile kodlanmış metin.

    Dönüş
    -----
    Any
        Elde edilen Python objesi (dict, list, str, int, float, bool, None).
    """

    def _strip_comment(line: str) -> str:
        """Tırnak içindeki # karakterlerine dokunmadan yorumları temizle."""
        in_string = False
        result = []

        for ch in line:
            if ch == '"':
                in_string = not in_string
                result.append(ch)
            elif ch == "#" and not in_string:
                # Tırnak dışında ilk # gördüğümüzde yorum başlıyor
                break
            else:
                result.append(ch)

        return "".join(result).rstrip()

    # Yorum ve boş satırları temizle
    clean_lines = []
    for raw_line in text.splitlines():
        line = _strip_comment(raw_line)
        if line.strip():
            clean_lines.append(line)
    lines = clean_lines

    def _parse_primitive(v: str):
        """En basit tipleri (bool, None, sayı, string) çöz."""
        # Bool token'ları (yeni kısa format + eski true/false desteği)
        if v in ("+1", "true"):
            return True
        if v in ("+0", "false"):
            return False

        # None
        if v == "_":
            return None

        # Tırnaklı string
        if v.startswith('"') and v.endswith('"'):
            # Basit kullanım için kaçış karakteri desteklenmiyor
            return v[1:-1]

        # Integer
        if re.fullmatch(r"-?\d+", v):
            return int(v)

        # Float
        if re.fullmatch(r"-?\d+\.\d+", v):
            return float(v)

        # Geriye kalan her şey düz string
        return v

    def _split_top_level(s: str, sep: str):
        """
        En dış seviyedeki ayırıcıya göre böl.
        Örn: "a,b,[1,2],{x:1,y:2}" -> ["a", "b", "[1,2]", "{x:1,y:2}"]
        """
        out = []
        depth = 0
        in_string = False
        cur = []

        for ch in s:
            if ch == '"':
                in_string = not in_string
                cur.append(ch)
                continue

            if not in_string:
                if ch in "{[":
                    depth += 1
                elif ch in "}]":
                    depth -= 1

                if ch == sep and depth == 0:
                    out.append("".join(cur))
                    cur = []
                    continue

            cur.append(ch)

        out.append("".join(cur))
        return out

    def _parse_value(s: str):
        """Tek bir değeri (primitive, liste, dict) çöz."""
        s = s.strip()

        # Inline dict
        if s.startswith("{") and s.endswith("}"):
            inner = s[1:-1].strip()
            if not inner:
                return {}
            obj = {}
            parts = _split_top_level(inner, ",")
            for p in parts:
                key, val = p.split(":", 1)
                obj[key.strip()] = _parse_value(val.strip())
            return obj

        # Inline list
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            parts = _split_top_level(inner, ",")
            return [_parse_value(p.strip()) for p in parts]

        # Primitive
        return _parse_primitive(s)

    idx = 0
    n = len(lines)

    # Tek satırlık inline root
    if n == 1:
        single = lines[0].strip()
        if (single.startswith("{") and single.endswith("}")) or (
            single.startswith("[") and single.endswith("]")
        ):
            return _parse_value(single)

    def _parse_block(indent: int):
        """
        Eski çok satırlı formatı çözen basit blok parser.

        YAML benzeri:
            - liste elemanları için '-'
            - sözlükler için 'key: value'
        """
        nonlocal idx
        obj = None

        while idx < n:
            line = lines[idx]
            stripped = line.lstrip()
            cur_indent = len(line) - len(stripped)

            # Üst seviyeye geri döndüysek bloğu bitir
            if cur_indent < indent:
                break

            # Liste elemanı
            if stripped.startswith("-"):
                if obj is None:
                    obj = []

                tail = stripped[1:].strip()

                if tail:
                    # Tek satırda değer var
                    obj.append(_parse_value(tail))
                    idx += 1
                else:
                    # Alt blok
                    idx += 1
                    obj.append(_parse_block(cur_indent + 2))

                continue

            # key: value satırı
            if ":" in stripped:
                if obj is None or isinstance(obj, list):
                    obj = {}

                key, rest = stripped.split(":", 1)
                key = key.strip()
                rest = rest.strip()

                if rest:
                    obj[key] = _parse_value(rest)
                    idx += 1
                else:
                    idx += 1
                    obj[key] = _parse_block(cur_indent + 2)

                continue

            # Tanınmayan satır; atla
            idx += 1

        return obj

    return _parse_block(0)
