"""
Model mahalle v2 — tipoloji kataloğu, asansör kuralı ve maliyet varsayımları
===========================================================================
metrikler.py, konut_tipolojileri.py ve tipoloji_asansor_ozeti.py bu modülü kullanır.

İşaretler: [D] mevzuat / resmî kaynak (proje mevzuat paketinden aktarıldı) · [İ] ikincil ·
[V] bu çalışmanın varsayımı (doğrulanmadı) · [H] çizimden hesaplandı.
"""

import math

# --- PAİY md. 34/1 (RG 01.07.2026 değişik) [D, 08_MEVZUAT_POLITIKA/degisiklik_paketi_v1.md P4] ------------
#   tek bağımsız bölümlü konutlar hariç; bodrum dahil kat adedi 3 → asansör yeri; ≥ 4 → asansör tesisi.
#   md. 34/4: zemin üzerinde 20'den fazla konut bağımsız bölümü olan yapıda en az 2 asansör.
ASANSOR_KURAL = "PAİY md. 34/1 (RG 01.07.2026): 3 kat → asansör yeri; ≥ 4 kat → asansör (tek BB hariç)"


def asansor_kurali(kat, bb):
    """Bodrum dahil kat adedi ve bağımsız bölüm sayısına göre PAİY md. 34/1 gereği."""
    if bb <= 1:
        return "yok (tek BB)"
    if kat >= 4:
        return "asansör" + (" ×2 (md. 34/4)" if bb > 20 else "")
    if kat == 3:
        return "asansör yeri"
    return "yok"


# --- Yapım maliyeti: 2026 Yapı Yaklaşık Birim Maliyetleri Tebliği (RG 03.02.2026/33157) [D] -----------
#   M6 finansman modeliyle aynı sınıflar; tebliğdeki %10 yüklenici kârı çıkarıldı (× 0,92).
BIRIM_MALIYET = {"III.A": 19_800, "III.B": 21_050}       # TL/m²
KAR_HARIC = 0.92
SINIF = {"T1": "III.B", "T2": "III.A", "T3_Z+2": "III.A", "T3_Z+3": "III.B", "T4": "III.B"}
FIYAT_TR = 42_488                                         # TL/m², Türkiye ort. satış (Ağu. 2026) [İ, M6]

# --- Asansör ve platform maliyeti (2026) — [V] doğrulanmadı ----------------------------------------------
#   Piyasa teklifi alınmalı. Tebliğ birim maliyetinin asansörü kısmen kapsayıp kapsamadığı doğrulanmadı;
#   burada ayrı kalem olarak gösterilir.
ASANSOR_TL = 1_300_000          # 630 kg / 8 kişilik, 4 durak, kuyu ve kapılar dahil [V] (aralık 1,0–1,7 milyon)
ASANSOR_EK_DURAK_TL = 100_000   # her ek durak [V]
PLATFORM_TL = 900_000           # ev tipi kaldırma platformu, 3 durak (EN 81-41 sınıfı) [V]
ASANSOR_BAKIM_YIL = 48_000      # aylık bakım + yıllık muayene + enerji, TL/yıl [V]
KUYU_ASANSOR = (1.6, 1.8)       # m, 630 kg asansör kuyusu (iç) [V]
KUYU_T2 = (1.4, 1.6)            # m, T2 asansör yeri (platform için yeterli) [V]
KUYU_PLATFORM = (1.0, 2.3)      # m, T1 platform yeri (kiler / dolap dikmesi); 0,8 × 1,25 kabin sığar [DY]

# --- Bağımsız bölüm kataloğu (brüt m², çekirdek payı dahil) [H, tipoloji çizimlerinden] -------------------
#   Otopark Yönetmeliği Ek-1 sınıfı brüt alanla belirlenir (md. 8/3) [D].
BB = {
    "T1_son": 195.0, "T1_cekirdek": 113.0,
    "T2_zemin": 85.0, "T2_dubleks": 219.0,
    "T3_zemin_2+1": 110.0, "T3_zemin_1+1": 80.0, "T3_3+1": 110.0, "T3_3+1_kompakt": 90.0, "T3_yan_dubleks": 91.0,
    "T4_2+1": 112.0, "T4_1+1": 58.0,
    "T3_arka_2+1": 90.0,          # v2.1: T3 arka kanadı, tek katlı eşiksiz daire
}


def ek1_mevcut(brut):
    """Otopark Yönetmeliği Ek-1, meskenler (RG 25.03.2021 değişik) [D]."""
    if brut < 80:
        return 1 / 3
    if brut < 120:
        return 1 / 2
    if brut < 180:
        return 1.0
    return 2.0


def ek1_reform(brut):
    """Paket önerisi O1: her BB için 0,5; brüt ≥ 180 m² için 1 [öneri]."""
    return 1.0 if brut >= 180 else 0.5


DUKKAN_M2_YER = 50.0             # Ek-1: dükkân, 50 m² için 1 yer [D]
DUKKAN_BIRIM_M2 = 70.0           # bir dükkân biriminin ortalama brüt alanı [V]


def parsel_bb(p):
    """Bir parselin bağımsız bölümleri: [(sınıf, brüt m²)]."""
    k = int(p["konut"])
    if k <= 0:
        return []
    t = p["tip"]
    if t == "T1":
        return [("T1_son", BB["T1_son"])]
    if t == "T2":
        return [("T2_zemin", BB["T2_zemin"]), ("T2_dubleks", BB["T2_dubleks"])][:k]
    if t == "T3":
        yan = min(p.get("yan_konut", 4), k)
        arka = min(p.get("arka_konut", 0), k - yan)
        zemin = min(p.get("zemin_konut", 0), k - yan - arka)
        ust = k - yan - arka - zemin
        out = [("T3_yan_dubleks", BB["T3_yan_dubleks"])] * yan + [("T3_arka_2+1", BB["T3_arka_2+1"])] * arka
        out += ([("T3_zemin_2+1", BB["T3_zemin_2+1"]), ("T3_zemin_1+1", BB["T3_zemin_1+1"])] * 2)[:zemin]
        kat_basi = max(1, p.get("kat_basi", 3))
        for n in range(ust):
            out.append(("T3_3+1_kompakt", BB["T3_3+1_kompakt"]) if n % kat_basi == 1 else ("T3_3+1", BB["T3_3+1"]))
        return out
    # T4: kat başına 2+1 · 1+1 · 2+1
    return [("T4_1+1", BB["T4_1+1"]) if n % 3 == 1 else ("T4_2+1", BB["T4_2+1"]) for n in range(k)]


def bina_dikey_dolasim(p):
    """Bir parselin binaları için PAİY md. 34/1 gereği ve v2 tasarım kararı.

    Döndürür: list of dict(bina, kat, bb, kural, v2_cozum, asansor_mevcut, asansor_p4, yer, platform_yeri)
    asansor_mevcut: bugünkü uygulama (her merdiven evine asansör); asansor_p4: paket önerisi P4 (galeriyle bağlı
    en çok üç merdiven evine tek asansör)."""
    t, kat, k = p["tip"], p["kat"], int(p["konut"])
    if k <= 0:
        return []
    if t == "T1":
        return [dict(bina="T1 sıra ev", kat=kat, bb=1, kural=asansor_kurali(kat, 1),
                     v2_cozum="kaldırma platformu yeri (kiler/dolap dikmesi)", asansor_mevcut=0, asansor_p4=0, yer=0,
                     platform_yeri=1)]
    if t == "T2":
        return [dict(bina="T2 çok kuşaklı ev", kat=kat, bb=k, kural=asansor_kurali(kat, k),
                     v2_cozum="asansör (platform) yeri; zemin 2+1 eşiksiz", asansor_mevcut=0, asansor_p4=0, yer=1,
                     platform_yeri=0)]
    if t == "T3":
        yan = min(p.get("yan_konut", 4), k)
        arka = p.get("arka_konut", 0)
        sk_bb = k - yan - arka
        out = [dict(bina="T3 sokak kanadı", kat=kat, bb=sk_bb, kural=asansor_kurali(kat, sk_bb),
                    v2_cozum=("2 çekirdekte asansör (P4 ile galeri + 1 asansör)" if kat >= 4
                              else "2 çekirdekte asansör yeri; zemin daireler eşiksiz"),
                    asansor_mevcut=2 if kat >= 4 else 0, asansor_p4=1 if kat >= 4 else 0,
                    yer=2 if kat == 3 else 0, platform_yeri=0)]
        out += [dict(bina="T3 yan kanat (Z+1 dubleks)", kat=2, bb=yan // 2, kural=asansor_kurali(2, yan // 2),
                     v2_cozum="gerekmez (zeminden girişli dubleks)", asansor_mevcut=0, asansor_p4=0, yer=0,
                     platform_yeri=0)] * 2
        if arka:
            out.append(dict(bina="T3 arka kanat (Z, v2.1)", kat=1, bb=arka, kural=asansor_kurali(1, arka),
                            v2_cozum="gerekmez (tek katlı, eşiksiz)", asansor_mevcut=0, asansor_p4=0, yer=0,
                            platform_yeri=0))
        return out
    return [dict(bina="T4 çubuk parseli", kat=kat, bb=k, kural=asansor_kurali(kat, k),
                 v2_cozum="1 asansör (çekirdekte)", asansor_mevcut=1, asansor_p4=1, yer=0, platform_yeri=0)]


def asansor_maliyeti(durak):
    return ASANSOR_TL + max(0, durak - 4) * ASANSOR_EK_DURAK_TL


def tip_yapim_maliyeti(sinif, brut_m2):
    return brut_m2 * BIRIM_MALIYET[sinif] * KAR_HARIC


def sayi_tavan(x):
    return int(math.ceil(x - 1e-9))
