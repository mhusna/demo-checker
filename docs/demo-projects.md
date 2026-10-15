# Demo depoları

Bu demo üç public GitHub deposu kullanır:

- [yanki-deployment-checker](https://github.com/mhusna/yanki-deployment-checker):
  diff, referans taraması ve AI agent ağı.
- [core](https://github.com/mhusna/core): değiştirilen helper'ların kaynağı;
  push üzerine analiz workflow'unu çalıştırır.
- [business](https://github.com/mhusna/business): `core` helper'ını kullanan
  bağımlı örnek uygulama.

## Bağımlılık yönü

`business/pyproject.toml`, `core-calculators` paketini core deposunun
`v0.1.0` tag'inden kurar. Business kodu `calculate_total` helper'ını order
toplamında kullanır. `core` içindeki helper adı değiştiğinde analiz aracı diff
ve business deposundaki import/kullanım satırlarını raporlar.

Yeni bir core sürümü çıkınca business bağımlılığını yeni tag'e yükseltip
business testlerini çalıştırın. Sadece core deposuna push yapılması business
projesinin kurulu bağımlılığını kendiliğinden güncellemez.

## Core Actions ayarları

`core` deposunun **Settings → Secrets and variables → Actions → Variables**
bölümüne şunları ekleyin:

| Ad | Değer |
| --- | --- |
| `BUSINESS_REPOSITORY` | `mhusna/business` |
| `BUSINESS_BASE_REF` | `main` |
| `ANALYZER_REPOSITORY` | `mhusna/yanki-deployment-checker` |
| `AZURE_OPENAI_DEPLOYMENT` | Azure AI Foundry'deki deployment adı |

**Secrets** bölümüne ekleyin:

| Ad | Değer |
| --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint'i |
| `AZURE_OPENAI_API_KEY` | Endpoint API key'i |

Core deposunun Actions izinlerinde workflow'ların çalışmasına izin verildiğini
doğrulayın. Public depoların checkout'u için ek PAT gerekmez.

## Yerel kullanım

PowerShell'de depoları aynı üst klasöre klonladıktan sonra:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .\core -e .\business
python -m pytest .\core\tests .\business\tests
```

`core` helper'ında bir değişiklik yapıp `core` ana dalına push edin. GitHub
Actions analiz raporunu workflow run özeti ve artifact olarak yayımlar.

## Sınırlar

`demo-deployment` workflow adımı yalnızca örnek yer tutucudur; bulut ortamına
gerçek deployment yapmaz. Gerçek deployment platformu seçildiğinde bu adım
uygun deploy action/komutuyla değiştirilmelidir. Bu repo/branch düzeni bir
üretim dağıtım politikasının yerini tutmaz.
