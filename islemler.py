"""Görsel işlemler: arayüzden bağımsız, okunabilir NumPy fonksiyonları."""

import numpy as np


def rgb_kontrol(gorsel: np.ndarray) -> None:
    if not isinstance(gorsel, np.ndarray):
        raise ValueError("Görsel bir NumPy dizisi olmalı.")
    if gorsel.ndim != 3 or gorsel.shape[2] != 3:
        raise ValueError("Görsel (yükseklik, genişlik, 3) şeklinde RGB olmalı.")
    if gorsel.dtype != np.uint8 or 0 in gorsel.shape:
        raise ValueError("Görsel, boş olmayan uint8 piksel verisi içermeli.")


def parlaklik_ayarla(gorsel: np.ndarray, katsayi: float) -> np.ndarray:
    """1 aynı, 1'den küçük daha koyu, 1'den büyük daha parlak."""
    rgb_kontrol(gorsel)
    if not np.isfinite(katsayi) or not 0 <= katsayi <= 4:
        raise ValueError("Parlaklık katsayısı 0–4 arasında olmalı.")
    # Önce float: uint8 üzerinde çarpma yaparken sayı taşmasını önleriz.
    sonuc = gorsel.astype(np.float32) * katsayi
    # Piksel aralığı 0–255; asıl görseli değiştirmeden yeni dizi döneriz.
    return np.clip(sonuc, 0, 255).astype(np.uint8)


def gri_yap(gorsel: np.ndarray) -> np.ndarray:
    """RGB kanallarını ağırlıklı birleştir; üç kanallı gri görsel döndür."""
    rgb_kontrol(gorsel)
    agirliklar = np.array([0.299, 0.587, 0.114], dtype=np.float32)
    # Son eksen renk kanalları: her piksel için tek gri değer hesaplanır.
    gri = np.clip(gorsel.astype(np.float32) @ agirliklar, 0, 255)
    gri = np.rint(gri).astype(np.uint8)
    return np.repeat(gri[:, :, None], 3, axis=2)


def kirp(gorsel: np.ndarray, x_araligi: tuple, y_araligi: tuple) -> np.ndarray:
    """x sütun, y satır seçer; sağ ve alt sınırlar dilimlemede hariçtir."""
    rgb_kontrol(gorsel)
    x1, x2 = x_araligi
    y1, y2 = y_araligi
    yukseklik, genislik, _ = gorsel.shape
    if not (0 <= x1 < x2 <= genislik and 0 <= y1 < y2 <= yukseklik):
        raise ValueError("Kırpma alanı boş olmamalı ve görsel sınırlarında kalmalı.")
    # Dilim görünüm üretir; bağımsız çıktı için kopya alıyoruz.
    return gorsel[y1:y2, x1:x2].copy()
