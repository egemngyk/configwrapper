# configwrap

Config ve ayar dosyalarındaki değişkenleri tek bir API ile yönetmek için Python kütüphanesi. Dosya yolu ve değişken şeması (structure) verirsin; okuma, yazma, ekleme ve silme işlemleri hep aynı arayüzden yapılır.

**English:** [README.md](README.md)

---

## İçindekiler

- [Proje yapısı](#proje-yapısı)
- [Temel kavramlar](#temel-kavramlar)
- [Kurulum](#kurulum)
- [Hızlı başlangıç](#hızlı-başlangıç)
- [Tutorial](#tutorial)
  - [1. Import ve Core oluşturma](#1-import-ve-core-oluşturma)
  - [2. Değer okuma ve yazma](#2-değer-okuma-ve-yazma)
  - [3. Tüm değerler / toplu yazma](#3-tüm-değerler--toplu-yazma)
  - [4. Listeleme ve kontrol](#4-listeleme-ve-kontrol)
  - [5. Ekleme ve silme](#5-ekleme-ve-silme)
  - [6. Sıfırlama ve yeniden yükleme](#6-sıfırlama-ve-yeniden-yükleme)
  - [7. Loglar](#7-loglar)
  - [8. Dosya formatları](#8-dosya-formatları)
- [Komut özeti](#komut-özeti)
- [Tam örnek](#tam-örnek)
- [GitHub'a yükleme](#githuba-yükleme)
- [Lisans](#lisans)

---

## Proje yapısı

```text
configwrap/
├── main.py                 # Çalıştırma / örnek
├── config/                 # Veri dosyaları (.json, .conf)
│   ├── app.conf
│   └── theme.json
├── configwrap/             # Paket
│   ├── __init__.py
│   ├── core.py
│   ├── structure.py
│   └── formats.py
├── LICENSE
├── .gitignore
└── README.md
```

---

## Temel kavramlar

| Kavram        | Açıklama                                                                                             |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| **Dosya**     | Değerlerin saklandığı dosya (örn. `config/app.conf`). JSON veya conf formatında.                     |
| **Structure** | Hangi değişkenlerin olacağı ve varsayılan değerleri. Python `dict`: `{"theme": "dark", "size": 14}`. |
| **Core**      | Dosya ile structure'ı birleştirir. `get`, `set`, `save` vb. tüm işlemler Core üzerinden.             |

> **Özet:** “Bu dosyada şu değişkenler olsun, varsayılanları bunlar” diye structure tanımlarsın; Core dosyayı okuyup yazar ve değişkenleri yönetir.

---

## Kurulum

Proje dizininde harici bağımlılık yok; doğrudan paketi import edebilirsin:

```bash
git clone https://github.com/egemngyk/configwrap.git
cd configwrap
python main.py
```

Başka bir projede kullanmak için `configwrap` klasörünü projene kopyala veya `PYTHONPATH`'e ekle.

---

## Hızlı başlangıç

```python
from pathlib import Path
from configwrap import Core, core_config

CONFIG = Path(__file__).parent / "config" / "app.conf"
VARS = {"theme": "dark", "font_size": 14}

c = Core(str(CONFIG), VARS)
c.set("theme", "light")
c.save()
```

---

## Tutorial

### 1. Import ve Core oluşturma

```python
from pathlib import Path
from configwrap import Core, core_config

CONFIG = Path(__file__).parent / "config" / "app.conf"
VARS = {
    "theme": "dark",
    "font_size": 14,
    "accent_color": "#3498db",
}

c = Core(str(CONFIG), VARS)
```

- **Dosya yoksa:** İlk açılışta sadece bellekte varsayılan değerler kullanılır; `c.save()` ile dosya oluşturulur.
- **Dosya varsa:** İçerik okunur, structure ile birleştirilir; eksik alanlar varsayılanla doldurulur.

### 2. Değer okuma ve yazma

```python
tema = c.get("theme")      # okuma
c.set("theme", "light")   # yazma (bellekte)
c.set("font_size", 16)
c.save()                  # dosyaya kaydet
```

- **get:** Sadece okur. Değişken structure'da yoksa hata verir.
- **set:** Bellekte günceller; kalıcı olması için **save()** gerekir.

### 3. Tüm değerler / toplu yazma

```python
hepsi = c.get_all()
c.set_all({"theme": "dark", "font_size": 12})
c.save()
```

### 4. Listeleme ve kontrol

```python
isimler = c.list()        # veya c.keys()
if c.has("theme"):
    print(c.get("theme"))
c.items()                 # (isim, değer) çiftleri
c.values()                 # sadece değerler
```

### 5. Ekleme ve silme

```python
c.add("version", 1)
c.add("debug_mode", False)
c.save()

# Sadece veriden siler; reload'da varsayılanla geri gelir
c.delete("font_size")

# Hem veriden hem şemadan siler; kalıcı
c.delete("debug_mode", from_structure=True)
c.save()
```

### 6. Sıfırlama ve yeniden yükleme

```python
c.clear()      # tüm değerleri varsayılana çek
c.save()

c.reload()     # dosyayı tekrar oku
```

### 7. Loglar

```python
c.info("Config yüklendi")
c.warn("Dikkat: eski format")
c.error("Dosya yazılamadı")
c.critical("Kritik hata")

# Sadece debug açıkken
core_config["debug"] = True   # tüm Core'lar
c.debug = True                # sadece bu Core
c.log_debug("theme = %s", c.get("theme"))
```

### 8. Dosya formatları

| Uzantı              | Format | Açıklama                                                     |
| ------------------- | ------ | ------------------------------------------------------------ |
| `.json`             | JSON   | Key–value.                                                   |
| `.conf` / uzantısız | Conf   | `key=value` veya `key: value`, `[section]`, `#` / `;` yorum. |

Formatı zorlamak için:

```python
c = Core("config/ayar.conf", VARS, format="conf")
c = Core("config/ayar.json", VARS, format="json")
```

Bölümlü conf: structure'da `"ui.theme": "dark"` → dosyada `[ui]` altında `theme=dark`.

---

## Komut özeti

| İşlem               | Komut                                                                |
| ------------------- | -------------------------------------------------------------------- |
| Değer oku           | `c.get("isim")`                                                      |
| Değer yaz           | `c.set("isim", değer)`                                               |
| Tümünü al           | `c.get_all()`                                                        |
| Toplu yaz           | `c.set_all({"a": 1})`                                                |
| İsimleri listele    | `c.list()` / `c.keys()`                                              |
| Var mı?             | `c.has("isim")`                                                      |
| Çiftler / değerler  | `c.items()`, `c.values()`                                            |
| Yeni değişken       | `c.add("isim", varsayılan)`                                          |
| Sil                 | `c.delete("isim")` / `c.delete("isim", from_structure=True)`         |
| Varsayılana sıfırla | `c.clear()`                                                          |
| Dosyadan oku        | `c.reload()`                                                         |
| Dosyaya yaz         | `c.save()`                                                           |
| Log                 | `c.info()`, `c.warn()`, `c.error()`, `c.critical()`, `c.log_debug()` |
| Debug               | `core_config["debug"] = True/False` veya `c.debug = True/False`      |

---

## Tam örnek

```python
from pathlib import Path
from configwrap import Core, core_config

core_config["debug"] = False
CONFIG = Path(__file__).parent / "config" / "uygulama.conf"
VARS = {"theme": "dark", "dil": "tr", "ses": True}

c = Core(str(CONFIG), VARS)
c.info("Başladı: %s", c.file_path)

c.set("theme", "light")
c.set("dil", "en")
c.save()

print("Güncel:", c.get_all())
```

Bu script çalıştığında `config/uygulama.conf` oluşur veya güncellenir; `theme`, `dil`, `ses` değişkenleri structure'daki tiplere uygun yazılır.

---

## Lisans

MIT License. Detay için [LICENSE](LICENSE) dosyasına bakın.
