# Şifrələmə Metodları və SecretNotesPy Layihəsinin Arxitekturası

Müasir dünyada məlumatların təhlükəsizliyi hər şeydən önəmlidir. Məlumatların icazəsiz şəxslərin əlinə keçməməsi üçün müxtəlif kriptoqrafik (şifrələmə) alqoritmlərindən istifadə olunur. Bu məqalədə həm yaratdığımız **SecretNotesPy** layihəsinin arxitekturasını, həm də layihədə tətbiq olunan əsas şifrələmə üsullarının (AES, RSA və ECC) riyazi işləmə prinsiplərini dərindən araşdıracağıq.

---

## 1. SecretNotesPy Layihəsi Nədir?

**SecretNotesPy**, istifadəçilərə qeydlərini təhlükəsiz şəkildə şifrələməyə və deşifrə etməyə imkan verən qrafik interfeysli (Tkinter əsaslı) bir tətbiqdir. 

Layihə 3 fərqli şifrələmə metodunu dəstəkləyir:
1. **AES-256**: Parol əsaslı, çox sürətli və simmetrik şifrələmə metodu.
2. **RSA-2048**: Açıq (Public) və Özəl (Private) açar məntiqinə əsaslanan klassik asimmetrik şifrələmə.
3. **ECC (P-256)**: Elliptik Əyrilər üzərində qurulmuş, kiçik açar ölçüsü ilə yüksək təhlükəsizlik verən asimmetrik şifrələmə.

Layihə `cryptography` kitabxanasından istifadə edir və asimmetrik alqoritmlər (RSA və ECC) üçün "hibrid şifrələmə" modelini tətbiq edir. Yəni mətnin özü hər zaman AES ilə şifrələnir, lakin AES-in açarı RSA və ya ECC vasitəsilə qorunur. Bu həm sürəti, həm də təhlükəsizliyi maksimuma çatdırır.

---

## 2. AES (Advanced Encryption Standard)

### AES Nədir?
AES, simmetrik bir şifrələmə alqoritmidir. Yəni məlumatı şifrələmək və şifrəni açmaq üçün **eyni açar** istifadə olunur. SecretNotesPy layihəsində parol əsaslı AES şifrələməsi zamanı parol `PBKDF2HMAC` alqoritmi vasitəsilə 32-baytlıq AES açarına çevrilir.

### AES Necə İşləyir? (Riyazi və Məntiqi Yollar)
AES mətni bloklar (128 bit və ya 16 bayt) şəklində şifrələyir. AES-256 alqoritmində 14 raund (mərhələ) tətbiq olunur. Hər raundda 4 əsas əməliyyat yerinə yetirilir:

1. **SubBytes (Əvəzetmə):** Blokdakı hər bir bayt S-Box adlanan xüsusi bir cədvəl vasitəsilə başqa bir baytla əvəz olunur. Bu addım riyazi olaraq Galois Sahəsində ($GF(2^8)$) tərsini tapma və affin transformasiyasına əsaslanır. Bu, alqoritmə qeyri-xəttilik (non-linearity) qatır.
2. **ShiftRows (Sətirlərin Sürüşdürülməsi):** 4x4 matris şəklində dizilmiş baytların sətirləri sola doğru fərqli addımlarla sürüşdürülür (1-ci sətir 0, 2-ci sətir 1, 3-cü sətir 2 və s.).
3. **MixColumns (Sütunların Qarışdırılması):** Hər bir sütun $GF(2^8)$ sahəsində müəyyən bir matrislə vurulur. Bu, bir baytda olan dəyişikliyin bütün bloka təsir etməsini təmin edir (diffuziya).
4. **AddRoundKey (Raund Açarının Əlavə Edilməsi):** Matrisdəki hər bayt əsas açardan törədilmiş həmin raunda aid açar matrisi ilə XOR (Xüsusi VƏ YA / Exclusive OR) əməliyyatına salınır. 

*Qeyd: SecretNotesPy AES-in GCM (Galois/Counter Mode) modundan da istifadə edir ki, bu da həm şifrələmə, həm də məlumatın tamlığını (bütövlüyünü) təsdiqləmək üçün istifadə olunur.*

---

## 3. RSA (Rivest-Shamir-Adleman)

### RSA Nədir?
RSA ən məşhur **asimmetrik** şifrələmə alqoritmidir. Burada iki fərqli açar var: **Açıq Açar (Public Key)** məlumatı şifrələmək üçündür və hamı ilə paylaşıla bilər, **Özəl Açar (Private Key)** isə şifrəni açmaq üçündür və gizli saxlanılmalıdır.

### RSA-nın Riyazi Əsasları
RSA-nın təhlükəsizliyi **çox böyük ədədləri vuruqlara ayırmağın çətinliyi** (Integer Factorization Problem) probleminə əsaslanır.

**Açarların Yaradılması Yolu:**
1. İki çox böyük təsadüfi sadə ədəd seçilir: $p$ və $q$.
2. Modul $n$ hesablanır: 
   $$n = p \times q$$
   (Bu $n$ ədədi hər iki açarın tərkib hissəsi olacaq. $n$-in uzunluğu açarın uzunluğudur, məsələn layihədəki kimi 2048 bit).
3. Eylerin totient funksiyası $\phi(n)$ hesablanır: 
   $$\phi(n) = (p-1) \times (q-1)$$
4. Açıq açarın eksponenti ($e$) seçilir. Adətən bu $e = 65537$ (və ya $2^{16}+1$) olaraq götürülür. $e$ ədədi $\phi(n)$ ilə qarşılıqlı sadə olmalıdır.
5. Özəl açarın eksponenti ($d$) hesablanır. $d$, $e$-nin $\phi(n)$ modulunda tərsi olmalıdır:
   $$d \times e \equiv 1 \pmod{\phi(n)}$$

**Nəticədə:**
- Açıq Açar: $(n, e)$
- Özəl Açar: $(n, d)$

**Şifrələmə Prosesi:**
Mətn ədədi qiymətə ($M$) çevrilir ($M < n$). 
Şifrələnmiş mətn ($C$) belə hesablanır:
$$C = M^e \pmod{n}$$

**Deşifrə (Şifrəaçma) Prosesi:**
Şifrələnmiş mətn yalnız Özəl Açar ($d$) vasitəsilə açıla bilər:
$$M = C^d \pmod{n}$$

*SecretNotesPy layihəsində böyük mətnləri birbaşa RSA ilə şifrələmək yavaş olduğu üçün "Hibrid" üsul istifadə olunub: Təsadüfi bir AES açarı yaradılır, mətn bu AES açarı ilə şifrələnir. AES açarının özü isə RSA Açıq Açarı ilə şifrələnib mətnə əlavə edilir.*

---

## 4. ECC (Elliptic Curve Cryptography)

### ECC Nədir?
ECC müasir və çox güclü **asimmetrik** şifrələmə üsuludur. RSA-dan ən böyük fərqi odur ki, çox daha kiçik açar ölçüsü ilə RSA ilə eyni səviyyədə təhlükəsizlik təmin edir. Məsələn, 256-bitlik ECC açarı (layihədə istifadə olunan `SECP256R1`) 3072-bitlik RSA açarı ilə eyni gücdədir.

### ECC-nin Riyazi Əsasları
ECC-nin təhlükəsizliyi **Elliptik Əyri üzərində Diskret Loqarifm Problemi**nə (ECDLP) əsaslanır.

**Elliptik Əyri Tənliyi:**
Adətən belə bir sadə modul tənliyinə malikdir:
$$y^2 = x^3 + a x + b \pmod{p}$$
(Burada $p$ böyük bir sadə ədəddir, $a$ və $b$ isə əyrinin formasını təyin edən sabitlərdir. $4a^3 + 27b^2 \neq 0$).

**Nöqtə Toplanması və Skalyar Vurma:**
Əyri üzərindəki iki nöqtəni ($P$ və $Q$) xüsusi həndəsi və cəbri qaydalarla toplamaq ($P+Q$) mümkündür. 
Əsas əməliyyat isə bir nöqtənin öz-özü ilə dəfələrlə toplanması, yəni **Skalyar Vurma**dır:
$$Q = k \times P$$
Burada:
- **$P$ (Base Point):** Əyri üzərində standart başlanğıc nöqtəsidir (hamıya məlumdur).
- **$k$ (Özəl Açar):** Çox böyük təsadüfi tam ədəddir (gizli saxlanılır).
- **$Q$ (Açıq Açar):** $P$ nöqtəsinin $k$ dəfə toplanması nəticəsində alınan yeni nöqtədir ($x$ və $y$ koordinatları).

Əgər $k$ və $P$ məlumdursa, $Q$-nü tapmaq çox asandır. Amma **$Q$ və $P$ verildikdə $k$-nı (özəl açarı) tapmaq qeyri-mümkündür**. Bu, ECC-nin qırılmaz riyazi təməlidir.

### ECDH (Elliptic-Curve Diffie-Hellman) Açar Mübadiləsi
Layihədə ECC şifrələmək üçün birbaşa mətnə tətbiq edilmir. Bunun əvəzinə ortaq sirr tapmaq üçün istifadə edilir (layihədəki `_ecdh_shared_key` funksiyası).
Təsəvvür edək iki tərəf var:
- Sizin Özəl Açarınız: $d_A$, Açıq Açarınız: $Q_A = d_A \times P$
- Qarşı tərəfin Özəl Açarı: $d_B$, Açıq Açarı: $Q_B = d_B \times P$

Ortaq AES açarı tapmaq üçün siz öz Özəl açarınızı ($d_A$) qarşı tərəfin Açıq açarına ($Q_B$) vurursunuz:
$$S = d_A \times Q_B$$
Riyazi olaraq bu bərabərdir:
$$S = d_A \times (d_B \times P) = d_B \times (d_A \times P) = d_B \times Q_A$$
Yəni qarşı tərəf də sizin açıq açarınızı öz özəl açarı ilə vuranda **eyni S nöqtəsini (ortaq sirri)** əldə edir. Layihədə bu $S$ nöqtəsi HKDF (kdf) funksiyasından keçirilərək güclü 32-baytlıq AES açarına çevrilir və qeyd bu AES ilə şifrələnir.

---

## Yekun Nəticə

**SecretNotesPy** layihəsi, həm sürəti, həm də müasir təhlükəsizlik standartlarını özündə birləşdirir:
- Əgər mətni sadəcə parol ilə yadda saxlamaq istəyirsinizsə, **AES-256** tam sizə görədir.
- Əgər qeydlərinizi asimmetrik üsulla qorumaq və ya başqa birinə onun açıq açarı ilə şifrələyib göndərmək istəyirsinizsə, **RSA-2048** ən ənənəvi üsuldur.
- Eyni asimmetrik təhlükəsizliyi daha sürətli, müasir və daha kiçik ölçülü açarlarla etmək istəyirsinizsə, **ECC (P-256)** ən ideal seçimdir. 

Kriptoqrafiyanın arxasındakı bu riyazi prinsiplər, rəqəmsal dünyada məlumatlarımızın tamamilə təhlükəsiz qalmasını təmin edən əsas bünövrədir.
