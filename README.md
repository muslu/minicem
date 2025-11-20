# minicem

Kompakt, insan tarafından okunabilir minik bir metin formatı ve Python için
encoder/decoder fonksiyonları.

A tiny, human-friendly text format.

https://github.com/muslu/minicem

## Ne işe yarar? / What is it for?

- JSON kadar **gürültülü** değil, YAML kadar **karmaşık** değil.  
  Not as noisy as JSON, not as complex as YAML.
- Küçük config / prompt / ayar dosyalarını elle yazmak için ideal.  
  Ideal for small configs, prompts and settings.
- Daha az karakter ⇒ LLM / yapay zeka prompt’larında **daha az token** ⇒ daha ucuz ve hızlı.  
  Fewer characters ⇒ **fewer tokens** in LLM / AI prompts ⇒ cheaper and faster.


## Format Özeti / Format Summary

- ✅ Dict ve list yapıları:
  - `{key:val, key2:val2}`
  - `[1,2,3]`
- ✅ Kompakt bool ve None:
  - `True  -> +1`
  - `False -> +0`
  - `None  -> _`
- ✅ Yorum desteği:
  - Tırnak dışındaki `#` sonrası yorum kabul edilir.
- ✅ Tek satır veya çok satırlı (YAML benzeri) blok formatı
- ✅ Basit Python tipleri:
  - `dict`, `list`, `str`, `int`, `float`, `bool`, `None`
---
- minicem, aynı veride JSON compact’tan ~%15 daha kısa. (minicem is ~15% shorter than compact JSON for this example.)
- LLM prompt’larında her karakter token maliyetine yaklaşır (In LLM prompts, fewer characters ≈ fewer tokens)
- Daha ucuz istekler / cheaper requests (Daha hızlı yanıtlar / faster responses)
- Uzun context kullanan uygulamalarda daha verimli / more efficient in long-context apps
---

## Kurulum

```bash
pip install minicem
```
---
### Örnek
```python
from minicem import encode_mt, decode_mt

data = {
    "users": [
        {"id": 1, "name": "Ali", "active": True},
        {"id": 2, "name": "Veli", "active": False},
        {
            "id": 3,
            "name": "John Doe",
            "active": True,
            "meta": {"age": 32, "city": "New York"},
        },
    ],
    "nums": [1, 2, 3],
    "title": "Example Data",
}

# Python -> minicem
text = encode_mt(data)
print("MINICEM:")
print(text)

# minicem -> Python
decoded = decode_mt(text)
print("DECODED:")
print(decoded)

assert decoded == data
```
---

### Çıktı
```sh
#MINICEM:
{users:[{id:1, name:Ali, active:+1},{id:2, name:Veli, active:+0},{id:3, name:"John Doe", active:+1, meta:{age:32, city:"New York"}}], nums:[1,2,3], title:"Example Data"}

#DECODED:
{'users': [{'id': 1, 'name': 'Ali', 'active': True}, {'id': 2, 'name': 'Veli', 'active': False}, {'id': 3, 'name': 'John Doe', 'active': True, 'meta': {'age': 32, 'city': 'New York'}}], 'nums': [1, 2, 3], 'title': 'Example Data'}
```
