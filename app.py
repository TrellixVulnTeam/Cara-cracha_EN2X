# Created by Davi Soares at 06/01/2021
# Projeto: CompareImageStreamlit
# Feature: # Enter feature name here
# Enter feature description here

# Scenario: # Enter scenario name here
# Enter steps here

# email: davi_soares@hotmail.com

import streamlit as st
import numpy as np
import cv2
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import imutils
from email_validator import validate_email, EmailNotValidError
import mysql.connector
from mysql.connector import Error

Image.MAX_IMAGE_PIXELS = 10000000000000


def connect(username, email, tipo, score, contador):
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='deparadb.mysql.uhserver.com',
                                       database='deparadb',
                                       user='daviso',
                                       password='daviSO2309@')
        if conn.is_connected():
            print('Connected to MySQL database')
            mycursor = conn.cursor()
            sqlstring = "INSERT INTO transacoes(nome, email, tipo, SSIM, cnts) VALUES(%s, %s, %s, %s, %s)"
            mycursor.execute(sqlstring, (username, email, tipo, score, contador))
            conn.commit()
            conn.close()
    except Error as e:
        print(e)


def main(dtimgref, dtimgmod, imgResultRGB):
    """
    main script
    Args:
        streamlit files, uploaded by the user(arg1, arg2)
    Returns:
        type: true or false (equal)
    Raises:
        Exception: description
    """
    imageA = np.array(dtimgref.convert('RGB'))
    grayA = cv2.cvtColor(imageA, cv2.COLOR_RGB2GRAY)

    imageB = np.array(dtimgmod.convert('RGB'))

    grayB = cv2.cvtColor(imageB, cv2.COLOR_RGB2GRAY)
    (score, diff) = ssim(grayA, grayB, full=True)
    diff = (diff * 255).astype("uint8")
    # st.sidebar.text("SSIM: {}".format(score))
    thresh = cv2.threshold(diff, 0, 255,
                           cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    contador = 0
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(imgResultRGB, (x, y), (x + w, y + h), (0, 0, 255), 3)
        contador = contador + 1
    contador = contador
    imagefinal = imgResultRGB
    # imagefinal = cv2.resize(imageB,(1920*2, 1080*2), interpolation=cv2.INTER_LINEAR)
    return imagefinal, score, int(contador)


if __name__ == '__main__':
    st.set_page_config(
        page_title="Cara-Crachá",

        page_icon="inspect.png",

        layout="wide",

        initial_sidebar_state="expanded")

    st.title('Cara-Crachá')
    st.text("Ferramenta online e completamente gratuita para comparar fotos, desenhos e textos")
    st.markdown('-' * 17)

    st.sidebar.title('Resultados')

    expanderinicial = st.beta_expander("Dados para envio do arquivo", expanded=True)
    if expanderinicial:
        username = expanderinicial.text_input("Digite o seu nome.")
        email = expanderinicial.text_input("Digite o seu email")
        if email != "":
            try:
                # Validate.
                valid = validate_email(email)

                # Update with the normalized form.
                email = valid.email
                expanderinicial.info("Email confirmado")

            except EmailNotValidError as e:
                # email is not valid, exception message is human-readable
                expanderinicial.warning('Email inválido')
                pass
    expander = st.beta_expander("Seleção de arquivos", expanded=True)
    if expander:
        expander.text("Procure inserir desenho na mesma dimensão e qualidade. ")
        opcoes_menu = ['Desenho', 'Foto', 'Texto']
        opcao = expander.selectbox("Escolha um tipo de análise:", opcoes_menu, index=0, )
        col1, col2 = expander.beta_columns(2)
        col1.markdown("**Carregue o desenho referência**")
        imagem_referencia = col1.file_uploader("", type=['jpg', 'jpeg', 'png'])
        if imagem_referencia is not None:
            imagemexibicao = col1.empty()
            dtimgref = Image.open(imagem_referencia)
            col1.header(opcao + " original", )
            imagemexibicao = col1.image(dtimgref, use_column_width=True)
            imageRefRGB = np.array(dtimgref.convert('RGB'))
            imageRef = cv2.cvtColor(imageRefRGB, cv2.COLOR_RGB2GRAY)
            w, h = imageRef.shape
            dimensoes = col1.text(f"Dimensões: {w} x {h}")
        else:
            col1.image("placeholder.png", width=300)
        col2.markdown("**Carregue o desenho a ser comparado**")
        imagem_modficada = col2.file_uploader("", type=['jpg', 'jpeg', 'png'], key="ImagemModif")
        if imagem_modficada is not None:
            dtimgmod = Image.open(imagem_modficada)
            col2.header(opcao + " para estudo")
            col2.image(dtimgmod, use_column_width=True)
            imageModRGB = np.array(dtimgmod.convert('RGB'))
            imageMod = np.array(dtimgmod.convert('RGB'))
            imageMod = cv2.cvtColor(imageMod, cv2.COLOR_RGB2GRAY)
            w, h = imageMod.shape
            col2.text(f"Dimensões: {w} x {h}")
        else:
            col2.image("placeholder.png", )
        if imagem_referencia is not None and imagem_modficada is not None:
            if (imageRef.shape != imageMod.shape):
                h, w = imageMod.shape
                imageRef = cv2.resize(imageRef, (w, h), interpolation=cv2.INTER_LINEAR)

                imagemexibicao = imagemexibicao.image(imageRef, use_column_width=True)
                w, h = imageRef.shape
                dimensoes = dimensoes.text(f"Dimensões: {w} x {h}")

        compararbuton = expander.button("Comparar")

    if compararbuton:
        expander2 = st.beta_expander("Resultados", expanded=True)
        if expander2:
            imagefinal, score, contador = main(imageRef, imageMod, imageModRGB)
            scoredb = "{:.2f}".format(score)
            connect(username, email, opcao, scoredb, contador)

            # imagefinal = cv2.resize(imageB,(1920*2, 1080*2), interpolation=cv2.INTER_LINEAR)
            if score < 1:
                st.sidebar.title("Status")
                st.sidebar.markdown("**Resultado:**" + " Diferença computada")
                st.sidebar.markdown(f"**SSIM: ** {score}")
                st.sidebar.markdown("**Número de divergências:** {} divergências".format(contador))
            else:
                st.sidebar.markdown("**Resultado:**" + " Arquivos iguais")

            expander2.success('Operação realizada com sucesso.')
            expander2.image(imagefinal, use_column_width=True)

    link = '[Criado por: Davi Soares](https://www.linkedin.com/in/davi-soares-batista-2a14692b/)'
    st.markdown(link, unsafe_allow_html=True)
