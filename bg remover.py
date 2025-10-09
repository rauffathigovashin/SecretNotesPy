from PIL import Image

# --- Parametrləri buradan dəyişə bilərsiniz ---
input_fayli = "pngegg.png"       # Arxa fonu silinəcək orijinal şəkil
output_fayli = "pngegg1.png"   # Yaddaşa veriləcək yeni şəklin adı
reng_kodu = (255, 255, 255)         # Silinəcək rəngin kodu (255, 255, 255 = bəyaz)

try:
    # Şəkli açırıq
    img = Image.open(input_fayli)

    # Şəkli RGBA formatına çeviririk (şəffaflıq üçün 'A' - Alpha kanalı)
    img = img.convert("RGBA")

    # Şəklin bütün piksel məlumatlarını alırıq
    datas = img.getdata()

    yeni_data = []
    for item in datas:
        # Əgər pikselin rəngi təyin etdiyimiz arxa fon rəngi ilə eynidirsə...
        if item[0] == reng_kodu[0] and item[1] == reng_kodu[1] and item[2] == reng_kodu[2]:
            # ...həmin pikseli tam şəffaf edirik (R, G, B, Alpha)
            yeni_data.append((255, 255, 255, 0))
        else:
            # Əks halda piksel olduğu kimi qalır
            yeni_data.append(item)

    # Yeni piksel məlumatlarını şəklə tətbiq edirik
    img.putdata(yeni_data)

    # Dəyişdirilmiş şəkli yeni fayl kimi yaddaşda saxlayırıq
    img.save(output_fayli, "PNG")

    print(f"Proses tamamlandı! Şəffaf arxa fonlu şəkil '{output_fayli}' adı ilə yaddaşa verildi.")

except FileNotFoundError:
    print(f"XƏTA: '{input_fayli}' faylı tapılmadı. Fayl adını düzgün yazdığınızdan əmin olun.")
except Exception as e:
    print(f"Gözlənilməz bir xəta baş verdi: {e}")