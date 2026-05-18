from sentence_transformers import SentenceTransformer
import time

print("==================================================")
print("🤖 AKADEMİK YAPAY ZEKA MODELİ İNDİRİLİYOR 🤖")
print("Bu işlem internet hızınıza göre 1-3 dakika sürebilir.")
print("Sadece BİR KERE indirilecek ve önbelleğe alınacaktır.")
print("==================================================")

start = time.time()
# Çok Dilli (Türkçe destekli) hafif ve güçlü akademik model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

end = time.time()
print(f"✅ BAŞARILI! Model {round(end-start, 1)} saniyede indirildi ve hazır.")
