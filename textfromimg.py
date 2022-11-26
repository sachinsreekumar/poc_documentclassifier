#tensorflow, keras_ocr, cv2, pytesseract  pip install tensorflow==2.5.0
#installed tesseract from https://digi.bib.uni-mannheim.de/tesseract/
import PyPDF2
import streamlit as st
import cv2
import pytesseract
import numpy as np
import os
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



img=st.file_uploader("")
text_extracted = ''
if img is not None:
    filetype = img.type.split('/')[1]
    # st.write(filetype)
    if filetype=='pdf':
        # pdfFileObj = open('Sachin - study permit.pdf', 'rb')
        pdfFileObj = img
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        print(pdfReader.numPages)

        # creating a page object
        pageObj = pdfReader.getPage(0)
        text_extracted = pageObj.extractText()
        pdfFileObj.close()
    elif filetype.lower() in ['ras', 'xwd', 'bmp', 'jpe', 'jpg', 'jpeg', 'xpm', 'ief', 'pbm', 'tif', 'gif', 'ppm', 'xbm', 'tiff', 'rgb', 'pgm', 'png', 'pnm']:
        file_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        opencv_image = cv2.imdecode(file_bytes, 1)
        text_extracted = img_to_text(opencv_image)
        # st.write(text)
    else:
        st.warning("Please upload a valid file (.pdf, .ras, .xwd, .bmp, .jpe, .jpg, .jpeg, .xpm, .ief, .pbm, .tif, .gif, .ppm, .xbm, .tiff, .rgb, .pgm, .png, .pnm)")

    option = st.selectbox('Please select the document type',
                          ('---Select an option---', 'Study Permit Application', 'Passport Process Request',
                           'TRV (Temporary residences Visa)', 'Study Permit Approval Letter (LOI)', 'Study Permit'))
    # st.write(option)

    if(option == 'Study Permit Application'):
        if text_extracted.find("your application has been received") != -1:
            st.success("Matched")
        else:
            st.warning("Please make sure you uploaded the right document")

    elif (option == 'Passport Process Request'):
        if text_extracted.find("We require your passport to finalize processing your application") != -1:
            st.success("Matched")
        else:
            st.warning("Please make sure you uploaded the right document")

    elif (option == 'TRV (Temporary residences Visa)'):
        if text_extracted.find("MULTIPLE") != -1:
            st.success("Matched")
        else:
            st.warning("Please make sure you uploaded the right document")

    elif (option == 'Study Permit Approval Letter (LOI)'):
        if text_extracted.find("letter of introduction") != -1:
            st.success("Matched")
        else:
            st.warning("Please make sure you uploaded the right document")

    elif (option == 'Study Permit'):
        if text_extracted.find("INFORMATION DU CLIENT") != -1:
            st.success("Matched")
        else:
            st.warning("Please make sure you uploaded the right document")
    # st.write(text_extracted)
