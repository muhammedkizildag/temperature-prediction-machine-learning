import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Fiziksel Bölge ve Izgara (Grid) Tanımlamaları
Lx, Ly = 10.0, 10.0          # [0, Lx] x [0, Ly] iki boyutlu bölge
nx, ny = 60, 60              # Izgara nokta sayıları
dx = Lx / (nx - 1)           # Delta x
dy = Ly / (ny - 1)           # Delta y

x = np.linspace(0, Lx, nx)
y = np.linspace(0, Ly, ny)
X, Y = np.meshgrid(x, y, indexing='ij')

# 2. Fiziksel Parametreler (Adveksiyon-Difüzyon Modeli)
alpha = 0.70                 # Termal difüzivite (alpha)
T_source = 100.0             # Kaynak sıcaklığı (T_source)
x_source_idx = nx // 3       # Kaynağın x indeksi (akışı görmek için biraz sola/aşağıya alındı)
y_source_idx = ny // 3       # Kaynağın y indeksi
vx = 0.35                    # Akışkanın x yönündeki hızı (v_x)
vy = 0.25                    # Akışkanın y yönündeki hızı (v_y)

# 3. Zaman Adımı ve Sayısal Kararlılık (CFL) Koşulu
dt_diff = 0.2 * min(dx**2, dy**2) / alpha
dt_adv = 0.2 * min(dx / (abs(vx) + 1e-8), dy / (abs(vy) + 1e-8))
dt = min(dt_diff, dt_adv)    # Hem difüzyon hem adveksiyon için güvenli zaman adımı
nt = 300                     # Toplam zaman adımı sayısı

# Difüzyon (iletim) katsayıları
rx = (alpha * dt) / (dx**2)
ry = (alpha * dt) / (dy**2)

# Adveksiyon (taşınım/akış) katsayıları
cx = (vx * dt) / (2.0 * dx)
cy = (vy * dt) / (2.0 * dy)

# 4. Başlangıç ve Sınır Koşulları
T = np.zeros((nx, ny))
T[x_source_idx, y_source_idx] = T_source

# Makine öğrenmesi veri setini tutacak liste
dataset_records = []

# 5. Sonlu Farklar Yöntemi (FDM) ile Zaman Döngüsü
for n in range(nt):
    T_new = T.copy()
    current_time = n * dt
    
    # Ayrıklaştırılmış 2B Adveksiyon-Difüzyon Denklemi:
    # dT/dt + vx*(dT/dx) + vy*(dT/dy) = alpha * (d^2T/dx^2 + d^2T/dy^2)
    difuzyon_x = rx * (T[2:, 1:-1] - 2 * T[1:-1, 1:-1] + T[:-2, 1:-1])
    difuzyon_y = ry * (T[1:-1, 2:] - 2 * T[1:-1, 1:-1] + T[1:-1, :-2])
    
    adveksiyon_x = cx * (T[2:, 1:-1] - T[:-2, 1:-1])
    adveksiyon_y = cy * (T[1:-1, 2:] - T[1:-1, :-2])
    
    T_new[1:-1, 1:-1] = (
        T[1:-1, 1:-1]
        + difuzyon_x + difuzyon_y
        - adveksiyon_x - adveksiyon_y
    )
    
    # Sıcaklık kaynağını sabit tutma
    T_new[x_source_idx, y_source_idx] = T_source
    T = T_new

    # Belirli zaman adımlarında makine öğrenmesi için veri kaydetme
    if (n + 1) % 75 == 0:
        for i in range(nx):
            for j in range(ny):
                dataset_records.append({
                    'T_source': T_source,
                    'alpha': alpha,
                    'vx': vx,
                    'vy': vy,
                    'x_source': x[x_source_idx],
                    'y_source': y[y_source_idx],
                    'x': x[i],
                    'y': y[j],
                    't': current_time,
                    'T': T[i, j]
                })

# 6. Veri Setinin Oluşturulması ve Kaydedilmesi
df_dataset = pd.DataFrame(dataset_records)
print(f"Toplam üretilen veri satırı sayısı: {len(df_dataset)}")
print(df_dataset.head())
df_dataset.to_csv("simulasyon_veri_seti_akiskanli.csv", index=False)

# 7. Sonuçların Görselleştirilmesi (Pürüzsüz 2B Sıcaklık Haritası ve Akış Yönü)
plt.figure(figsize=(9, 7))

# Halkalı görünümü önlemek için shading='gouraud' ile pcolormesh kullanımı
mesh = plt.pcolormesh(X, Y, T, shading='gouraud', cmap='inferno')
plt.colorbar(mesh, label='Sıcaklık (T)')

# Akışkanın hız vektörü (yön) gösterimi
x_quiver, y_quiver = np.meshgrid(np.linspace(1, Lx-1, 8), np.linspace(1, Ly-1, 8))
plt.quiver(x_quiver, y_quiver, vx, vy, color='white', alpha=0.5, scale=5, label='Akış Yönü (v)')

# Isı kaynağının işaretlenmesi
plt.scatter(x[x_source_idx], y[y_source_idx], color='cyan', marker='*', s=140, label='Isı Kaynağı')

plt.title(f'Akışkan Etkili 2B Sıcaklık Dağılımı $T_{{FDM}}(x,y)$\n($v_x={vx}, v_y={vy}$, t = {nt*dt:.2f} s)')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()