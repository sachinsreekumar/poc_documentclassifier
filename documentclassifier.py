import PyPDF2
import streamlit as st
import cv2
import pytesseract
import numpy as np
import pandas as pd
import time
from PIL import Image
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Document Classifier")

st.markdown(
    """
    <style>
        .css-9ycgxx {
            display: none;      /* drag drop content set empty */
            
        }
        .css-1fttcpj {
            display: none;              /* drag drop size content set empty */
        }
        .css-u8hs99:after {
            content: "Drop files";      /* content in drag drop */
        }
        
        .css-x8wxsk {
            padding-top:4px;
            padding-bottom:4px;             /* drag drop padding */
        }
        .css-po3vlj{
            padding-top:4px;
            padding-bottom:4px;             /* drag drop padding light */
        }
        .css-fis6aj{
            padding-top:0px;            /* document display below widget */
        }
        .css-ocqkz7{
            height:90px;                /* height of drag drop */
        }
        .css-k3w14i{
            display:none;
        }
        
        .css-1fqecya {
         text-align:left;           /* warning text dark */
        }
        .css-yzb2at{
            text-align:left;     /* warning text light */
        }
        
        .css-1avcm0n{
            height:0px;         /* header dark */
        }
        .css-18e3th9{
            padding-top:0rem !important;
        }
        .css-18ni7ap{                  /* header light */
            height:0px;             
        }
        
        .st-an {
            padding-top: 4px;
        }
        .css-ocqkz7{
            height:70px;            /* real */
        }
        .css-5uatcg:hover {         /* button color */
            border-color: rgb(31 202 11);
            color: rgb(31 202 11);
        }
        
        .css-5uatcg:focus:not(:active) {        /* button color */
            border-color: rgb(31 202 11);
            color: rgb(31 202 11);
        }
        
        .css-5uatcg:focus {                                                     /* button color */
            box-shadow: rgb(31 202 11 / 50%) 0px 0px 0px 0.2rem;
            outline: none;
        }
        
        # .st-co {                            /* checkbox color */
        #     background-color: rgb(31 118 35);
        # }
        # .st-d6 {                                /* checkbox color dark*/
        #     background-color: rgb(19, 23, 32);
        # }
        .st-cj {                            /* checkbox color */
            border-bottom-color: rgb(31 118 35);
        }

        .st-ci {                                    /* checkbox color */
            border-top-color: rgb(31 118 35);
        }

        .st-ch {                                    /* checkbox color */
            border-right-color: rgb(31 118 35);
        }

        .st-cg {                                    /* checkbox color */
            border-left-color: rgb(31 118 35);
        }
        
         
    </style>
    """, unsafe_allow_html=True)


st.markdown("""
        <style>
                /* page view */
               .css-18e3th9 {
                    padding-top: 2rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
               
        </style>
        """, unsafe_allow_html=True)


left, right = st.columns([1, 1])
with left:
    image = Image.open('logo.png')
    st.image(image, caption='', width=None, use_column_width=True)
with right:
    st.markdown(
        "<h2 id='seperator' style='width: 100%; text-align: center; line-height: 0.1em; margin: 10px 0 20px;'>"
        "<span style='background:transparent; padding:0 10px; color: #0074B1 '>Document Classifier</span></h2>",
        unsafe_allow_html=True)


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


#Dataframe for reference
data = [['Study Permit Application',"your application has been received"],
        ['Study Permit Application',"Principal Applicant"],
        ['Passport Process Request (PPR)',"We require your passport to finalize processing your application"],
        ['Temporary Resident Visa (TRV)','MULTIPLE'],
        ['Study Permit Approval Letter (LOI)',"letter of introduction"],
        ['Study Permit','INFORMATION DU CLIENT']]

df = pd.DataFrame(data, columns=['doctype', 'keywords'])

#To validate the document input-extracted text, output-document type
def documentValidation(text):
    recommended_doc=None
    for item in df.keywords:
        if(text.find(item) != -1):
            recommended_doc = df[['doctype']][(item==df.keywords)]['doctype'].iloc[0]
    return recommended_doc

def textExtractor(doc, file_type):
    text_extracted = ''
    if doc is not None:
        filetype = doc.type.split('/')[1]  # getting file type
        print("filetype:",filetype)
        if filetype.lower() == 'pdf':
            pdfFileObj = doc
            try:
                # pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                pdfReader = PyPDF2.PdfReader(pdfFileObj)
                # print(pdfReader.numPages)
                for i in range(0, len(pdfReader.pages)):                                             #Fixed issue PyPDF not rendering because reader.numpages is deprecated
                    pageObj = pdfReader.getPage(i)
                    text_extracted = text_extracted + '   ' + pageObj.extractText()
                pdfFileObj.close()
            except Exception as e:
                # st.warning("File contents are not clear. Please verify and re-upload a good quality file.")
                st.write(e)
                return "not_clear"
        elif filetype.lower() in ['ras', 'xwd', 'bmp', 'jpe', 'jpg', 'jpeg', 'xpm', 'ief', 'pbm', 'tif', 'gif', 'ppm',
                                  'xbm', 'tiff', 'rgb', 'pgm', 'png', 'pnm']:
            try:
                file_bytes = np.asarray(bytearray(doc.read()), dtype=np.uint8)
                opencv_image = cv2.imdecode(file_bytes, 1)
                text_extracted = img_to_text(opencv_image)
            except:
                # st.warning("Image is not clear. Please verify and re-upload a good quality file.")
                return "not_clear"
        else:
            # st.warning("Please upload a valid file (.pdf, .ras, .xwd, .bmp, .jpe, .jpg, .jpeg, .xpm, .ief, .pbm, .tif, .gif, .ppm, .xbm, .tiff, .rgb, .pgm, .png, .pnm)")
            return "invalid_file"

        if (file_type == 'Study Permit Application'):
            if text_extracted.find("your application has been received") != -1 or text_extracted.find(
                    "Principal Applicant") != -1:
                return "success"
            else:
                doc_recommended = documentValidation(text_extracted)
                if doc_recommended is None:
                    return "not_relevant"
                else:
                    return "relevant-"+doc_recommended

        elif (file_type == 'Passport Process Request (PPR)'):
            if text_extracted.find("We require your passport to finalize processing your application") != -1:
                return "success"
            else:
                doc_recommended = documentValidation(text_extracted)
                if doc_recommended is None:
                    return "not_relevant"
                else:
                    return "relevant-"+doc_recommended

        elif (file_type == 'Temporary Resident Visa (TRV)'):
            if text_extracted.find("MULTIPLE") != -1:
                return "success"
            else:
                doc_recommended = documentValidation(text_extracted)
                if doc_recommended is None:
                    return "not_relevant"
                else:
                    return "relevant-"+doc_recommended

        elif (file_type == 'Study Permit Approval Letter (LOI)'):
            if text_extracted.find("letter of introduction") != -1:
                return "success"
            else:
                doc_recommended = documentValidation(text_extracted)
                if doc_recommended is None:
                    return "not_relevant"
                else:
                    return "relevant-"+doc_recommended

        elif (file_type == 'Study Permit'):
            if text_extracted.find("INFORMATION DU CLIENT") != -1:
                return "success"
            else:
                doc_recommended = documentValidation(text_extracted)
                if doc_recommended is None:
                    return "not_relevant"
                else:
                    return "relevant-"+doc_recommended
    return ''

def fileStatus(status,file_type):
    if status is not None:
        try:
            if(status == "success"):

                set_key = file_type+"_check"
                st.checkbox("Select to confirm",key=set_key,value=True)
            elif(status == "not_clear"):
                st.warning("File contents are not clear. Please verify and re-upload a good quality file.")
            elif(status == "invalid_file"):
                st.warning("Please upload a valid file (.pdf, .ras, .xwd, .bmp, .jpe, .jpg, .jpeg, .xpm, .ief, .pbm, .tif, .gif, .ppm, .xbm, .tiff, .rgb, .pgm, .png, .pnm)")
            elif(status == "not_relevant"):
                st.warning("Looks like this is not a relevant document. Please verify.")
            elif(status.startswith("relevant")):
                st.warning(
                    '''Please make sure you uploaded the right document.  
                    This document looks like a ''' + status.split("-")[1],
                    icon="⚠️")
        except Exception as e:
            print(e)

st.markdown(
    """
    <style>
        div[data-testid="column"]:nth-of-type(1)
        {
            line-height: 2;
            display: inline-block;
            vertical-align: middle;
            text-align:center;
        } 

        div[data-testid="column"]:nth-of-type(2)
        {
            line-height: 1.5;
            display: inline-block;
            vertical-align: top;
            text-align:center;
        } 
        div[data-testid="column"]:nth-of-type(3)
        {
            padding-top:0px;
            vertical-align: middle;
            text-align:center;
        } 
    </style>
    """,unsafe_allow_html=True
)

# with st.spinner('Wait for it...'):
status1=status2=status3=status4=status5=''
left,center, right = st.columns([1,1,1.5])


with left:
    st.write("Study Permit Application")
with center:
    file_spa = st.file_uploader("",key="spa",label_visibility="collapsed")
    status_spa = textExtractor(file_spa, "Study Permit Application")
with right:
    fileStatus(status_spa,"spa")
    # st.write(status1)

left,center, right = st.columns([1,1,1.5])
with left:
    st.write("Passport Process Request (PPR)")
with center:
    file_ppr = st.file_uploader("",key="ppr",label_visibility="collapsed")
    status_ppr = textExtractor(file_ppr, "Passport Process Request (PPR)")
with right:
    fileStatus(status_ppr,"ppr")


left,center, right = st.columns([1,1,1.5])
with left:
    st.write("Temporary Resident Visa (TRV)")
with center:
    file_trv = st.file_uploader("",key="trv",label_visibility="collapsed")
    status_trv = textExtractor(file_trv, "Temporary Resident Visa (TRV)")
with right:
    fileStatus(status_trv,"trv")


left,center, right = st.columns([1,1,1.5])
with left:
    st.write("Study Permit Approval Letter (LOI)")
with center:
    file_loi = st.file_uploader("",key="loi",label_visibility="collapsed")
    status_loi = textExtractor(file_loi, "Study Permit Approval Letter (LOI)")
with right:
    fileStatus(status_loi,"loi")


left,center, right = st.columns([1,1,1.5])
with left:
    st.write("Study Permit")
with center:
    file_sp = st.file_uploader("",key="sp",label_visibility="collapsed")
    status_sp = textExtractor(file_sp, "Study Permit")
with right:
    fileStatus(status_sp,"sp")


docs_list = []
spa_check=ppr_check=loi_check=trv_check=sp_check=False
try:
    spa_check = st.session_state["spa_check"]
except:
    print("no spa key")
try:
    ppr_check = st.session_state["ppr_check"]
except:
    print("no ppr key")
try:
    trv_check = st.session_state["trv_check"]
except:
    print("no trv key")
try:
    loi_check = st.session_state["loi_check"]
except:
    print("no loi key")
try:
    sp_check = st.session_state["sp_check"]
except:
    print("no sp key")

# st.write([spa_check,ppr_check,trv_check,loi_check,sp_check])

if spa_check:
    docs_list.append("Study Permit Application")
    print(docs_list)
if ppr_check:
    docs_list.append("Passport Process Request (PPR)")
if trv_check:
    docs_list.append("Temporary Resident Visa (TRV)")
if loi_check:
    docs_list.append("Study Permit Approval Letter (LOI)")
if sp_check:
    docs_list.append("Study Permit")

# st.write(', '.join(docs_list))


def submitClick():
    if submit_button:
        names=''
        for i in docs_list:
            names  = names+", "+i
        if len(docs_list)>0:
            st.success("Documents submitted: "+names[1:])
        else:
            st.warning("No Documents Submitted")


left, center, right = st.columns([1, 1, 1.5])
with center:
    submit_button=st.button("Submit")
submitClick()



html_string = '''

<script language="javascript">
    window.scrollTo(0, 100);

</script>
'''

# components.html(html_string)
