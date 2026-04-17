# Yerimi Birleştirme — Tarayıcı Yer İmi Birleştirici

Chrome, Edge ve Firefox tarayıcılarındaki yer imlerini okuyup tek bir HTML dosyasında birleştirir. Oluşan dosya tüm tarayıcılara standart yolla içe aktarılabilir.

## Gereksinimler

- Python 3.10 veya üzeri
- Ek paket gerekmez (yalnızca Python standart kütüphanesi kullanılır)
- **Linux ve Windows 11** desteklenir (işletim sistemi otomatik algılanır)

## Kullanım

### Temel kullanım

**Linux / macOS:**
```bash
python3 bookmark_merger.py
```

**Windows 11:**
```powershell
python bookmark_merger.py
```

Tüm tespit edilen tarayıcıların yer imlerini birleştirir ve `bookmarks_merged.html` dosyasını oluşturur.

### Seçenekler

| Seçenek | Açıklama |
|---|---|
| `--output DOSYA` | Çıktı dosyasının adı/yolu. Varsayılan: `bookmarks_merged.html` |
| `--browsers chrome edge firefox` | Yalnızca belirtilen tarayıcıları dahil et |
| `--no-dedup` | Aynı URL'yi birden fazla tarayıcıda varsa hepsini yaz (varsayılan: tekrarlar silinir) |
| `--verbose` | Ayrıntılı işlem logu göster |

### Örnekler

```bash
# Tüm tarayıcıları birleştir, özel dosya adı ver
python3 bookmark_merger.py --output tum_yer_imlerim.html

# Sadece Firefox ve Chrome'u birleştir
python3 bookmark_merger.py --browsers firefox chrome

# Tekrarlananları silmeden birleştir
python3 bookmark_merger.py --no-dedup

# Hangi tarayıcıların bulunduğunu ve kaç yer imi okunduğunu gör
python3 bookmark_merger.py --verbose
```

## Tarayıcı Profil Konumları

Araç işletim sistemini otomatik algılayarak doğru konuma bakar:

| Tarayıcı | Linux | Windows 11 |
|---|---|---|
| Chrome | `~/.config/google-chrome/Default/Bookmarks` | `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks` |
| Edge | `~/.config/microsoft-edge/Default/Bookmarks` | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Bookmarks` |
| Firefox | `~/.mozilla/firefox/*.default*/places.sqlite` | `%APPDATA%\Mozilla\Firefox\Profiles\*.default*\places.sqlite` |

Tarayıcı kurulu değilse veya profil bulunamazsa o tarayıcı atlanır, hata verilmez.

> **Not:** Firefox açıkken de çalışır — veritabanı kilitlenmesi sorunu yaşanmaz.

## Çıktı Dosyasını Tarayıcıya Aktarma

Oluşan `bookmarks_merged.html` dosyasını istediğiniz tarayıcıya içe aktarabilirsiniz:

**Chrome / Edge**
1. Adres çubuğuna `chrome://bookmarks` (veya `edge://bookmarks`) yazın
2. Sağ üstteki `⋮` menüsünden **"Yer imlerini ve ayarları içe aktar"** seçin
3. `bookmarks_merged.html` dosyasını seçin

**Firefox**
1. Yer İmleri menüsünden **"Tüm yer imlerini yönet"** açın (veya `Ctrl+Shift+O`)
2. **İçe Aktar ve Yedekle → HTML'den yer imlerini içe aktar** seçin
3. `bookmarks_merged.html` dosyasını seçin
