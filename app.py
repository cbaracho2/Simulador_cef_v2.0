import streamlit as st;
import numpy as np
import pandas as pd
import numpy_financial as npf

st.title("Simulador de Crédito Caixa / 7LM")
st.subheader ('Análise do potencial de financiamento') 

df = pd.read_excel("Base_Preços.xlsx")

df_001 = pd.DataFrame(df.groupby("CIDADE")['CIDADE'].count())
df_001 = df_001.rename(columns={"CIDADE":"COL1"})
df_001 = df_001.reset_index()
cidades_list = list(df_001['CIDADE'].values[0:2].astype(str))

df_003 = pd.DataFrame(df.groupby(["CIDADE","CÓD"])['CIDADE'].count())
df_003 = df_003.rename(columns={"CIDADE":"COL1"})
df_003 = df_003.reset_index()

df_004 = pd.DataFrame(df.groupby(["CIDADE","CÓD","BLOCO"])['CIDADE'].count())
df_004 = df_004.rename(columns={"CIDADE":"COL1"})
df_004 = df_004.reset_index()

df_005 = pd.DataFrame(df.groupby(["CIDADE","CÓD","BLOCO","UNIDADE"])['CIDADE'].count())
df_005 = df_005.rename(columns={"CIDADE":"COL1"})
df_005 = df_005.reset_index()

df_002 = pd.DataFrame(df.groupby(["CIDADE","CÓD","BLOCO","UNIDADE","VALOR DE AVALIAÇÃO (1x)\n--","VALOR LIQUIDO"])['CIDADE'].count())
df_002 = df_002.rename(columns={"CIDADE":"COL1","VALOR DE AVALIAÇÃO (1x)\n--":"VALOR DE AVALIAÇÃO"})
df_002 = df_002.reset_index()





checkbox_mostrar_tabela = st.sidebar.checkbox('Cadastrar Dados')



if checkbox_mostrar_tabela:
    st.sidebar.markdown('## Escolher a Cidade')
    cidades_list = st.sidebar.selectbox('Selecione a cidade para simular o plano', options = cidades_list)
    df_003 = df_003.loc[df_003.CIDADE == cidades_list]
    empreend_list = list(df_003['CÓD'].values[0:5])
    emp = st.sidebar.selectbox("Escolha o empreendimento", options= empreend_list)
    df_004 = df_004.loc[(df_004.CIDADE == cidades_list) & (df_004['CÓD'] == emp)]
    blocos_list = list(df_004['BLOCO'].values[0:30])
    bloco = st.sidebar.selectbox("Escolha o Bloco", options=blocos_list)
    df_005 = df_005.loc[(df_005.CIDADE == cidades_list) & (df_005['CÓD'] == emp) & (df_005['BLOCO'] == bloco)]
    unidades_list = list(df_005['UNIDADE'].values[0:500])
    #st.sidebar.selectbox("Escolha a Unidade", options=unidades_list)
    unidade = st.sidebar.selectbox("Escolha a Unidade", options=unidades_list)
    #apartamento = st.sidebar.text_input(label="Apartamento")
    #sinal = st.sidebar.number_input(label="Valor do sinal", format="%.5f")
    preco = df_002.loc[((df_002.CIDADE == cidades_list) & (df_002.CÓD == emp) & (df_002.BLOCO == bloco) & (df_002.UNIDADE == unidade)),"VALOR LIQUIDO"].values[0]
    st.sidebar.write(preco, format="%.5f")
    st.write("Valor de Total de Vendas:", preco)





with st.form(key="include"):
    
    input_age = st.number_input(label="Insira sua idade")
    input_renda = st.number_input(label="Qual sua renda?", format="%.5f")
    input_VGV = st.number_input(label="Qual o Valor de TOTAL do apê?", format="%.5f")
    input_avaliacao = st.number_input(label="Qual o Valor de avaliação do apê?", format="%.5f")
    input_solteiro = st.checkbox(label="Solteiro")
    input_casado = st.checkbox("Casado")
    input_viuvo =st.checkbox("Viúvo")
    input_uniao = st.checkbox("União Estável")
    #input_select = st.multiselect ("Solteiro", "Casado")
    btconfirma = st.form_submit_button("Simular")
    

    def dependente():
        if (input_casado == True) or (input_uniao == True):
            return 1
        else:
            return 0.5
    
    def juros_aa_cef(renda):
        if renda <= 2000:
            return float(5.25)
        elif renda<=2600:
            return float(5.50)
        elif renda<=3000:
            return float(6.00)
        elif renda<=4000:
            return float(7.00)
        elif renda<=7000:
            return float(8.16)
        else:
            return float(8.16)
        
    DFI = 0.000073

    def calculo_MIP(idade, Avaliacao):
        if idade <= 25:
            return float(Avaliacao * 0.00011500)
        elif idade <= 35:
            return float(Avaliacao * 0.00017800)
        elif idade <= 45:
            return float(Avaliacao * 0.00031800)
        elif idade <= 55:
            return float(Avaliacao * 0.00075100)
        elif idade <= 65:
            return float(Avaliacao * 0.00278100)
        elif idade <= 75:
            return float(Avaliacao *0.00470700)
        else:
            return float(Avaliacao *0.00470700)
    
    def calculo_FGHAB(idade, renda):
        if idade <= 25:
            return float(renda * 0.02)
        elif idade <= 35:
            return float(renda * 0.0214)
        elif idade <= 40:
            return float(renda *0.0232)
        elif idade <= 45:
            return float(renda * 0.0309)
        elif idade <= 50:
            return float(renda * 0.0352)
        elif idade <= 75:
            return float(renda *0.0714)
        else:
            return float(renda *0.0714)

        
    COMP_SAC =  0.3
    COMP_PRICE = 0.29843
    DEP = dependente()
    #AVALIACAO = 137500
    PRAZO_TOTAL_POUP = 48
    PRAZO_PRE = 24       
    PRAZO_POS = 24
    SUB_MAX = 21090
    SUB_MIN = 2350
    PISO_RENDA = 1800
    RENDA_SUB_MIN = 3275
    RENDA_SUB_MAX = 4000
    #JUROS_AA = juros_aa_cef(RENDA_FAMILIAR)
    #PRAZO = 360
    COEF1 = float(0.00861361677678828)
    COEF2 = float(-25.4101694915254)


    def CALCULAR_SUB(RENDA):
        SUBSIDIO_1  = np.round((COEF1*((RENDA-PISO_RENDA)**2)+COEF2*(RENDA-PISO_RENDA)+SUB_MAX),0)
        if RENDA == 0:
            return float(0.0)
        elif RENDA > RENDA_SUB_MAX:
            return float(0.0)
        elif SUBSIDIO_1 > SUB_MAX:
            return float(SUB_MAX * dependente())
        elif (RENDA > RENDA_SUB_MIN) and (RENDA <=RENDA_SUB_MAX):
            return float(SUB_MIN * dependente())
        else:
            return float(SUBSIDIO_1 * dependente())
    
    def calculo_potencial_pgto_cef(idade, renda, avaliacao, prazo):
        list_PRICE = []
        list_SAC = []
        MIP = calculo_MIP(idade, avaliacao)
        COTA = avaliacao * 0.8
        VALOR_DFI = DFI * COTA
        PRICE = -npf.pv((juros_aa_cef(renda)/12/100), prazo, (COMP_PRICE*renda)-MIP-VALOR_DFI)
        SAC = np.round((renda * COMP_SAC) - MIP - VALOR_DFI)/(1/prazo+(juros_aa_cef(renda)/1200))
        list_PRICE.append([COTA,PRICE])
        list_SAC.append([COTA,SAC])
        PRICE_001 = min(min(list_PRICE))
        SAC_001 = min(min(list_SAC))
        return np.round(SAC_001,2), np.round(PRICE_001,2)
    


    sac = calculo_potencial_pgto_cef(input_age, input_renda, input_avaliacao, 360)[0]
    price = calculo_potencial_pgto_cef(input_age, input_renda, input_avaliacao, 360)[1]


    if btconfirma:
        #st.write(f' Potencial de: $ {sac} SAC.')
        #st.write(f' Potencial de: $ {price} PRICE.')
        #st.write(f"Subsídio de: ${CALCULAR_SUB(input_renda)}")
        df = pd.DataFrame(np.random.randn(1, 5), columns=['idade','renda','Fin_Sac','Fin_Price','Subsídio'])
        df['idade'] = input_age
        df['renda'] = input_renda
        df['Fin_Sac'] = sac
        df['Fin_Price'] = price
        df['Subsídio'] = CALCULAR_SUB(input_renda)
        st.write(df)
    
    