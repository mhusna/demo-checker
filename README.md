# Demo Checker

Core değişikliklerinin bağımlı projelere etkisini analiz eden Python CLI paketi
ve GitHub Actions demo uygulaması.

Bir `core` projesindeki deployment öncesi değişikliklerin, ona bağımlı ayrı bir
`business` deposundaki olası etkilerini GitHub Actions içinde inceleyen demo.
Analiz, Azure AI Foundry üzerinde dağıtılmış bir Azure OpenAI modeliyle çalışan
üç uzman agent'ın (bağımlılık etkisi, davranış/uyumluluk ve yayın riski)
bulgularını sentezler.

## Akış

1. `main` dalına push veya elle workflow çalıştırma analizi başlatır.
2. Workflow, `core` deposundaki diff'i ve yapılandırılmış `business` deposunu alır.
3. Statik tarama değişen helper adlarını ve `business` içindeki metinsel referansları toplar.
4. Üç uzman agent bu kanıtları bağımsız inceler; sentez agent'ı sonucu birleştirir.
5. Markdown raporu GitHub Actions özetinde ve indirilebilir artifact olarak yayımlanır.

Agent'lar olasılıksal değerlendirme yapar. Metinsel eşleşme tam bir çağrı grafiği
veya derleme/test kanıtı değildir; rapor bunu kesin doğrulanmış davranış olarak
sunmamalıdır.

## GitHub yapılandırması

`core` deposunun **Settings → Secrets and variables → Actions** bölümünde:

| Tür | Ad | Değer |
| --- | --- | --- |
| Variable | `BUSINESS_REPOSITORY` | `owner/repository` biçiminde business deposu |
| Variable | `BUSINESS_BASE_REF` | Business deposunun analiz edilecek dalı (isteğe bağlı, varsayılan `main`) |
| Secret | `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint'i (ör. `https://<resource>.openai.azure.com`) |
| Secret | `AZURE_OPENAI_API_KEY` | Endpoint için API anahtarı |
| Variable | `AZURE_OPENAI_DEPLOYMENT` | Dağıtılmış model deployment adı |
| Variable | `ANALYZER_REPOSITORY` | Yayımlanmış analiz aracının `owner/repository` adı |

Bu demo reposu public olduğu için business checkout işlemi ilave token
kullanmaz. Azure anahtarını koda veya workflow variable'larına koymayın.

Azure AI Foundry'de Azure OpenAI v1 API destekleyen bir kaynak ve model
deployment'ı oluşturun. `AZURE_OPENAI_DEPLOYMENT` değeri model adı değil,
deployment adıdır. Entegrasyon sürüm parametresi gerektirmeyen
`/openai/v1/` endpoint'ini kullanır. Etki analizi workflow'u core deposunda,
varsayılan olarak `main` branch push'larında çalışır; `workflow_dispatch` ile
elle de başlatılabilir. Yayımlanan demo için repo adresleri ve kurulum adımları
[demo projeler](docs/demo-projects.md) belgesindedir.

Kurulum ayrıntıları ve veri akışı için [mimari ve yapılandırma](docs/architecture.md)
belgesine bakın.

## Yerel geliştirme

Python 3.12+ ve Git gereklidir.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
python -m pytest
```

Analizi yerelde çalıştırmak için iki repository klasörünü ve bir Git base ref'i
verin; Azure ayarlarını ortam değişkeni olarak sağlayın:

```powershell
$env:AZURE_OPENAI_ENDPOINT = "https://<resource>.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY = "<secret>"
$env:AZURE_OPENAI_DEPLOYMENT = "<deployment-name>"
demo-checker --core-repo ..\core --business-repo ..\business --base origin/main --report impact-report.md
```

## Sınırlar

- İlk demo helper tanımlarını Python ve JavaScript/TypeScript'te tanır; referans
  taraması metin tabanlıdır ve başka dillerdeki eşleşmeleri de bulabilir.
- Dinamik dispatch, alias/import çözümleme ve gerçek çağrı grafiği çıkarımı yoktur.
- Bu proje örnek kod sağlar, gerçek deployment platformuna dağıtım yapmaz.
  Core deposundaki workflow analizden sonra açıkça demo deployment adımı
  gösterir; gerçek ortama bağlamadan önce onay ve test kapıları ekleyin.
- İncelenen diff ve eşleşen business kod parçaları Azure endpoint'ine gönderilir.
  Kurumunuzun veri sınıflandırma ve saklama kurallarını önceden doğrulayın.
