#tensorflow, keras_ocr, cv2, pytesseract  pip install tensorflow==2.5.0
#installed tesseract from https://digi.bib.uni-mannheim.de/tesseract/
import streamlit as st
import cv2
import pytesseract
import numpy as np
# pytesseract.pytesseract.tesseract_cmd= r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd=r"tesseract"

def img_to_text(img):
    # img = cv2.imread(img)
    # img1 = asarray(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    dilation = cv2.dilate(thresh, rect_kernel, iterations=1)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    final_text = ''
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        rect = cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = gray[y:y + h, x:x + w]

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)

        final_text = final_text + '' + text
    return final_text
    # cv2.imshow('invert', contours)
    # cv2.waitKey()

# img_to_text("spr.png")
# print("*******************************************************************************")
# img_to_text("ppr.png")
# print("*******************************************************************************")
# img_to_text("doc.png")
# print("*******************************************************************************")
# img_to_text("visa2.png")
# print("*******************************************************************************")
# img_to_text("loi.png")
# print("*******************************************************************************")
# img_to_text("studypermit.png")
# print("*******************************************************************************")

img=st.file_uploader("")
if img is not None:
    file_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    text = img_to_text(opencv_image)
    st.write(text)