import cv2
import numpy as np
import matplotlib.pyplot as plt


def analiziraj_teksturu(putanja_do_slike):
    # Učitavanje slike u crno-belom formatu (grayscale)
    slika = cv2.imread(putanja_do_slike, cv2.IMREAD_GRAYSCALE)

    if slika is None:
        print("Greška: Slika nije pronađena!")
        return

    # 1. Određivanje histograma i verovatnoća (normalizovan histogram)
    L = 256  # Broj nivoa sjajnosti
    hist, bin_edges = np.histogram(slika.flatten(), bins=L, range=[0, 256], density=True)

    # Nivoi sjajnosti (z_i) od 0 do 255
    z = np.arange(L)

    # 2. Računanje momenata i pokazatelja
    # Prvi moment: Srednja vrednost
    m = np.sum(z * hist)

    # Drugi centralni moment: Varijansa
    mu_2 = np.sum(((z - m) ** 2) * hist)

    # Treći centralni moment: Asimetrija
    mu_3 = np.sum(((z - m) ** 3) * hist)

    # Uniformnost (Uniformity)
    U = np.sum(hist ** 2)

    # Srednja entropija
    # Dodajem jako malu vrednost (eps) da izbegnem log2(0)
    eps = np.finfo(float).eps
    e = -np.sum(hist * np.log2(hist + eps))

    # Prikaz rezultata u konzoli
    print(f"--- Parametri teksture ---")
    print(f"1. moment (Srednja vrednost, m): {m:.2f}")
    print(f"2. moment (Varijansa, μ2):       {mu_2:.2f}")
    print(f"3. moment (Asimetrija, μ3):      {mu_3:.2f}")
    print(f"Uniformnost (U):                 {U:.6f}")
    print(f"Srednja entropija (e):           {e:.2f}")

    # 3. Grafički prikaz histograma
    plt.figure(figsize=(10, 5))
    plt.title(f"Histogram sjajnosti m = {m:.2f}, μ2 = {mu_2:.2f}, μ3 = {mu_3:.2f}")
    plt.xlabel('Nivo sjajnosti')
    plt.ylabel('Verovatnoća p(z_i)')
    plt.bar(z, hist, width=1, color='gray', edgecolor='black')
    plt.xlim([0, 255])
    plt.grid(axis='y', alpha=0.75)
    plt.savefig('Histogram sjajnosti slike.png')

analiziraj_teksturu('slika 222.jpg')