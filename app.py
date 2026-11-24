"""Arayüz: fotoğrafı oku, NumPy işlemlerini uygula ve sonucu göster."""

from hashlib import sha256
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
import streamlit as st

from islemler import gri_yap, kirp, parlaklik_ayarla

# 1. Sayfa ve stil. Görünüm, NumPy işlem kodundan ayrı tutulur.
st.set_page_config(page_title="Atölye — Fotoğraf düzenleyici", layout="wide")
stil = Path(__file__).with_name("stil.css").read_text(encoding="utf-8")
st.markdown(f"<style>{stil}</style>", unsafe_allow_html=True)


def sifirla():
    """Yüklenen fotoğrafı koruyarak düzenleme ayarlarını sıfırla."""
    for anahtar in ("parlaklik", "gri", "kirpma", "x_aralik", "y_aralik"):
        st.session_state.pop(anahtar, None)


@st.cache_data(show_spinner=False)
def gorsel_oku(veri: bytes):
    """Dosyayı RGB NumPy dizisine dönüştür; kaynak boyutunu da döndür."""
    with Image.open(BytesIO(veri)) as kaynak:
        if kaynak.width * kaynak.height > 24_000_000:
            raise ValueError("En fazla 24 megapiksel bir fotoğraf seç.")
        duz = ImageOps.exif_transpose(kaynak)
        kaynak_boyutu = duz.size
        rgba = duz.convert("RGBA")
        zemin = Image.new("RGBA", rgba.size, "white")
        rgb = Image.alpha_composite(zemin, rgba).convert("RGB")
        # Çalışma görseli ve indirilen PNG aynı boyuttadır.
        rgb.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        return np.asarray(rgb).copy(), kaynak_boyutu


def png_olustur(dizi: np.ndarray) -> bytes:
    """Piksel dizisini indirilebilir PNG baytlarına dönüştür."""
    tampon = BytesIO()
    Image.fromarray(dizi).save(tampon, format="PNG")
    return tampon.getvalue()


# 2. Dosya ve ayarlar. Dosya seçilmeden düzenleme yapılmaz.
with st.sidebar:
    st.markdown('<p class="panel-title">Fotoğraf</p>', unsafe_allow_html=True)
    dosya = st.file_uploader(
        "Fotoğraf seç", type=["png", "jpg", "jpeg", "webp"], key="dosya",
        label_visibility="collapsed",
    )

orijinal = None
kaynak_boyutu = None
kimlik = None
dosya_adi = "fotograf"
if dosya is not None:
    veri = dosya.getvalue()
    kimlik = sha256(veri).hexdigest()
    try:
        orijinal, kaynak_boyutu = gorsel_oku(veri)
        dosya_adi = Path(dosya.name).stem
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        st.sidebar.error("Fotoğraf okunamadı. En fazla 24 megapiksel bir PNG, JPEG veya WebP seç.")

if st.session_state.get("kaynak_kimligi") != kimlik:
    sifirla()
    st.session_state.kaynak_kimligi = kimlik

hazir = orijinal is not None
gecerli_kirpma = True
with st.sidebar:
    st.divider()
    st.markdown('<p class="panel-title">Ayarlar</p>', unsafe_allow_html=True)
    katsayi = st.slider(
        "Parlaklık", 0.2, 2.0, 1.0, step=0.05, format="%.2f ×",
        key="parlaklik", disabled=not hazir,
    )
    gri = st.toggle("Siyah beyaz", key="gri", disabled=not hazir)
    st.divider()
    kirpma = st.toggle("Kırp", key="kirpma", disabled=not hazir)
    if hazir and kirpma:
        h, w, _ = orijinal.shape
        x_aralik = st.slider("Sol / sağ sınır", 0, w, (0, w), key="x_aralik")
        y_aralik = st.slider("Üst / alt sınır", 0, h, (0, h), key="y_aralik")
        gecerli_kirpma = x_aralik[0] < x_aralik[1] and y_aralik[0] < y_aralik[1]
        if not gecerli_kirpma:
            st.error("Kırpma alanı boş. Sınırları birbirinden uzaklaştır.")
    st.divider()
    st.button("Sıfırla", on_click=sifirla, width="stretch", disabled=not hazir)

# 3. NumPy işlemleri. Her düzenleme orijinal veriden başlar.
sonuc = None
if hazir:
    sonuc = orijinal
    if kirpma and gecerli_kirpma:
        sonuc = kirp(sonuc, x_aralik, y_aralik)
    sonuc = parlaklik_ayarla(sonuc, katsayi)
    if gri:
        sonuc = gri_yap(sonuc)

# 4. Çalışma alanı. Kullanıcının fotoğrafı, görünüm ve indirme.
baslik, indir = st.columns([5, 1.5], vertical_alignment="center")
with baslik:
    st.markdown('<div class="wordmark">Atölye<span>Fotoğraf düzenleyici</span></div>',
                unsafe_allow_html=True)
with indir:
    st.download_button(
        "PNG indir", data=png_olustur(sonuc) if hazir else b"",
        file_name=f"{dosya_adi}_duzenlendi.png", mime="image/png",
        type="primary", width="stretch", disabled=not hazir or not gecerli_kirpma,
    )
st.divider()

gorunum = st.segmented_control(
    "Görünüm", ["Düzenlenmiş", "Önce / sonra"], default="Düzenlenmiş",
    key="gorunum", label_visibility="collapsed", disabled=not hazir,
)

if not hazir:
    st.markdown("""
    <section class="empty-canvas">
      <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">
        <rect x="5" y="5" width="30" height="30" rx="3" stroke="currentColor" stroke-width="1.4"/>
        <circle cx="15" cy="15" r="3" stroke="currentColor" stroke-width="1.4"/>
        <path d="M6 29L16 21L23 26L29 18L35 24" stroke="currentColor" stroke-width="1.4"/>
      </svg>
      <h1>Bir fotoğrafla başla.</h1>
      <p>Sol panelden fotoğrafını seç.<br>Parlaklığı ayarla, kırp ve sonucu indir.</p>
      <span>PNG · JPEG · WebP</span>
    </section>
    """, unsafe_allow_html=True)
else:
    st.caption(dosya.name)
    if not gecerli_kirpma:
        st.warning("Kırpma alanı geçerli olana kadar tam görsel gösteriliyor; indirme kapalı.")
    if gorunum == "Önce / sonra":
        sol, sag = st.columns(2, gap="medium")
        with sol:
            st.caption("ORİJİNAL")
            st.image(orijinal, width="stretch")
        with sag:
            st.caption("DÜZENLENMİŞ")
            st.image(sonuc, width="stretch")
    else:
        st.image(sonuc, width="stretch")
    h, w, _ = sonuc.shape
    renk = "Siyah beyaz" if gri else "RGB"
    st.caption(f"{w} × {h} px · {renk} · PNG")
    if kaynak_boyutu != (orijinal.shape[1], orijinal.shape[0]):
        st.caption("Çalışma ve indirme boyutu uzun kenarda 1600 piksele sınırlandı.")
