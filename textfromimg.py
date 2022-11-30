#installed tesseract from https://digi.bib.uni-mannheim.de/tesseract/
import PyPDF2
import streamlit as st
import cv2
import pytesseract
import numpy as np
import pandas as pd

#Specifying the path of Tesseract
# pytesseract.pytesseract.tesseract_cmd= r'C:\Program Files\Tesseract-OCR\tesseract.exe'                  #For running locally
pytesseract.pytesseract.tesseract_cmd=r"tesseract"                                                    #For running in cloud

#Function to preprocess image and returns text from it
def img_to_text(img):
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


option = st.selectbox('Please select the document type',
                          ('---Select an option---', 'Study Permit Application', 'Passport Process Request (PPR)',
                           'Temporary Resident Visa (TRV)', 'Study Permit Approval Letter (LOI)', 'Study Permit'))

#Dataframe for reference
data = [['Study Permit Application',"your application has been received"],
        ['Study Permit Application',"Principal Applicant"],
        ['Passport Process Request (PPR)',"We require your passport to finalize processing your application"],
        ['Temporary Resident Visa (TRV)','MULTIPLE'],
        ['Study Permit Approval Letter (LOI)',"letter of introduction"],
        ['Study Permit','INFORMATION DU CLIENT']]

df = pd.DataFrame(data, columns=['doctype', 'keywords'])


#To validate the document
def documentValidation(text):
    recommended_doc=None
    for item in df.keywords:
        if(text.find(item) != -1):
            recommended_doc = df[['doctype']][(item==df.keywords)]['doctype'].iloc[0]
    return recommended_doc

doc=st.file_uploader("")                            #Get the uploaded file
text_extracted = ''
if doc is not None:
    filetype = doc.type.split('/')[1]               #getting file type
    if filetype.lower()=='pdf':
        pdfFileObj = doc
        try:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            # print(pdfReader.numPages)
            for i in range(0, pdfReader.numPages):
                pageObj = pdfReader.getPage(i)
                text_extracted = text_extracted + '   ' + pageObj.extractText()
            pdfFileObj.close()
        except:
            st.warning("File contents are not clear. Please verify and re-upload a good quality file.")
            option=''
    elif filetype.lower() in ['ras', 'xwd', 'bmp', 'jpe', 'jpg', 'jpeg', 'xpm', 'ief', 'pbm', 'tif', 'gif', 'ppm', 'xbm', 'tiff', 'rgb', 'pgm', 'png', 'pnm']:
        try:
            file_bytes = np.asarray(bytearray(doc.read()), dtype=np.uint8)
            opencv_image = cv2.imdecode(file_bytes, 1)
            text_extracted = img_to_text(opencv_image)
        except:
            st.warning("Image is not clear. Please verify and re-upload a good quality file.")
            option = ''
    else:
        st.warning("Please upload a valid file (.pdf, .ras, .xwd, .bmp, .jpe, .jpg, .jpeg, .xpm, .ief, .pbm, .tif, .gif, .ppm, .xbm, .tiff, .rgb, .pgm, .png, .pnm)")
        option = ''
    # option = st.selectbox('Please select the document type',
    #                       ('---Select an option---', 'Study Permit Application', 'Passport Process Request (PPR)',
    #                        'Temporary Resident Visa (TRV)', 'Study Permit Approval Letter (LOI)', 'Study Permit'))

    if(option == 'Study Permit Application'):
        if text_extracted.find("your application has been received") != -1 or text_extracted.find("Principal Applicant") != -1:
            st.success("Matched",icon="✅")
        else:
            doc_recommended=documentValidation(text_extracted)
            if doc_recommended is None:
                st.warning("Looks like this is not a relevant document. Please verify.")
            else:
                st.warning("Please make sure you uploaded the right document. This document looks like a "+doc_recommended,icon="⚠️")

    elif (option == 'Passport Process Request (PPR)'):
        if text_extracted.find("We require your passport to finalize processing your application") != -1:
            st.success("Matched",icon="✅")
        else:
            doc_recommended = documentValidation(text_extracted)
            if doc_recommended is None:
                st.warning("Looks like this is not a relevant document. Please verify.")
            else:
                st.warning(
                    "Please make sure you uploaded the right document. This document looks like a " + doc_recommended,
                    icon="⚠️")

    elif (option == 'Temporary Resident Visa (TRV)'):
        if text_extracted.find("MULTIPLE") != -1:
            st.success("Matched",icon="✅")
        else:
            doc_recommended = documentValidation(text_extracted)
            if doc_recommended is None:
                st.warning("Looks like this is not a relevant document. Please verify.")
            else:
                st.warning(
                    "Please make sure you uploaded the right document. This document looks like a " + doc_recommended,
                    icon="⚠️")

    elif (option == 'Study Permit Approval Letter (LOI)'):
        if text_extracted.find("letter of introduction") != -1:
            st.success("Matched",icon="✅")
        else:
            doc_recommended = documentValidation(text_extracted)
            if doc_recommended is None:
                st.warning("Looks like this is not a relevant document. Please verify.")
            else:
                st.warning(
                    "Please make sure you uploaded the right document. This document looks like a " + doc_recommended,
                    icon="⚠️")

    elif (option == 'Study Permit'):
        if text_extracted.find("INFORMATION DU CLIENT") != -1:
            st.success("Matched",icon="✅")
        else:
            doc_recommended = documentValidation(text_extracted)
            if doc_recommended is None:
                st.warning("Looks like this is not a relevant document. Please verify.")
            else:
                st.warning(
                    "Please make sure you uploaded the right document. This document looks like a " + doc_recommended,
                    icon="⚠️")
    # st.write(text_extracted)



