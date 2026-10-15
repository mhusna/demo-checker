# Mimari ve yapılandırma

## Bileşenler

- `core/.github/workflows/deployment-impact.yml`: core push'u ve elle
  tetikleme, business ve analiz deposu checkout'u, analiz çalıştırma,
  raporlama ve demo deployment adımı.
- `.github/workflows/tests.yml`: checker deposunun test CI'si.
- `src/deployment_impact/analysis.py`: Git diff'i okur, desteklenen helper
  tanımlarını çıkarır ve business deposunda sınırlı sayıda metinsel referans bulur.
- `src/deployment_impact/agents.py`: Azure OpenAI endpoint'ine paralel üç uzman
  değerlendirmesi gönderir ve sentez agent'ıyla rapor oluşturur.
- `src/deployment_impact/cli.py`: bileşenleri birleştirir, boş diff'i reddeder
  ve raporu dosyaya yazar.

## Güven sınırları

Business deposu içeriği model isteminde **güvenilmeyen veri** olarak ele alınır.
Agent'lara yalnızca core diff ve referans bulunan satırlardan kısa kanıt parçaları
verilir; tüm business deposu gönderilmez. Yine de bu kod parçaları Azure
endpoint'ine aktarılır. Hassas veri içeren depolarda çalıştırmadan önce Azure
AI Foundry bölgesi, erişim, loglama ve saklama politikalarını doğrulayın.

Workflow minimum `contents: read` izni ister. Demo depoları public olduğundan
business ve analiz deposu checkout'u için ekstra token kullanılmaz. Azure
anahtarını yalnızca Actions secret olarak saklayın. Bu demo API key ile kimlik doğrular;
üretimde GitHub OIDC ve Microsoft Entra ID federasyonu gibi kısa ömürlü
kimlik bilgilerini değerlendirin.

Azure çağrıları Azure OpenAI v1 API'sini ve OpenAI Python SDK'sının standart
`OpenAI` istemcisini kullanır. `AZURE_OPENAI_ENDPOINT` sonuna `/openai/v1/`
eklenir; API sürümü parametresi gerekmez. Model parametresi olarak Azure'daki
deployment adı gönderilir.

## Agent iş bölümü

1. **Dependency impact analyst**: değişen helper adlarını ve business kanıtlarını
   inceler; doğrudan kanıtı varsayımdan ayırır.
2. **Behavior and compatibility analyst**: diff'in olası davranış ve API
   uyumluluğu etkisini değerlendirir.
3. **Release risk analyst**: risk ve doğrulama adımlarını önerir.
4. **Synthesis**: uzman yanıtlarını tek verdict, kanıt özeti ve kontrol listesine
   dönüştürür.

İlk üç istek paralel yürütülür. Agent'lar çağrı grafiği, compiler veya test
sonuçlarının yerine geçmez; özellikle dolaylı/dinamik kullanımlarda sonucu
`inconclusive` olarak değerlendirin.

## Workflow değişiklikleri

- Varsayılan `main` dalı ve workflow dispatch tetiklemeleri core deposundaki
  `.github/workflows/deployment-impact.yml` içindedir.
- Başka bir branch'i deployment hedefi yapmak için workflow tetikleyicisini
  güncelleyin.
- Business deposu private yapılırsa checkout için yalnızca o depoda
  **Contents: Read** yetkili bir fine-grained token'ı GitHub Actions secret'ına
  ekleyin ve workflow checkout adımına bağlayın.
- Gerçek deployment'a bağlamadan önce entegrasyon/e2e testleri ve manuel
  deployment onayı ekleyin. Bu demo deployment komutu çalıştırmaz.

## Yerel doğrulama

```powershell
python -m pip install -e ".[test]"
python -m pytest
```
