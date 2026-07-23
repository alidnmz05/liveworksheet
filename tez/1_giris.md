# 1. GİRİŞ

Bu bölümde, çalışmanın temelini oluşturan eğitim teknolojilerindeki dijital dönüşüm süreçleri, modern eğitim yönetim sistemlerindeki otomatik ölçme-değerlendirme modüllerinin önemi, geleneksel değerlendirme yöntemlerinin yapısal ve semantik sınırlılıkları ile bu çalışmada geliştirilen yapay zekâ destekli hibrit çözümün konusu, problemi, amacı, önemi ve yenilikçi yönleri ele alınmaktadır. Raporun genel organizasyonu da bu bölümün sonunda ayrıntılı olarak açıklanmaktadır.

## 1.1. Çalışmanın Konusu

Bilgi ve iletişim teknolojilerinde son yıllarda yaşanan ivmeli gelişmeler, toplumsal ve kurumsal yapıların yanı sıra eğitim-öğretim süreçlerini de köklü bir değişime uğratmıştır. Geleneksel sınıf içi yüz yüze eğitim modelleri, yerini büyük ölçüde karma (blended) ve tamamen web tabanlı e-öğrenme modellerine bırakmıştır. Eğitimde dijitalleşme olarak adlandırılan bu dönüşüm; coğrafi engelleri ortadan kaldırarak eğitimde fırsat eşitliğini desteklemekte ve öğrencilerin kendi öğrenme hızlarında (asenkron) ilerlemelerine imkân tanımaktadır. Öğrenme Yönetim Sistemleri (LMS - Learning Management Systems) bu dönüşümün merkezinde yer alarak öğrenim materyallerinin dağıtımı, takibi ve notlandırılmasında kritik bir rol oynamaktadır.

Eğitim süreçlerinin dijitalleşmesindeki en önemli basamaklardan biri de, öğrencilerin edindikleri teorik kazanımları pratik uygulamalarla pekiştirmelerini sağlayan etkileşimli çalışma kağıtlarıdır (worksheets). Bu çalışma kağıtları, öğrencilerin anlık olarak sorulara yanıt vermesine ve kendi öğrenme süreçlerini izlemelerine olanak tanımaktadır.

Bu çalışmanın konusunu; öğretmenlerin zengin multimedya öğeleriyle (YouTube/Vimeo videoları, ses dosyaları, metinden sese dönüştürme sistemleri) donatılmış etkileşimli çalışma kağıtları tasarlayabildiği, sanal sınıflar (Classroom) kurarak öğrencilerini takip edebildiği ve ödev (Assignment) atayabildiği bütüncül bir e-öğrenme platformunun tasarlanması ve gerçekleştirilmesi oluşturmaktadır. Çalışmanın asıl odak noktası ise; öğrencilerin platform üzerinden gönderdiği açık uçlu (open-ended) ve kısa cevaplı serbest metin yanıtlarını, klasik karakter eşleşmesinin ötesine geçerek **semantik (anlamsal) düzeyde** otomatik olarak değerlendiren, dil bilimsel kurallarla mantıksal çelişkileri analiz eden ve branş bazlı kavram yanılgılarını (concept misconceptions) saptayabilen yapay zekâ destekli hibrit bir değerlendirme motorunun sisteme entegrasyonudur [5, 20]. Ayrıca platform, öğrenci kazanımlarını takip ederek zayıf yönlerini geliştirmek üzere kişiselleştirilmiş materyal önerileri sunan akıllı bir ders asistanı (AI Tutor) barındırmaktadır.

## 1.2. Problemin Tanımı

E-öğrenme platformlarında çoktan seçmeli, eşleştirmeli, sürükle-bırak veya doğru-yanlış gibi yapılandırılmış soru tipleri bilgisayar sistemleri tarafından kolaylıkla ve anında değerlendirilebilirken; serbest metin formatındaki açık uçlu yanıtların otomatik puanlanması ciddi bir sınırlılık teşkil etmektedir [6]. Literatürde ve mevcut ticari/akademik eğitim araçlarında karşılaşılan temel problemler şu şekilde detaylandırılabilir:

*   **Harfi Harfine Eşleşme (Exact-Match) Sınırlılığı ve Yanlış Negatif Kararlar:** Geleneksel otomatik değerlendirme modülleri, öğrencinin yanıtı ile öğretmenin sisteme girdiği referans doğru cevabı karakter bazlı (birebir) karşılaştırır [8]. Bu katı yaklaşım; eş anlamlı kelime kullanımlarını, farklı kelime dizilimlerini veya Türkçe gibi zengin çekim ve yapım eklerine sahip sondan eklemeli bir dilin morfolojik varyasyonlarını tolere edememektedir. Sonuç olarak, anlamsal açıdan tamamen doğru ve yeterli olan bir öğrenci yanıtı, referans cevapla birebir örtüşmediği için sistem tarafından yanlış kabul edilmektedir. Bu durum, ölçme güvenilirliğini zedeleyerek yüksek oranda "yanlış negatif" sonuçlar üretmektedir.
*   **Mantıksal Çelişkilerin Yakalanamaması:** Sadece kelime benzerliğine veya yüzeysel semantik vektör yakınlığına odaklanan yapay zekâ modelleri, olumsuzluk eklerini veya zıt anlamlı kelimeleri gözden kaçırabilmektedir. Örneğin; doğru cevabın *"Hücre çekirdeği kalıtımı kontrol eder"* olduğu bir soruda öğrencinin *"Hücre çekirdeği kalıtımı kontrol **etmez**"* yazması durumunda, iki cümle arasındaki kelime benzerliği ve vektör yakınğlığı çok yüksek çıkmasına rağmen anlam tamamen zıttır. Geleneksel sistemler bu tür kritik mantıksal çelişkileri ayırt edememekte ve yanlış bir yanıta tam puan verebilmektedir [20].
*   **Akademik Kavram Yanılgılarının (Concept Misconception) Saptanamaması:** Öğrenciler, fen bilimleri, matematik veya sosyal bilgiler gibi branşlarda birbirine yakın veya birbiriyle ilişkili bilimsel kavramları sıklıkla karıştırmaktadır (örneğin; *"mitokondri"* yerine *"ribozom"* yazılması, *"mitoz"* yerine *"mayoz"* denilmesi, *"ivme"* yerine *"hız"* kavramının kullanılması). Mevcut sistemler bu tür hataları sadece genel bir anlamsal uzaklık olarak görmekte; hatanın tam olarak hangi bilimsel kavramın yanlış kullanımından kaynaklandığını belirleyemediği için öğrenciye yönlendirici, öğretici ve akademik bir geri bildirim sunamamaktadır.
*   **Öğretmenlerin Değerlendirme Yükü ve Zaman Maliyeti:** Özellikle kalabalık sınıflarda yüzlerce öğrencinin açık uçlu yanıtlarını tek tek okumak, adil bir şekilde puanlamak ve her birine yapıcı geri bildirimler hazırlamak öğretmenler için çok büyük bir zaman ve emek kaybına yol açmaktadır. Bu durum, biçimlendirici değerlendirme (formative assessment) süreçlerinin sıklığını ve niteliğini sınırlandırmaktadır.

## 1.3. Çalışmanın Amacı ve Önemi

Bu çalışmanın temel amacı; eğitimde ölçme-değerlendirme süreçlerini dijitalleştirirken öğretmenlerin sınav değerlendirme yükünü en aza indiren, öğrencilere ise anında, adil ve pedagojik açıdan nitelikli geri bildirimler sağlayan yapay zekâ destekli bütüncül bir e-öğrenme platformu tasarlamak ve gerçekleştirmektir.

Çalışmanın akademik ve pratik açıdan önemini ortaya koyan unsurlar şu şekilde sıralanabilir:

1.  **Ölçme Değerlendirmede Güvenilirlik ve Adalet:** Geliştirilen semantik ve dil bilimsel analiz altyapısı sayesinde, öğrencilerin özgün cümlelerle ifade ettiği doğru yanıtların "harfi harfine eşleşmediği" gerekçesiyle elenmesini (yanlış negatif kararları) önlemek ve adil bir notlandırma sağlamak.
2.  **Pedagojik Geri Bildirim Süreçlerinin Hızlandırılması:** Öğrencilere sadece sayısal bir not vermek yerine, yaptıkları yazım hatalarını, mantıksal çelişkileri ve kavram yanılgılarını açıklayan anlık geri bildirimler sunarak öğrenme sürecini etkin bir şekilde desteklemek.
3.  **Öğretmenlerin Operasyonel İş Yükünün Azaltılması:** Açık uçlu ödevleri ve çalışma kağıtlarını el ile puanlama yükünü ortalama %85 oranında azaltarak, öğretmenlerin idari yükünü hafifletmek ve doğrudan öğrenci rehberliğine odaklanmalarına katkıda bulunmak.
4.  **Kişiselleştirilmiş Öğrenme Patikalarının İnşası:** Geliştirilen yapay zekâ çalışma asistanı (AI Tutor) vasıtasıyla, her öğrencinin eksik olduğu kazanımlara göre otomatik olarak özelleştirilmiş ek çalışma materyalleri sunarak bireysel öğrenme süreçlerini yönlendirmek.

## 1.4. Önerilen Çözüm Yaklaşımı

Belirtilen problemleri çözmek amacıyla, bu çalışmada yapay zekâ tabanlı, çok katmanlı ve hibrit bir otomatik değerlendirme boru hattı (pipeline) geliştirilmiştir. Sunucu altyapısında Django framework [11] ve Python tabanlı Doğal Dil İşleme (NLP) kütüphaneleri kullanılmıştır.

Önerilen çözüm yaklaşımının ana aşamaları şu şekildedir:

1.  **Cevap Ön İşleme Süreci:** Öğrenci yanıtları ve referans doğru cevaplar noktalama işaretlerinden temizlenir, küçük harfe dönüştürülür ve morfolojik analiz için hazırlanır.
2.  **Linguistik Çelişki Denetimi:** Türkçe morfolojisine uygun olarak tasarlanan kural tabanlı bir algoritmayla fiillerdeki olumsuzluk ekleri (`-mıyor`, `-medi`, `-mez` vb.) ve yapılandırılmış zıt anlam sözlüğü taranarak iki cümle arasında mantıksal çelişki olup olmadığı denetlenir.
3.  **Teorik Kavram Yanılgısı Denetimi:** Fizik, kimya, biyoloji, matematik gibi branşlara özel kurgulanan "Rakip Kavram Grupları" (Theory Groups) üzerinden, öğrencinin doğru kavram yerine gruptaki yanlış bir terimi kullanıp kullanmadığı küme analizleriyle incelenir.
4.  **Semantik Vektörleme ve Benzerlik Analizi:** Cümleler, `paraphrase-multilingual-MiniLM-L12-v2` Sentence Transformer modeliyle [3] 384 boyutlu yoğun vektörlere dönüştürülür ve aralarındaki Kosinüs Benzerliği [8] hesaplanır.
5.  **Bulanık Eşleştirme (Fuzzy Matching) Entegrasyonu:** Kısa cevaplı kelimelerdeki harf hatalarını yakalamak için Gestalt Pattern Matching [9] tabanlı fuzzy skoru hesaplanır [16] ve semantik skorla melezlenerek nihai hibrit puan elde edilir.
6.  **Kazanım Bazlı Öneri (AI Tutor):** Öğrencinin eksik olduğu konu etiketlerine (`learning_objective`) göre Alpine.js tabanlı chatbot [17] ve Pandas tabanlı öneri motoru çalışarak öğrenciye en uygun çalışma kağıtlarını listeler.

Önerilen hibrit yapay zekâ değerlendirme motorunun boru hattı (pipeline) akış şeması Şekil 1.1'de gösterilmiştir.

![Şekil 1.1: Önerilen Hibrit Yapay Zekâ Değerlendirme Motorunun Boru Hattı (Pipeline) Akış Şeması](gorseller/evaluation_flowchart.png)

## 1.5. Çalışmanın Yenilikçi Yönleri

Geliştirilen platform, mevcut eğitim araçlarına kıyasla akademik ve teknik açıdan birçok yenilikçi yön barındırmaktadır:

*   **Semantik-Linguistik Hibridizasyon:** Derin öğrenme tabanlı Sentence Transformers modellerinin [3] zayıf noktası olan olumsuzluk/mantıksal çelişki durumları, morfolojik regex kuralları ve zıt anlam sözlüğüyle çözülerek hibrit bir yapı kurulmuştur.
*   **Küme Tabanlı Kavram Yanılgısı Tespiti:** Sadece metin benzerliği hesaplamakla kalmayıp, ders müfredatındaki rakip terim grupları üzerinden pedagojik kavram yanılgılarını akademik düzeyde raporlayan özgün bir algoritmaya sahiptir.
*   **Uzunluğa Duyarlı Dinamik Eşikleme:** Tek veya iki kelimelik kısa cevaplar ile uzun cümleler arasındaki anlam yoğunluğu farkı gözetilerek değerlendirme eşik değerinin dinamik olarak ayarlanması sağlanmıştır.
*   **Taslak Kaydetme ve Bütüncül LMS:** Öğrencilerin yarıda bıraktıkları ödevleri veritabanında taslak (draft) olarak koruyabildiği, öğretmenlerin ise anında otomatik puanlamayı denetleyip el ile güncelleyebildiği entegre bir sınıf yönetim modülü mevcuttur.
*   **Çok Dilli Semantik Analiz Yeteneği:** Çok dilli ortak uzayda eğitilmiş dil modeli sayesinde [7, 15], farklı dillerdeki yanıtlar arasında dahi anlamsal yakınlık ölçülebilmekte ve platform 11 farklı dilde tamamen yerelleştirilmiş olarak çalışmaktadır.

## 1.6. Raporun Organizasyonu

Bu mezuniyet projesi raporu toplam altı ana bölümden oluşmaktadır:

*   **Bölüm 1 (Giriş):** Çalışmanın konusu, problemi, amacı, önemi, önerilen çözüm yaklaşımı ve yenilikçi yönleri hakkında genel bilgiler sunulmaktadır.
*   **Bölüm 2 (Literatür Çalışmaları):** E-öğrenme platformları, otomatik ölçme-değerlendirme yöntemleri, serbest metin analizi, doğal dil işleme tabanlı semantik benzerlik yaklaşımları (BERT, Sentence Transformers) ve literatürdeki eksiklikler ele alınmaktadır.
*   **Bölüm 3 (Metod ve Materyal):** Geliştirme ortamı, kullanılan teknolojiler (Django [11], SQLite/PostgreSQL [19], Tailwind CSS [18], Alpine.js [17], Sentence Transformers [3]), fonksiyonel/fonksiyonel olmayan gereksinimler, sistem mimarisi, ER diyagramı, kullanıcı rolleri ve akışları ile yapay zekâ değerlendirme algoritmalarının pseudocode tasarımları detaylandırılmaktadır.
*   **Bölüm 4 (Deneysel Çalışmalar):** Test senaryolarının kurgulanması, değerlendirme yöntemlerinin karşılaştırmalı doğruluk analizleri, çelişki/kavram yanılgısı algılama başarıları, zaman performansı testleri, diller arası eşleşme denemeleri ve kullanıcı arayüz ekranları sunulmaktadır.
*   **Bölüm 5 (Sonuç ve Öneriler):** Proje çıktılarından elde edilen akademik ve pratik kazanımlar özetlenmekte, çalışmanın sınırlılıkları tartışılmakta ve gelecekte yapılabilecek geliştirmeler önerilmektedir.
*   **Bölüm 6 (Kaynaklar):** Raporda atıfta bulunulan tüm akademik yayınlar, kitaplar, standartlar ve kütüphane dokümantasyonları listelenmektedir.
*   **Ekler:** Yapay zekâ modülü başlatma kodları, ilişkisel veritabanı modelleri, AI Tutor view mekanizmaları, ek ekran görüntüleri ve test senaryosu verileri yer almaktadır.
*   **Özgeçmiş:** Yazarların akademik geçmişleri, çalışma alanları ve kişisel bilgileri bu bölümde yer almaktadır.
