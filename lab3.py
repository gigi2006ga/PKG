import streamlit as st
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def apply_smoothing(image, method, ksize):
    if method == "Усредняющий фильтр (Mean)":
        return cv2.blur(image, (ksize, ksize))
    elif method == "Гауссово размытие (Gaussian)":
        return cv2.GaussianBlur(image, (ksize, ksize), 0)
    elif method == "Медианный фильтр (Median)":
        return cv2.medianBlur(image, ksize)
    elif method == "Билатеральный фильтр":
        return cv2.bilateralFilter(image, d=ksize, sigmaColor=75, sigmaSpace=75)
    return image

def linear_contrast(img):
    img_float = img.astype(np.float32)
    min_val = np.min(img_float)
    max_val = np.max(img_float)
    stretched = (img_float - min_val) * (255.0 / (max_val - min_val))
    return np.clip(stretched, 0, 255).astype(np.uint8)

def plot_histogram(image):
    fig, ax = plt.subplots(figsize=(4,3))
    if len(image.shape) == 2:
        ax.hist(image.ravel(), bins=256, color='black')
        ax.set_title("Гистограмма (Grayscale)")
    else:
        colors = ('r', 'g', 'b')
        for i, col in enumerate(colors):
            ax.hist(image[..., i].ravel(), bins=256, color=col, alpha=0.5)
        ax.set_title("Гистограмма RGB")
    ax.set_xlabel("Яркость")
    ax.set_ylabel("Количество пикселей")
    st.pyplot(fig, use_container_width=True)

def main():
    st.set_page_config(layout="wide", page_title="Лаб. работа №2 — Вариант 8")
    st.title("Лабораторная работа №2 — Обработка изображений")
    st.markdown("""
    **Вариант 2 — Задания:**
    1. Реализация низкочастотных фильтров (сглаживающих).  
    2. Построение и эквализация гистограммы изображения.  
    3. Линейное контрастирование изображения.  
    """)

    uploaded_file = st.sidebar.file_uploader("Загрузите изображение", type=["jpg", "png", "jpeg", "bmp"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img = np.array(image)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        st.sidebar.header("Выберите режим")
        mode = st.sidebar.radio("Метод обработки", 
                                ["Низкочастотные фильтры", 
                                 "Гистограмма и эквализация",
                                 "Линейное контрастирование"])

        
        processed_img = img_bgr.copy()
        if mode == "Низкочастотные фильтры":
            method = st.sidebar.selectbox("Тип фильтра", 
                                      ["Усредняющий фильтр (Mean)",
                                       "Гауссово размытие (Gaussian)",
                                       "Медианный фильтр (Median)",
                                       "Билатеральный фильтр"])
            ksize = st.sidebar.slider("Размер окна (нечётное число)", 3, 31, 5, step=2)
            processed_img = apply_smoothing(img_bgr, method, ksize)
            processed_gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
        elif mode == "Гистограмма и эквализация":
            method = st.sidebar.selectbox("Метод эквализации", 
                                      ["Эквализация (equalizeHist)",
                                       "Адаптивная эквализация (CLAHE)"])
            if method == "Эквализация (equalizeHist)":
                processed_gray = cv2.equalizeHist(img_gray)
            else:
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                processed_gray = clahe.apply(img_gray)
        elif mode == "Линейное контрастирование":
            processed_gray = linear_contrast(img_gray)

      
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Исходное изображение")
            st.image(image, use_container_width=True)
        with col2:
            st.subheader("Обработанное изображение")
            if mode == "Низкочастотные фильтры":
                st.image(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB), use_container_width=True)
            else:
                st.image(processed_gray, use_container_width=True, channels="GRAY")
        with col3:
            st.subheader("Гистограмма")
            if mode == "Низкочастотные фильтры":
                plot_histogram(cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY))
            else:
                plot_histogram(processed_gray)

if __name__ == "__main__":
    main()

