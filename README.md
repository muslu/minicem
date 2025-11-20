# minicem

Kompakt, insan tarafından okunabilir minik bir metin formatı ve Python için
encoder/decoder fonksiyonları.

Amaç: JSON kadar gürültülü olmayan, config dosyalarında rahat yazılabilen,
hem tek satırlık hem de YAML benzeri çok satırlı yapıları destekleyen ufak bir
ara format.

## Özellikler

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
