
# Dir Sync
Dir Sync; bilgisayarınızdaki dosyaları, harici sabit diskinizle eşitlemenizi sağlar. Dilerseniz harici sabit disk yerine, bilgisayarınızdaki iki ayrı klasörü de eşitleyebilirsiniz.

Aşağıdaki video ile demoyu izleyebilirsin.
[![Facebook'taki videonun göreseli](https://scontent-ist1-1.xx.fbcdn.net/v/t15.5256-10/300819345_784912042628224_1018950493210215850_n.jpg?stp=dst-jpg_p180x540&_nc_cat=110&ccb=1-7&_nc_sid=ad6a45&_nc_eui2=AeG9UYgvJVikMgeTnHX6yMtpw6vJxV6SmEHDq8nFXpKYQY9iCqduoJAL5vssJcaAaeTU-mkTEJdK2MElz_HbBnLD&_nc_ohc=mPWG_k1naVUAX8-cUCK&_nc_ht=scontent-ist1-1.xx&oh=00_AT9Fc4tIMSrffB55fsYL2gYi0u85wKCd8wL3pmd1KywM6w&oe=630E2F49)](https://www.facebook.com/eren.mustafa.ozdal/posts/pfbid09ShhXqMyXyCLYDCEGnQ2358yVXDSpjZT4ax89nN28bgQ15TtCbJ711RZsjX1TgjEl)

## Özellikleri
✅ Bilgisayar'dan sabit diske veya sabit diskten bilgisayara; çift yönlü senkronizasyon yapar. Bu şekilde aynı harici sabit diskteki dosyaları birden fazla bilgisayarda kullanıyorsanız, sabit diskinizi aracı yaparak tüm bilgisayarlarınızı senkronize tutar.<br>
✅ Dosyaların son değişiklik zamanını kontrol eder. Yeni değişiklikleri diğer tarafa yansıtır.<br>
✅ Silme işlemlerinde geri dönüşüm klasörüne *(trash)* taşıma yapar. Bu klasör Dir Sync'in bulunduğu klasörde oluşturulur. 30 gün süreyle kendi geri dönüşüm klasöründe tutar. Ardından bilgisayarın geri dönüşüm kutusuna gönderir. Bu 30 günlük süre ayar dosyasından (`.env`) değiştirilebilir.<br>
✅ Dir Sync eğer harici sabit disk takılı değilse; çalışmaz.<br>
✅ Yaptığı tüm işlemlerin günlüklerini `logs` klasöründe gün gün tutar.

## Gereksinimler

- [Python](https://www.python.org/downloads) `>=3.9`
- [python-dotenv](https://pypi.org/project/python-dotenv) `~=0.20.0`
- [pipenv](https://pypi.org/project/pipenv) (isteğe bağlı, önerilir)

## Kurulum İşlem Adımları

### 1. Dir Sync'i İndirin
Dir Sync'in son sürümünü https://github.com/erenmustafaozdal/dir-sync/releases adresinden indirin.

### 2. Ayar Dosyasını Düzeltin
Dir Sync'i indirip, bilgisayarınızda istediğiniz yere çıkarıp yerleştirdiğinizde; `.envexample` dosyasını göreceksiniz. Bu dosya ayar dosyasının bir örneğidir. **Adını `.env` şeklinde değiştirin.** Dosyanın içeriğini aşağıdaki gibi bulacaksınız.

```
# bilgisayarda eşitlenecek klasörün yolu  
PC="C:\Users\kullanici\esitlenecek-klasör"  
# tercihen hard diskte eşitlenecek klasörün yolu  
DRIVE="D:\esitlenecek-klasör"  
# dosya ve klasörler geri dönüşümde kaç gün kalacak  
TRASH_DAY=30
```

Aşağıdaki açıklamalara göre ayarlamaları yapın.

| Ayar 	| Açıklama 	|
|---	|---	|
| PC 	| Bilgisayarınızdaki eşitlenecek klasörün yolu.<br>❗ Tırnaklar içine yazın. 	|
| DRIVE 	| Eşitleme yapılacak diğer klasörün yolu. Tercihen harici sabit diskinizdeki bir klasörü atayabilirsiniz.<br>❗ Tırnaklar içine yazın. 	|
| TRASH_DAY 	| Dosya ve/veya klasörler silindiğinde, Dir Sync geri dönüşüm klasöründe ne kadar kalacaklarını gün sayısı olarak yazın.<br>❗ Varsayılan olarak 30 gündür. 	|


### 3. Python Kurulumu
`3.9` veya daha yeni bir Python sürümünü bilgisayarınıza https://pypi.org/project/pipenv adresinden indirip kurun.

### 4. Pipenv Kurulumu
Dir Sync'e özel bir sanal ortam kurmanızı tavsiye ederim. Eğer bilgisayarınızda daha sonradan geliştirme yapacaksanız veya başka python programları kullanacaksanız versiyon çakışmalarının önüne bu şekilde geçmiş olursunuz.
Pipenv kurulumu için bilgisayarınızda komut istemini *(CMD)* açın ve aşağıdaki komutu çalıştırın.
```python
pip install pipenv
```

### 5. Bağımlılıkları Yükleyin

#### 5.1 Eğer Pipenv Kurduysanız
Dir Sync'i indirip, sıkıştırılmış dosyadan nereye çıkardıysanız; o klasöre gidin. Dir Sync'in bulunduğu klasörde komut istemini açın ve aşağıdaki komutu çalıştırın.
```python
pipenv install
```
Bu komut sizin için sanal bir ortam oluşturacak ve tüm bağımlılıkları yükleyecek.

#### 5.2 Sistemde Kurulu Python İle
Bilgisayarınızda ayrı bir çalıştırma ortamı olmadan, sizin kurduğunuz Python üzerinden de Dir Sync'i kullanabilirsiniz. Bunun için öncelikle Dir Sync'in bulunduğu klasörde komut istemini açın ve aşağıdaki komutu çalıştırın.
```python
pip install -r requirements.txt
```

### 6. Dir Sync'i Çalıştırın

#### 6.1 Pipenv İle
Öncelikle `pipenv.exe` dosyasının bilgisayarındaki konumunu bulmamız gerekiyor. Aşağıdaki adreste `< >` işaretleri arasında size özel yerleri düzelterek bilgisayarınızdaki klasöre gidin.
```
C:\Users\<kullanıcı adın>\AppData\Local\Programs\Python\<Python versiyon klasörü>\Scripts\pipenv.exe
```
Örneğin pipenv.exe sizin için `C:\Users\eren\AppData\Local\Programs\Python\Python39\Scripts\pipenv.exe` konumunda olduğunu kabul edelim. O zaman siz Dir Sync'i aşağıdaki komut ile çalıştırabilirsiniz.

❗ Aşağıdaki komutu Dir Sync'in bulunduğu klasörde komut istemini açarak çalıştırmalısınız.

```python
C:\Users\eren\AppData\Local\Programs\Python\Python39\Scripts\pipenv.exe run python main.py
```

#### 6.2 Pipenv Olmadan
Dir Sycn'i sisteminizde yüklü Python ortamında çalıştırmak için aşağıdaki komutu kullanmalısınız.

❗ Aşağıdaki komutu Dir Sync'in bulunduğu klasörde komut istemini açarak çalıştırmalısınız.

```python
python main.py
```

---

> ❗❗❗ Yukarıdaki komutlar ile Dir Sync'i çalıştırdınız. Ancak sadece bir defa... Her şey bitti. 😀 Şimdi ise aşağıdaki yöntemle çalıştırdığınız komutu Windows'ta zamanlayacağız. Sürekli çalışmaya başlayacak.

### 7. Dir Sync'i Zamanlayın
Windows'ta **Görev Zamanlayıcı**'yı açın. Yeni bir görev oluşturun. İsim ve açıklama bölümüne istediğinizi yazabilirsiniz. Aşağıdaki sekme ve alanları doldurun.

- **Tetikleyiciler Sekmesi**
    - Yeni tuşu ile bir tetikleyici oluşturun. Burada isteğe bağlı seçim yapabilirsiniz. Ben *"Başlatılırken"* seçimi yaptım. Altından da 5 dakikada bir yenilemesini istedim. Yani bilgisayarım açıldığında Dir Sync çalışmaya başlayacak ve 5 dakikada bir tekrar tekrar çalışacak.
- **Eylemler Sekmesi**
    - Yeni tuşu ile bir eylem oluşturun. Yukarıdaki çalıştırma komutunuzu *"Program/Komut dosyası:"* alanına yapıştırın. Tamam deyin. *"Program bağımsız değişkenlerle çalışacak"* gibi bir uyarıya *"Evet"* diyerek tamamlayın.

❗ **Koşullar** ve **Ayarlar** sekmelerinde de kendinize göre ayarlamalar yapabilirsiniz.

---

> 😎 Artık programınız hazır. Dir Sync istediğiniz ayarlara göre çalışacak. Eğer harici sabit diskiniz takılı değilse, herhangi bir işlem yapmayacak.

## Hata, Sorun Bildirme ve Destek
Hata ve sorun bildirmek için https://github.com/erenmustafaozdal/dir-sync/issues adresinde konu açıp bilgi verebilirsiniz. Hata ve sorun bildirirken `logs` klasöründeki dosyalardan hata veren çıktıyı da paylaşmayı unutmayın.

Bir sınıf öğretmeni tarafından geliştirilen Dir Sync programına sen de katkı sağlayabilirsin.

- Daha sade bir metot...
- Daha işlevsel bir özellik...
- Daha iyi bir veritabanı yapılandırması...
- Bir hata düzeltme...

Tek yapman gereken Dir Sync'i fork'layıp, gerekli değişiklikleri yapıp, sonrasında pull request ile birleştirme isteği göndermek. Hepsi bu kadar 😊. Şimdiden desteğin için teşekkürler 🙏.
