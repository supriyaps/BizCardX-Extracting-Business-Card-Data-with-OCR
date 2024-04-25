









import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import pandas as pd
import numpy as np
import easyocr
import re
import io
import sqlite3

def Image_to_text(path):
  input_image= Image.open(path)

  #converting image to array format

  image_arr = np.array(input_image)

  reader= easyocr.Reader(['en'])
  text= reader.readtext(image_arr, detail=0)
  return text , input_image

def extracted_text(texts):
  extracted_dict = {"NAME":[], "DESIGNATION":[], "COMAPNY_NAME":[],  "CONTACT":[], "EMAIL":[] , "WEBSITE":[],"ADDRESS":[] , "PINCODE":[]  }

  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2, len(texts)):

    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extracted_dict["CONTACT"].append(texts[i])
    elif "@" in texts[i] and ".com" in texts[i]:
      extracted_dict["EMAIL"].append(texts[i])
    elif "WWW" in texts[i] or "www" in texts[i]  or "Www" in texts[i] or "WwW" in texts[i]  or "wwW" in texts[i]:
      small= texts[i].lower()
      extracted_dict["WEBSITE"].append(small)

    elif "Tamil Nadu"  in texts[i] or "TamilNadu" in texts[i]   or texts[i].isdigit():
      extracted_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):
      extracted_dict["COMAPNY_NAME"].append(texts[i])
    else:
      remove_colon= re.sub(r'[,;]' , '',texts[i])
      extracted_dict["ADDRESS"].append(remove_colon)

  for key,value in extracted_dict.items():
    # print(key,";" , value , len(value))
    if (len(value)>0):
      concatenate= " ".join(value)
      extracted_dict[key] = [concatenate]
    else:
      value= "NA"
      extracted_dict[key] = [value]


  return extracted_dict






#streamlit code

st.set_page_config(layout= "wide")
st.title("BizCardX: Extracting Business Card Data with OCR")
st.divider()
st.subheader('Submitted by Supriya Ps')
with st.sidebar:

  select= option_menu("Main Menu" , ["Home", "upload & modify" ,"delete data"])
if select ==  "Home":
  st.title('Technologies')
  st.markdown('OCR,streamlit GUI, SQL,Data Extraction')
elif select == "upload & modify":
  img = st.file_uploader("upload your image" , type=["png","jpg","jpeg"])
  if img is not None:
    st.image(img, width= 300)

    text_image, input_img= Image_to_text(img)

    text_dict = extracted_text(text_image)


    if text_dict:
      st.success(" Text HAS BEEN EXTRACTED")

    df=pd.DataFrame(text_dict)

    #converting image to bytes

    Image_bytes = io.BytesIO()   #calling the package through a variable
    input_img.save(Image_bytes, format= "PNG")  #using that variable to save the image in bytes format

    image_data = Image_bytes.getvalue()

    #creating dictionary

    data = {"IMAGE" : [image_data]}

    df_1 = pd.DataFrame(data)

    concat_df = pd.concat([df,df_1], axis= 1)
    st.dataframe(concat_df)

    button_1 = st.button("Save")
    if button_1:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      #table creation

      create_table_querry = '''CREATE TABLE IF NOT EXISTS bizcardx_details(name varchar(225),
                                                                              designation varchar(225),
                                                                              company_name varchar(225),
                                                                              contact varchar(225),
                                                                              email varchar(225),
                                                                              website text,
                                                                              address text,
                                                                              pincode varchar(225),
                                                                              image text)'''


      cursor.execute(create_table_querry)
      mydb.commit()


      #inser querry

      insert_querry = ''' INSERT INTO bizcardx_details(name,designation,company_name,contact,email,website,address,pincode,image)

                                            values(?,?,?,?,?,?,?,?,?)'''

      datas = concat_df.values.tolist()[0]
      cursor.execute(insert_querry,datas)
      mydb.commit()

      st.success("Saved Successfully")

  method = st.radio("select the method",["none","preview","Modify"])
  if method == "none":
    st.write("")

  if method =="preview":
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()
    # select querry

    select_query = " SELECT * FROM bizcardx_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))
    st.dataframe(table_df)


  elif method =="Modify":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()
    # select querry

    select_query = " SELECT * FROM bizcardx_details"

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns=("NAME","DESIGNATION","COMPANY","CONTACT","EMAIL","WEBSITE","ADDRESS","PINCODE","IMAGE"))

    col1,col2 = st.columns(2)
    with col1:

      selected_name = st.selectbox("Slect the name",table_df["NAME"])

    df_3 = table_df[table_df["NAME"]== selected_name]

    df_4 = df_3.copy()



    col1.col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("Name",df_3["NAME"].unique()[0])
      mo_designation = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
      mo_company = st.text_input("Company",df_3["COMPANY"].unique()[0])
      mo_contact = st.text_input("Conatact",df_3["CONTACT"].unique()[0])
      mo_email = st.text_input("Email",df_3["EMAIL"].unique()[0])

      df_4["NAME"] = mo_name
      df_4["DESIGNATION"] = mo_designation
      df_4["COMPANY"] = mo_company
      df_4["CONTACT"] = mo_contact
      df_4["EMAIL"] = mo_email

    with col2:
      mo_website = st.text_input("Website",df_3["WEBSITE"].unique()[0])
      mo_address = st.text_input("Address",df_3["ADDRESS"].unique()[0])
      mo_pincode = st.text_input("Pincode",df_3["PINCODE"].unique()[0])
      mo_image = st.text_input("Image",df_3["IMAGE"].unique()[0])


      df_4["WEBSITE"] = mo_website
      df_4["ADDRESS"] = mo_address
      df_4["PINCODE"] = mo_pincode
      df_4["IMAGE"] = mo_image

    st.dataframe(df_4)
    col1,col2= st.columns(2)
    with col1:
      button_3 = st.button("Modify")

    if button_3:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      cursor.execute(f"DELETE FROM bizcardx_details WHERE NAME = '{selected_name}'")
      mydb.commit()

      #insert

      insert_querry = ''' INSERT INTO bizcardx_details(name,designation,company_name,contact,email,website,address,pincode,image)

                                            values(?,?,?,?,?,?,?,?,?)'''

      datas = df_4.values.tolist()[0]
      cursor.execute(insert_querry,datas)
      mydb.commit()

      st.success("Data modified Successfully")

elif select == "delete data":
    # select querry

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    col1,col2= st.columns(2)
    with col1:

      select_query = " SELECT NAME FROM bizcardx_details"

      cursor.execute(select_query)
      table1 = cursor.fetchall()
      mydb.commit()

      names = []

      for i in table1:
        names.append(i[0])

      name_select = st.selectbox("Select the name" , names)

    with col2:

      select_query2 = f"SELECT DESIGNATION FROM bizcardx_details  WHERE NAME ='{name_select}'"

      cursor.execute(select_query2)
      table2 = cursor.fetchall()
      mydb.commit()

      designations = []

      for j in table2:
        designations.append(j[0])

      designation_select = st.selectbox("Select the designation", options = designations)

    if name_select and designation_select:
      col1,col2,col3= st.columns(3)

      with col1:
        st.write(f"Selected Name : {name_select}")
        st.write("")
        st.write("")
        st.write("")
        st.write(f"Selected Designation : {designation_select}")

      with col2:
         st.write("")
         st.write("")
         st.write("")
         st.write("")


         remove = st.button("Delete")

         if remove:

          cursor.execute(f"DELETE FROM bizcardx_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
          mydb.commit()

          st.warning("DELETED")




















