import logging
import re
import os

logger = logging.getLogger(__name__)

# Modeli modül seviyesinde başlatıyoruz (sadece bir kez RAM'e yüklenir)
try:
    from sentence_transformers import SentenceTransformer, util
    # 470MB'lık akademik NLP modelimiz. İndirildiği için artık anında çalışır.
    ST_MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    AI_ENABLED = True
except Exception as e:
    logger.error(f"Yapay zeka modeli yüklenemedi: {e}")
    ST_MODEL = None
    AI_ENABLED = False

def detect_contradiction(text1: str, text2: str):
    """
    Türkçe cümlelerde mantıksal çelişki (zıt anlam veya olumsuzluk) tespiti yapar.
    Örnek: "büyük bir şehirdir" ve "küçük bir şehirdir" veya "şehir değildir".
    Döndürür: (çelişki_var_mı: bool, açıklama: str)
    """
    words1 = re.findall(r'\b\w+\b', text1.lower())
    words2 = re.findall(r'\b\w+\b', text2.lower())
    
    has_deyil1 = any(w in ('değil', 'değildir') for w in words1)
    has_deyil2 = any(w in ('değil', 'değildir') for w in words2)
    
    def extract_verbs_polarity(words_list):
        verbs = {}
        for w in words_list:
            # -mıyor / -miyor
            m = re.match(r'^(\w+)(mıyor|miyor|muyor|müyor|mıyo|miyo|muyo|müyo)$', w)
            if m:
                verbs[m.group(1)] = 'neg'
                continue
            m = re.match(r'^(\w+)(ıyor|iyor|uyor|üyor|ıyo|iyo|uyo|üyo)$', w)
            if m:
                stem = m.group(1)
                if stem not in verbs:
                    verbs[stem] = 'pos'
                continue
                
            # -madı / -medi
            m = re.match(r'^(\w+)(madı|medi|madılar|mediler)$', w)
            if m:
                verbs[m.group(1)] = 'neg'
                continue
            m = re.match(r'^(\w+)(dı|di|du|dü|tı|ti|tu|tü|dılar|diler|tılar|tiler)$', w)
            if m:
                stem = m.group(1)
                if not stem.endswith('ma') and not stem.endswith('me'):
                    if stem not in verbs:
                        verbs[stem] = 'pos'
                continue

            # -maz / -mez
            m = re.match(r'^(\w+)(maz|mez|mazlar|mezler)$', w)
            if m:
                verbs[m.group(1)] = 'neg'
                continue
            m = re.match(r'^(\w+)(ar|er|ır|ir|ur|ür|arlar|erler)$', w)
            if m:
                stem = m.group(1)
                if stem not in verbs:
                    verbs[stem] = 'pos'
                continue
        return verbs

    verbs1 = extract_verbs_polarity(words1)
    verbs2 = extract_verbs_polarity(words2)
    
    for stem in verbs1:
        if stem in verbs2:
            if verbs1[stem] != verbs2[stem]:
                return True, f"Fiil olumsuzluk çelişkisi: '{stem}' fiili bir tarafta olumlu, diğer tarafta olumsuz."

    ANTONYM_PAIRS = [
        ('büyük', 'küçük'),
        ('iyi', 'kötü'),
        ('doğru', 'yanlış'),
        ('var', 'yok'),
        ('evet', 'hayır'),
        ('sıcak', 'soğuk'),
        ('hızlı', 'yavaş'),
        ('yüksek', 'alçak'),
        ('kolay', 'zor'),
        ('erken', 'geç'),
        ('önce', 'sonra'),
        ('alt', 'üst'),
        ('iç', 'dış'),
        ('açık', 'kapalı'),
        ('taze', 'bayat'),
        ('fakir', 'zengin'),
        ('genç', 'yaşlı'),
        ('güzel', 'çirkin'),
        ('kalın', 'ince'),
        ('uzun', 'kısa'),
        ('ucuz', 'pahalı'),
        ('akıllı', 'deli'),
        ('pozitif', 'negatif'),
        ('artı', 'eksi'),
        ('doğu', 'batı'),
        ('kuzey', 'güney'),
        ('aktif', 'pasif'),
        ('yararlı', 'zararlı'),
        ('faydalı', 'zararlı'),
        ('temiz', 'kirli'),
        ('siyah', 'beyaz'),
        ('ak', 'kara'),
        ('gece', 'gündüz'),
        ('tatlı', 'acı'),
        ('cesur', 'korkak'),
        ('dost', 'düşman'),
    ]

    antonym_checked = False
    for a, b in ANTONYM_PAIRS:
        has_a1 = any(w.startswith(a) for w in words1)
        has_a2 = any(w.startswith(a) for w in words2)
        has_b1 = any(w.startswith(b) for w in words1)
        has_b2 = any(w.startswith(b) for w in words2)
        
        if (has_a1 and has_b2) or (has_b1 and has_a2):
            antonym_checked = True
            pol1 = 'A' if (has_a1 and not has_deyil1) or (has_b1 and has_deyil1) else 'B'
            pol2 = 'A' if (has_a2 and not has_deyil2) or (has_b2 and has_deyil2) else 'B'
            
            if pol1 != pol2:
                return True, f"Zıt anlam çelişkisi: '{a}' ve '{b}' kelimeleri zıt bağlamlarda kullanılmış."

    if not antonym_checked and has_deyil1 != has_deyil2:
        common = set(words1) & set(words2)
        if len(common) >= 1:
            return True, "Olumsuzluk çelişkisi: Cümlelerden biri 'değil' ile olumsuzlaştırılmış."

    return False, ""


def detect_theoretical_mismatch(text1: str, text2: str):
    """
    Teorik ve bilimsel kavramların birbirinin yerine yanlış kullanımı (kavram yanılgısı) durumunu inceler.
    Örnek: Referansta 'mitokondri' varken öğrencide 'mitokondri' olmayıp 'ribozom' veya 'kloroplast' olması.
    Döndürür: (mismatch_var: bool, aciklama: str)
    """
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))

    # Rakip Kavram Grupları (300 çalışma kağıdındaki tüm branş ve konuları kapsayan devasa akademik kütüphane)
    THEORY_GROUPS = [
        # --- BİYOLOJİ & FEN BİLİMLERİ ---
        # Organeller
        {'mitokondri', 'kloroplast', 'ribozom', 'lizozom', 'golgi', 'koful', 'sentrozom', 'çekirdek'},
        # Hücre Bölünmeleri
        {'mitoz', 'mayoz'},
        # Hücre Türleri
        {'bitki', 'hayvan'},
        # Üreme Hücreleri
        {'vücut', 'üreme', 'sperm', 'yumurta'},
        # DNA Nükleotitleri
        {'adenin', 'timin', 'guanin', 'sitozin', 'urasil'},

        # --- FİZİK ---
        # Newton Yasaları
        {'etki', 'tepki', 'eylemsizlik'},
        # Elektrik ve Manyetizma
        {'gauss', 'coulomb', 'amper', 'volt', 'ohm', 'faraday'},
        # Fiziksel Nicelikler
        {'hız', 'ivme', 'konum', 'kuvvet', 'kütle', 'ağırlık', 'iş', 'güç', 'enerji'},
        # Enerji Tipleri
        {'potansiyel', 'kinetik'},
        # İletkenlik
        {'iletken', 'yalıtkan'},
        # Zeminler
        {'mermer', 'çakıl', 'cam', 'toprak', 'tahta', 'pürüzlü', 'pürüzsüz'},

        # --- KİMYA ---
        # Maddenin Halleri
        {'katı', 'sıvı', 'gaz'},
        # Hal Değişimleri
        {'erime', 'donma', 'buharlaşma', 'yoğuşma'},
        # Kimyasal Karakterler
        {'asit', 'baz', 'tuz'},
        # Kimyasal Bağlar
        {'iyonik', 'kovalent', 'metalik'},
        # Karışım Çeşitleri
        {'homojen', 'heterojen'},

        # --- MATEMATİK ---
        # Temel İşlemler
        {'toplama', 'çıkarma', 'çarpma', 'bölme'},
        # Sayı Kümeleri ve Yapıları
        {'rasyonel', 'irrasyonel', 'tamsayı', 'doğal sayı', 'üslü', 'köklü'},
        # Orantı Çeşitleri
        {'doğru', 'ters'},
        # Kalkülüs
        {'türev', 'integral', 'limit'},

        # --- TÜRKÇE ---
        # Anlam İlişkileri
        {'eş anlam', 'zıt anlam', 'sesteş', 'anlamdaş'},
        # Paragrafta Anlam
        {'ana fikir', 'ana düşünce', 'yardımcı fikir'},
        # Noktalama İşaretleri
        {'nokta', 'virgül', 'soru işareti', 'ünlem işareti', 'iki nokta', 'noktalı virgül'},

        # --- İNGİLİZCE ---
        # İngilizce Zamanlar (Tenses)
        {'present', 'past', 'future', 'continuous'},
        # Kelime Yapısı
        {'synonym', 'antonym'},

        # --- SOSYAL BİLGİLER & TARİH & COĞRAFYA ---
        # Anadolu Uygarlıkları
        {'hititler', 'frigler', 'lidyalılar', 'urartular', 'iyonlar'},
        # Türkiye'nin Coğrafi Bölgeleri
        {'karadeniz', 'akdeniz', 'ege', 'marmara', 'iç anadolu', 'doğu anadolu', 'güneydoğu anadolu'},
        # Astronomi
        {'güneş', 'ay'}
    ]

    for group in THEORY_GROUPS:
        # Referansta bu gruptan hangi kelimeler var?
        ref_terms = group & words1
        if ref_terms:
            # Öğrenci cevabında referanstaki doğru kelimelerden HİÇBİRİ yoksa
            if not (ref_terms & words2):
                # Ama öğrenci cevabında bu gruptan BAŞKA bir yanlış kelime varsa!
                wrong_terms = (group - ref_terms) & words2
                if wrong_terms:
                    correct_str = ", ".join(f"'{r}'" for r in ref_terms)
                    wrong_str = ", ".join(f"'{w}'" for w in wrong_terms)
                    return True, f"Teorik Kavram Yanılgısı: Beklenen bilimsel kavram {correct_str} iken, bunun yerine yanlışlıkla {wrong_str} kavramını kullandınız."

    return False, ""


def evaluate_open_answer(reference_answer: str, student_answer: str, threshold: float = 0.65):
    """
    Öğrenci cevabını Derin Öğrenme (Deep Learning) Vektör Analizi ile değerlendirir.
    Akademik düzeydedir. Kelimeler aynı olmasa bile anlamsal bağlam eşleşirse doğru kabul eder.
    """
    if not reference_answer or not student_answer:
        return {'ai_score': 0.0, 'is_correct': False, 'feedback': 'Cevap boş.'}
    
    # Noktalama işaretlerini ve fazla boşlukları temizleyelim (cümle içindeki anlamı bozmamak için)
    ref_clean = reference_answer.strip().lower()
    stu_clean = student_answer.strip().lower()

    if ref_clean == stu_clean:
        return {'ai_score': 1.0, 'is_correct': True, 'feedback': 'Mükemmel eşleşme ile doğru cevap.'}

    # 0. Mantıksal Çelişki (Zıt Anlam ve Olumsuzluk) Kontrolü
    contradiction_detected, contradiction_reason = detect_contradiction(ref_clean, stu_clean)
    if contradiction_detected:
        return {
            'ai_score': 0.30,
            'is_correct': False,
            'feedback': f"Cevabınız, beklenen doğru yargıyla mantıksal olarak çelişiyor ({contradiction_reason})."
        }

    # 0.5. Teorik/Bilimsel Kavram Yanılgısı Kontrolü
    mismatch_detected, mismatch_reason = detect_theoretical_mismatch(ref_clean, stu_clean)
    if mismatch_detected:
        return {
            'ai_score': 0.35,
            'is_correct': False,
            'feedback': mismatch_reason
        }

    if AI_ENABLED:
        try:
            # 1. NLP ile Cümle/Kelime Vektörlerini (Embeddings) Oluşturma
            emb1 = ST_MODEL.encode(ref_clean)
            emb2 = ST_MODEL.encode(stu_clean)
            
            # 2. Vektörler arasındaki Kosinüs Benzerliğini (Cosine Similarity) Hesaplama
            cosine_scores = util.cos_sim(emb1, emb2)
            similarity = float(cosine_scores[0][0])
            
            # Eğer kısa bir cevapsa ve harf hatası varsa (krxmozom vs kromozom), 
            # Derin öğrenme modeli kelimeyi tanımayabilir. Bu gibi typolar için "hybrid" yaklaşım uygulayalım.
            from difflib import SequenceMatcher
            fuzzy_ratio = SequenceMatcher(None, ref_clean, stu_clean).ratio()
            
            # NLP ve FuzzyLogic ortalamasını alıp veya en yüksek olanı seçip harf/anlam melezlemesi yapıyoruz
            final_similarity = max(similarity, fuzzy_ratio)
            
            # 3. Sonuç Değerlendirmesi
            # Eğer öğretmenin referans cevabı kısa ise (tek kelime veya iki kelime) 
            word_count = len(ref_clean.split())
            if word_count <= 2:
                match_threshold = 0.75
            else:
                match_threshold = threshold
                
            is_correct = final_similarity >= match_threshold
            
            if final_similarity >= 0.90:
                feedback = "Harika! Cümlenin anlamı beklenen bağlamla kusursuz örtüşüyor."
            elif is_correct:
                feedback = "Kelime farklılıkları veya harf hataları olsa da semantik (anlamsal) olarak doğru kabul edildi."
            elif final_similarity >= match_threshold - 0.20:
                feedback = "Cevabın konu ile kısmen bağdaşıyor ancak beklenen asıl yargıyı içermiyor."
            else:
                feedback = "Cevabının anlamı, öğretmenin beklediği bağlamdan tamamen farklı."

            return {
                'ai_score': round(final_similarity, 2),
                'is_correct': is_correct,
                'feedback': feedback
            }
        except Exception as e:
            logger.error(f"Tahmin sırasında hata: {e}")
            pass

    # AI Yüklenemezse her ihtimale karşı Fallback 
    from difflib import SequenceMatcher
    sim = SequenceMatcher(None, ref_clean, stu_clean).ratio()
    return {
        'ai_score': round(sim, 2),
        'is_correct': sim >= 0.70,
        'feedback': 'Sistem standart denetim modunda değerlendirdi.' if sim >= 0.70 else 'Hatalı cevap veya eksik ifade.'
    }
