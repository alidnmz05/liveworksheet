import pandas as pd
from apps.submissions.models import Submission
from apps.worksheets.models import Worksheet

def get_personalized_recommendations(user, num_recommendations=5):
    """
    Öğrencinin geçmişteki test çözme performansını Makine Öğrenmesi / Veri Analizi
    mantığıyla (Content-Based Filtering yaklaşımı) analiz ederek eksik olduğu
    konularda kişiselleştirilmiş yeni çalışma kağıtları öneren motor.
    """
    # 1. Aşama: Öğrencinin geçmişteki tüm notlandırılmış sınav verilerini çek
    submissions = Submission.objects.filter(student=user, is_graded=True).select_related('worksheet__subject')
    
    # Cold Start (Soğuk Başlangıç) Problemi Çözümü: 
    # Öğrenci yeni kayıt olmuş ve yeterince test çözmemişse en popüler (View Count) Worksheetleri öner.
    if submissions.count() < 3:
        return Worksheet.objects.filter(is_public=True).order_by('-view_count')[:num_recommendations]
    
    # 2. Aşama: Veriyi Pandas DataFrame üzerine alıyoruz (Akademik analiz kolaylığı)
    data = []
    for sub in submissions:
        # Eğer çalışma kağıdı silinmişse veya subject yoksa atla/genel de
        if not sub.worksheet:
            continue
            
        subject_name = sub.worksheet.subject.name if sub.worksheet.subject else "Genel"
        score = sub.score or 0.0
        
        data.append({
            'worksheet_id': str(sub.worksheet.id),
            'subject': subject_name,
            'score': score
        })
        
    if not data:
        return Worksheet.objects.filter(is_public=True).order_by('-view_count')[:num_recommendations]

    df = pd.DataFrame(data)
    
    # 3. Aşama: Öğrenci Zayıflık Profili (Knowledge Tracing)
    # Pandas kullanarak Konulara (Subject) göre not ortalamalarını gruplayıp hesaplıyoruz
    subject_performance = df.groupby('subject')['score'].mean().reset_index()
    
    # Eşik değeri: %70 ortalamanın altındaki konular "Zayıf / Eksik Kalsın" olarak etiketleniyor
    weak_subjects = subject_performance[subject_performance['score'] < 70.0]['subject'].tolist()
    
    # Öğrencinin notları çok yüksekse (Zayıf konusu yoksa), notu nispeten en düşük olan 2 konuyu seç
    if not weak_subjects:
        weak_subjects = subject_performance.sort_values(by='score').head(2)['subject'].tolist()

    # Zaten çözülmüş olan kağıtları tekrar önermemek için kimliklerini lsiteye alıyoruz
    completed_worksheet_ids = df['worksheet_id'].tolist()

    # 4. Aşama: Tavsiyeleri Veritabanından Filtreleyerek Getirme
    recommendations_qs = Worksheet.objects.filter(
        is_public=True,
        subject__name__in=weak_subjects
    ).exclude(
        id__in=completed_worksheet_ids
    ).order_by('-view_count') # İhtiyaç olan konulardaki en iyi materyalleri getir
    
    recommendations = list(recommendations_qs[:num_recommendations])
    
    # 5. Aşama: Eğer eksik konularda yeterli materyal yoksa, listeyi popüler genel materyallerle tamamla
    if len(recommendations) < num_recommendations:
        needed = num_recommendations - len(recommendations)
        extra_qs = Worksheet.objects.filter(is_public=True).exclude(
            id__in=[w.id for w in recommendations] + completed_worksheet_ids
        ).order_by('-view_count')[:needed]
        
        recommendations.extend(list(extra_qs))
        
    return recommendations
