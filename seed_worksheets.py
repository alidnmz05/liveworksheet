import os
import django
import sys
import random

# Django ortamını başlat
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django baslatilamadi: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from apps.worksheets.models import Worksheet, WorksheetPage, Question, Subject

User = get_user_model()

def seed_database_300():
    print("🚀 300 Yapay Zeka Uyumlu Çalışma Kağıdı Tohumlama İşlemi Başlatıldı...")

    # 1. Yazar Kullanıcıyı Bul veya Oluştur
    author = User.objects.filter(is_superuser=True).first()
    if not author:
        author = User.objects.filter(role='teacher').first()
    if not author:
        author = User.objects.first()
    if not author:
        print("👤 Hiç kullanıcı bulunamadı, test öğretmeni oluşturuluyor...")
        author = User.objects.create_user(
            username='ogretmen',
            email='ogretmen@gmail.com',
            password='password123',
            first_name='Test',
            last_name='Öğretmen',
            role='teacher'
        )
        print("👤 ogretmen@gmail.com (Şifre: password123) kullanıcısı oluşturuldu.")

    # 2. Dersleri (Subject) Bul veya Oluştur
    subjects_data = [
        {"name": "Matematik", "icon": "fa-calculator"},
        {"name": "Türkçe", "icon": "fa-language"},
        {"name": "Fen Bilimleri", "icon": "fa-flask"},
        {"name": "İngilizce", "icon": "fa-globe"},
        {"name": "Fizik", "icon": "fa-bolt"},
        {"name": "Kimya", "icon": "fa-atom"},
        {"name": "Biyoloji", "icon": "fa-dna"},
        {"name": "Sosyal Bilgiler", "icon": "fa-landmark"},
    ]

    subjects = {}
    for item in subjects_data:
        subj, created = Subject.objects.get_or_create(name=item["name"], defaults={"icon": item["icon"]})
        subjects[item["name"]] = subj

    # Eski test amaçlı olanları temizleyelim (Clean slate)
    Worksheet.objects.filter(author=author).delete()

    # 3. Kategori ve Konu Havuzu (Şablonlar)
    subtopics_pool = {
        "Matematik": [
            ("Temel Toplama ve Çıkarma", "sayılar, işlemler, toplama, çıkarma, temel", 
             "10 + 20 işleminin sonucu kaçtır?", "30",
             "Matematikte toplama işleminin temel mantığını ve hayatımızdaki önemini kısaca açıklayınız.",
             "Toplama işlemi, iki veya daha fazla çokluğun bir araya getirilerek tek bir toplam değer elde edilmesidir. Alışveriş yaparken, para sayarken veya ölçüm yaparken günlük hayatımızda sürekli kullanırız."),
            ("Kesirler ve Ondalık Sayılar", "kesirler, ondalık, rasyonel sayılar, bölme", 
             "3/5 kesrinin 2 ile genişletilmiş hali nedir? (Format: a/b)", "6/10",
             "Bir pastanın 3/8'ini Ahmet, 2/8'ini Mehmet yemiştir. Geriye kalan pastanın oranını bulunuz ve nasıl hesapladığınızı açıklayınız.",
             "Geriye pastanın 3/8'i kalmıştır. Ahmet ve Mehmet toplamda 3/8 + 2/8 = 5/8 yemişlerdir. Pastanın tamamı 8/8 olduğundan geriye 8/8 - 5/8 = 3/8 kalır."),
            ("Türev ve İntegral Analizi", "türev, integral, calculus, analiz, limit", 
             "f(x) = x^3 fonksiyonunun x'e göre birinci türevi nedir?", "3x^2",
             "Türev kavramının fiziksel olarak ne anlama geldiğini bir hız-zaman ilişkisi üzerinden kısaca açıklayınız.",
             "Türev, bir değişkenin diğerine göre anlık değişim oranıdır. Örneğin, bir hareketlinin konum-zaman fonksiyonunun zamana göre türevi bize o hareketlinin anlık hızını verir."),
            ("Üslü ve Köklü Sayılar", "üslü sayılar, köklü sayılar, cebir, üs", 
             "2^5 üslü ifadesinin değeri kaçtır?", "32",
             "Üslü sayıların günlük hayatta çok büyük veya çok küçük değerleri ifade etmede (Örn: bilimsel gösterim) sağladığı kolaylıkları açıklayınız.",
             "Çok büyük veya çok küçük sayıları daha kısa ve okunabilir şekilde yazmamızı sağlar. Örneğin, ışık hızı veya hücre boyutları üslü sayılarla kolayca gösterilir."),
            ("Oran ve Orantı Kuralları", "oran, orantı, problem, denklem", 
             "Bir sınıftaki kızların erkeklere oranı 3/4'tür. 12 kız varsa kaç erkek vardır?", "16",
             "Doğru orantı ile ters orantı arasındaki temel farkı günlük hayattan birer örnekle açıklayınız.",
             "Doğru orantıda iki çokluk aynı anda artar veya azalır (Örn: Alınan elma miktarı ve ödenen ücret). Ters orantıda ise biri artarken diğeri azalır (Örn: İşçi sayısı arttıkça işin bitme süresi kısalır).")
        ],
        "Türkçe": [
            ("Zıt Anlamlı Kelimeler", "zıt anlam, kelimeler, dil bilgisi, kelime bilgisi", 
             "'Siyah' kelimesinin zıt anlamlısı nedir?", "beyaz",
             "'Sıcak' kelimesinin zıt anlamlısı olan kelimeyi bulunuz ve bu kelimeyle ilgili bir cümle kurunuz.",
             "Sıcak kelimesinin zıt anlamlısı soğuk kelimesidir. Cümle: Kış aylarında hava çok soğuk olur veya Soğuk su içtiği için boğazı ağrıdı."),
            ("Eş Anlamlı Kelimeler Sözlüğü", "eş anlam, anlamdaş, kelime bilgisi, türkçe", 
             "'Sözcük' kelimesinin eş anlamlısı nedir?", "kelime",
             "'Cevap' kelimesinin eş anlamlısı olan kelimeyi bulunuz ve bu kelimeyle ilgili bir cümle kurunuz.",
             "Cevap kelimesinin eş anlamlısı yanıt kelimesidir. Cümle: Sorduğum soruya çok hızlı bir yanıt verdi veya Sınavdaki tüm soruların yanıtları doğruydu."),
            ("Okuduğunu Anlama Alıştırmaları", "okuma, anlama, paragraf, hızlı okuma", 
             "Bir paragrafta yazarın iletmek istediği asıl düşünceye ne ad verilir?", "ana fikir|ana düşünce",
             "Okuduğunuz kitapların kelime dağarcığınıza ve hayal gücünüze katkılarını kısaca değerlendiriniz.",
             "Kitap okumak yeni kelimeler öğrenmemizi sağlar, cümle kurma becerimizi geliştirir ve olayları zihnimizde canlandırarak hayal gücümüzü zenginleştirir."),
            ("Noktalama İşaretleri ve Yazım Kuralları", "noktalama, yazım kuralları, imla, dil bilgisi", 
             "Tamamlanmış cümlelerin sonuna hangi noktalama işareti konur?", ".",
             "Soru işaretinin (?) ve ünlem işaretinin (!) cümlelerdeki işlevlerini ve aralarındaki farkı kısaca açıklayınız.",
             "Soru işareti, cevap gerektiren soru cümlelerinin sonuna konur. Ünlem işareti ise korku, sevinç, şaşkınlık gibi yüksek duyguları veya hitapları belirten cümlelerin sonuna konur.")
        ],
        "Fen Bilimleri": [
            ("Maddenin Hâlleri ve Değişimi", "madde, katı, sıvı, gaz, erime, donma", 
             "Suyun donma noktası kaç santigrat derecedir?", "0",
             "Maddenin katı, sıvı ve gaz halleri arasındaki moleküler boşluk farkını kısaca açıklayınız.",
             "Katı halde moleküller arası boşluk yok denecek kadar azdır ve düzenlidir. Sıvı halde boşluk katıya göre daha fazladır ve moleküller serbest hareket eder. Gaz halinde ise boşluk en üst seviyededir."),
            ("Hücre ve Organellerin Görevleri", "biyoloji, hücre, organel, mitokondri", 
             "Hücrenin enerji santrali olarak bilinen organel hangisidir?", "mitokondri|mitochondria",
             "Bitki hücresi ile hayvan hücresi arasındaki en temel iki farkı açıklayınız.",
             "Bitki hücresinde hücre çeperi (duvarı) ve kloroplast bulunurken, hayvan hücresinde bunlar bulunmaz. Ayrıca bitki hücreleri köşeli, hayvan hücreleri ise oval yapıdadır."),
            ("Güneş Sistemi ve Gezegenler", "güneş, gezegenler, uzay, gök bilimi", 
             "Güneş sistemindeki en büyük gezegen hangisidir?", "Jüpiter|jupiter",
             "Güneş ve Ay tutulmalarının nasıl gerçekleştiğini kısaca karşılaştırarak açıklayınız.",
             "Güneş tutulmasında Ay, Dünya ile Güneş arasına girerek Güneş ışınlarını engeller. Ay tutulmasında ise Dünya, Güneş ile Ay arasına girerek gölgesini Ay'ın üzerine düşürür.")
        ],
        "İngilizce": [
            ("Simple Present Tense Exercises", "english, ingilizce, grammar, present simple", 
             "He _____ (go) to school everyday.", "goes",
             "Write a short paragraph in English about your daily routine (at least 3 sentences using Present Simple).",
             "I wake up at 7 o'clock in the morning. I have a healthy breakfast with my family. Then, I go to school by bus."),
            ("Vocabulary Building and Collocations", "vocabulary, words, collocations, english", 
             "What is the synonym of the word 'Big'?", "large|huge",
             "Why is learning a foreign language important in today's globalized world? Explain briefly.",
             "Learning a foreign language allows us to communicate with people from different countries, understand new cultures, and find better career opportunities in a globalized world.")
        ],
        "Fizik": [
            ("Newton'un Hareket Yasaları", "fizik, newton, kuvvet, ivme, dinamik", 
             "F = m.a formülündeki 'a' harfi hangi fiziksel niceliği temsil eder?", "ivme|acceleration",
             "Newton'un Etki-Tepki Yasasını günlük hayattan bir örnek vererek kısaca açıklayınız.",
             "Her etkiye karşı eşit ve zıt yönde bir tepki oluşur. Örneğin bir topu duvara fırlattığımızda duvarın topa uyguladığı tepki kuvveti sayesinde top geri seker veya yolda yürürken ayağımızla toprağı iteriz toprak da bizi ileri iter."),
            ("Elektriksel Alan ve Gauss Yasası", "fizik, gauss, elektrik, manyetizma, elektromanyetizma", 
             "Noktasal bir yükün etrafındaki elektriksel alan formülündeki katsayı sabitinin adı nedir?", "Coulomb sabiti|coulomb",
             "Gauss Yasasının temel ifadesini tanımlayınız ve hangi durumlarda elektriksel alan hesabını kolaylaştırdığını yazınız.",
             "Gauss yasası, kapalı bir yüzeyden geçen net elektriksel akının, yüzeyin içindeki toplam yükün boşluğun elektriksel geçirgenliğine oranına eşit olduğunu belirtir. Küresel, silindirik veya düzlemsel gibi yüksek simetriye sahip yük dağılımlarında alanı bulmayı çok kolaylaştırır.")
        ],
        "Kimya": [
            ("Kimyasal Bağlar ve Türler", "kimya, bağlar, atom, iyonik, kovalent", 
             "Suyun kimyasal formülü nedir?", "H2O",
             "İyonik bağ ile kovalent bağ arasındaki farkı elektron alışverişi veya ortaklaşması üzerinden açıklayınız.",
             "İyonik bağ, metal ve ametal atomları arasında elektron alışverişi ile oluşur. Kovalent bağ ise ametal atomları arasında elektronların ortaklaşa kullanılmasıyla meydana gelir."),
            ("Asitler, Bazlar ve Tuzlar", "kimya, asit, baz, ph, tuzlar", 
             "Saf suyun pH değeri kaçtır?", "7",
             "Asitler ve bazlar arasındaki temel farkları belirterek her ikisine de günlük hayattan birer örnek veriniz.",
             "Asitlerin tadı ekşidir, turnusol kağıdını kırmızıya çevirirler ve pH değerleri 7'den küçüktür (Örn: Limon). Bazların tadı acıdır, ele kayganlık hissi verirler ve pH değerleri 7'den büyüktür (Örn: Sabun).")
        ],
        "Biyoloji": [
            ("Mitoz ve Mayoz Bölünme", "biyoloji, mitoz, mayoz, hücre, dna", 
             "İnsanda toplam kaç adet kromozom bulunur?", "46",
             "Mitoz bölünme ile mayoz bölünme arasındaki en temel iki farkı yazınız.",
             "Mitoz bölünme vücut hücrelerinde görülür ve kromozom sayısı sabit kalır (2n -> 2n). Mayoz bölünme üreme ana hücrelerinde görülür, kromozom sayısı yarıya iner (2n -> n) ve kalıtsal çeşitlilik oluşur."),
            ("DNA Yapısı ve Kalıtım Kuralları", "dna, kalıtım, genetik, biyoloji, mendel", 
             "DNA molekülünde Adenin bazının karşısına hangi baz gelir?", "Timin|T",
             "DNA molekülünün yapısını ve canlıların kalıtsal özelliklerini nesilden nesile nasıl aktardığını kısaca özetleyiniz.",
             "DNA, çift sarmallı bir yapıya sahip olup adenin, timin, guanin ve sitozin nükleotitlerinden oluşur. Canlının tüm genetik kodlarını barındırır ve hücre bölünmesi sırasında kendini eşleyerek bu bilgileri yeni nesillere hatasız aktarır.")
        ],
        "Sosyal Bilgiler": [
            ("Anadolu Uygarlıkları ve Kültür", "sosyal bilgiler, tarih, anadolu, uygarlıklar, eski çağ", 
             "Parayı bulan ilk Anadolu medeniyeti hangisidir?", "Lidyalılar|lidya",
             "Hititler ve Frigler'in Anadolu medeniyetler tarihindeki önemini kısaca karşılaştırarak yazınız.",
             "Hititler askeri açıdan güçlü bir imparatorluk kurup ilk yazılı antlaşma olan Kadeş Antlaşması'nı imzalamışlardır. Frigler ise tarım ve hayvancılığa büyük önem verip sert kanunlar çıkarmışlar ve tarım tanrıçası Kibele'ye tapmışlardır."),
            ("Coğrafya ve Ekonomik Faaliyetler", "coğrafya, iklim, tarım, ekonomi, sosyal", 
             "Türkiye'de çay tarımının en yoğun yapıldığı coğrafi bölge hangisidir?", "Karadeniz|karadeniz bölgesi",
             "Coğrafi konumun bir ülkenin iklimi, tarımı ve ekonomik faaliyetleri üzerindeki etkilerini açıklayınız.",
             "Bir ülkenin ekvatora olan uzaklığı ve denizlere göre konumu iklim kuşaklarını belirler. İklim doğrudan yetiştirilen tarım ürünlerini etkiler, bu da ticaret, sanayi ve turizm gibi temel ekonomik faaliyetleri şekillendirir.")
        ]
    }

    # Seviye ve Uyumlu Dersler
    level_subject_pairings = {
        "ilkokul": ["Matematik", "Türkçe", "Fen Bilimleri", "İngilizce"],
        "ortaokul": ["Matematik", "Türkçe", "Fen Bilimleri", "İngilizce", "Sosyal Bilgiler"],
        "lise": ["Matematik", "Türkçe", "İngilizce", "Fizik", "Kimya", "Biyoloji", "Sosyal Bilgiler"],
        "universite": ["Matematik", "İngilizce", "Fizik", "Kimya", "Biyoloji"]
    }

    # Çeşitlilik ekleri (300 tane farklı başlık üretmek için)
    title_variations = [
        "Kazanım Testi", "Çalışma Kağıdı", "Alıştırmaları", "Ev Ödevi Etkinliği", 
        "Konu Anlatım Çalışması", "Deneme Sınavı Soruları", "Sınıf İçi Değerlendirme Yaprağı", 
        "Pekiştirme Çalışması", "Ünite Sonu Tarama Testi", "Tekrar Alıştırmaları"
    ]

    total_created = 0
    levels = ["ilkokul", "ortaokul", "lise", "universite"]

    for i in range(1, 301):
        # 1. Seviyeyi döngüsel/rastgele seç
        level = levels[(i - 1) % len(levels)]
        
        # 2. Seviyeye uygun dersleri seç
        allowed_subjects = level_subject_pairings[level]
        subject_name = allowed_subjects[(i - 1) % len(allowed_subjects)]
        subject_obj = subjects[subject_name]

        # 3. Ders havuzundan uygun şablonu çek
        templates = subtopics_pool[subject_name]
        template = random.choice(templates)
        
        topic_title, base_tags, fill_q, fill_ans, open_q, open_ans = template

        # 4. Benzersiz Title üret
        variation = title_variations[(i - 1) % len(title_variations)]
        final_title = f"{level.capitalize()} {subject_name}: {topic_title} {variation} (Grup {((i-1)//10) + 1} - Soru {i})"
        
        description = f"{level.capitalize()} düzeyinde {subject_name} dersinin '{topic_title}' konusunu kapsayan, semantik analiz motoru ve yapay zeka ipuçları ile zenginleştirilmiş etkileşimli çalışma kağıdı."
        tags = f"{base_tags}, {level}, {subject_name.lower()}, test{i}"

        # 5. Kaydı Veritabanına Yaz
        worksheet, created = Worksheet.objects.get_or_create(
            title=final_title,
            defaults={
                "author": author,
                "description": description,
                "subject": subject_obj,
                "level": level,
                "language": "tr",
                "is_public": True,
                "tags": tags
            }
        )

        if created:
            # Sayfa Oluştur
            page = WorksheetPage.objects.create(
                worksheet=worksheet,
                order=1,
                page_width=794,
                page_height=1123
            )

            # Boşluk Doldurma Sorusu
            Question.objects.create(
                page=page,
                question_type=Question.TYPE_FILL_BLANK,
                order=1,
                label=fill_q,
                correct_answer=fill_ans,
                learning_objective=f"{topic_title} Tanımları",
                points=10,
                pos_x=15, pos_y=20, width=35, height=6
            )

            # Açık Uçlu NLP Değerlendirme Sorusu
            Question.objects.create(
                page=page,
                question_type=Question.TYPE_OPEN_ANSWER,
                order=2,
                label=open_q,
                correct_answer=open_ans,
                learning_objective=f"{topic_title} Derin Analiz",
                points=20,
                pos_x=15, pos_y=45, width=70, height=12
            )

            total_created += 1
            if total_created % 50 == 0:
                print(f"📉 {total_created} adet çalışma kağıdı başarıyla oluşturuldu...")

    print(f"\n🎉 Mükemmel! Veritabanında toplam {total_created} adet tamamen benzersiz, konu ve düzey uyumlu yapay zeka destekli çalışma kağıdı başarıyla oluşturuldu!")

if __name__ == "__main__":
    seed_database_300()
