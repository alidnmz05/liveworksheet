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
