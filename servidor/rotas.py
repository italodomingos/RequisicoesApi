import time
from servidor import app
from flask import request, render_template
from uau import rendimentos
import receita_federal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from static.autenticacao import login_email, senha_email


@app.route('/consulta_receitafederal', methods=['POST', 'GET'])
def consulta_receitafederal():
    if request.method == 'POST':
        try:
            time.sleep(5)
            cnpj = request.json['cnpj']
            print(cnpj)
            return receita_federal.consultar(cnpj)

        except:
            return {"Error": f"Requisição {request.json} não é válida"}
    else:
        try:
            cnpj = request.values['cnpj']
            print(cnpj)
            return receita_federal.consultar(cnpj)

        except:
            return {"Error": f"Parâmetro {request.values.keys()} não é válido"}


@app.route('/informe_rendimentos', methods=['GET'])
def informe_redimentos():
    if request.method == 'GET':
        return rendimentos.envia_informe_rendimentos()
    else:
        return 'Só o método GET é aceito'


@app.route('/canvas')
def canvas():
    return render_template('canvas.html')


@app.route('/email')
def email():
    host = 'smtp.office365.com'
    port = 587
    user = login_email
    password = senha_email
    email = smtplib.SMTP(host, port)
    email.starttls()
    email.login(user, password)

    msg = MIMEMultipart()
    msg['From'] = user
    msg['Subject'] = f"Informe de Rendimentos - Bambuí"
    msg['To'] = 'italo.domingos@bambui.com.br'
    with open('static/email bgreat.html', encoding='utf-8') as html:
        msg.attach(MIMEText(html.read(), 'html'))

    # for k, anexo_base64 in enumerate(anexos_base64):
    #     byte = base64.b64decode(anexo_base64)
    #     with open("static/rendimentos.pdf", "wb") as fp:
    #         fp.write(byte)
    #     attachment = open('static/rendimentos.pdf', 'rb')
    #     part = MIMEBase('application', 'octet-stream')
    #     part.set_payload(attachment.read())
    #     encoders.encode_base64(part)
    #     part.add_header('Content-Disposition', f"attachment; filename=Rendimentos-Bambui-{k + 1}.pdf")
    #     msg.attach(part)
    #     attachment.close()
    #     fp.close()

    email.sendmail(user, 'italo.domingos@bambui.com.br', msg.as_string())
    print("E-mail enviado com sucesso!")

    email.quit()
    time.sleep(1)
    return "E-mail enviado com sucesso!"
