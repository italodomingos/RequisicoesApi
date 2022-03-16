import requests
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import time
import base64
from email import encoders
import pandas as pd
from static.autenticacao import token_uau, login_uau, senha_uau
from static.autenticacao import login_email, senha_email


def envia_email(destinatario, corpo, anexos_base64, nome, ano):
    host = 'smtp.office365.com'
    port = 587
    email = smtplib.SMTP(host, port)
    email.starttls()
    email.login(login_email, senha_email)

    msg = MIMEMultipart()
    msg['From'] = login_email
    msg['Subject'] = f"Informe de Rendimentos - Bambuí - {nome} - {ano}"
    msg['To'] = destinatario
    msg.attach(MIMEText(corpo, 'html'))

    for k, anexo_base64 in enumerate(anexos_base64):
        byte = base64.b64decode(anexo_base64)
        with open("static/rendimentos.pdf", "wb") as fp:
            fp.write(byte)
        attachment = open('static/rendimentos.pdf', 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename=Rendimentos-Bambui-{k+1}.pdf")
        msg.attach(part)
        attachment.close()
        fp.close()

    email.sendmail(login_email, destinatario, msg.as_string())
    print("E-mail enviado para {}".format(nome))
    email.quit()
    time.sleep(1)


def get_autenticador():

    headers = {"X-INTEGRATION-Authorization": token_uau,
        "Content-Type": "application/json"}
    data = {
        'login': login_uau,
        'senha': senha_uau
    }

    request = requests.post("http://45.191.207.245:8080/uauAPI/api/v1.0/Autenticador/AutenticarUsuario", headers=headers, data=str(data))
    return request.json()


def envia_informe_rendimentos():
    headers = {
            "X-INTEGRATION-Authorization": token_uau,
            "Content-Type": "application/json",
            "Authorization": get_autenticador()
                   }

    clientes_df = pd.DataFrame()
    ano_base = datetime.datetime.now().year - 1

    request = requests.post("http://45.191.207.245:8080/uauAPI/api/v1.0/Pessoas/ConsultarPessoasComVenda", headers=headers)
    clientes = request.json()[0]['Pessoas']

    for i, cliente in enumerate(clientes):
        rendimentos = []

        if i != 0:
            data = {"codigo_usuario": cliente['Cod_pes']}
            request = requests.post("http://45.191.207.245:8080/uauAPI/api/v1.0/Venda/ConsultarEmpreendimentosCliente", headers=headers, data=str(data))
            empreendimentos_cliente = request.json()[0]['MyTable']

            if len(empreendimentos_cliente) > 1:
                for j, empreendimento in enumerate(empreendimentos_cliente):

                    if j != 0:
                        data = {
                                  "vendasobras_empresa": [
                                      [
                                          str(empreendimento['Num_Ven']),
                                          str(empreendimento['Obra_Ven']),
                                          str(empreendimento['Empresa_ven'])
                                      ]
                                  ],
                                      "ano_base": ano_base,
                                      "naomostradados_venda": "true"
                              }

                        request = requests.post("http://45.191.207.245:8080/uauAPI/api/v1.0/RelatorioIRPF/GerarPDFRelIRPF", headers=headers, data=str(data))
                        rendimentos.append(request.json())

        if len(rendimentos) > 0 and rendimentos[0]:
            data = {"codigo_pessoa": cliente['Cod_pes']}
            request = requests.post("http://45.191.207.245:8080/uauAPI/api/v1.0/Pessoas/ConsultarPessoaPorChave",
                                    headers=headers, data=str(data))
            pessoa = request.json()[0]['MyTable'][1]
            try:
                if pessoa['Email_pes']:
                    emails = pessoa['Email_pes'].split(';')
                    for email in emails:
                        clientes_df = clientes_df.append({'Nome': pessoa['nome_pes'], 'CPF': pessoa['cpf_pes'], 'E-mail': email}, ignore_index=True)
                        with open('../static/email rendimentos.html', encoding='utf-8') as html:
                            envia_email(email, html.read(), rendimentos, pessoa['nome_pes'], ano_base)
            except:
                clientes_df = clientes_df.append({'Nome': pessoa['nome_pes'], 'CPF': pessoa['cpf_pes'], 'E-mail': email,
                                                  'Erro': 'E-mail não enviado'}, ignore_index=True)


        # if i >= 100:
        #     break
    writer = pd.ExcelWriter('static/rendimento_enviados.xlsx')
    clientes_df.to_excel(writer)
    writer.save()
