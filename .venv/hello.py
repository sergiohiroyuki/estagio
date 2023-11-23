from flask import Flask, render_template, request, Response, jsonify, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from teste import Grafico_1
import plotly.express as px
import plotly.graph_objects as go
from flask_paginate import Pagination, get_page_args
from werkzeug.security import generate_password_hash, check_password_hash
import re


app = Flask(__name__)
app.secret_key = 'Testando_1_Chave_Secreta_201013415'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:senha@localhost/estagio'

db = SQLAlchemy(app)

login_maneger = LoginManager()
login_maneger.init_app(app)
login_maneger.login_view = 'login'

@login_maneger.user_loader
def load_user(id):
    return Usuario.query.get(id)

#cria tabela
class Usuario(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    nome = db.Column(db.String(45), unique = True)
    email = db.Column(db.String(45), unique = True)
    senha = db.Column(db.String(228))
    adm = db.Column(db.Boolean, default= False)
    historico = db.relationship('Historico')

    def __init__(self, nome, email, senha, adm):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.adm = adm

class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    nome = db.Column(db.String(45))
    data_hora = db.Column(db.DateTime(timezone=True), default = func.now())
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __init__(self, nome, id_usuario):
        self.nome = nome   
        self.id_usuario = id_usuario     

# Rota para retornar todos os usuários
@app.route("/adm", methods=["GET"])
@login_required
def selecionar_todos_usuarios():
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):
        usuarios_objetos = Usuario.query.all() 
        return render_template("lista_usuarios.html", usuario_final = usuarios_objetos)
    return redirect("/inicial")


#retorna um usuario
@app.route("/adm/<id>", methods = ["GET"])
@login_required
def selecionar_um_usuario(id):
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):
        usuario_objeto = Usuario.query.get(id)
        return render_template("lista_usuarios.html", usuario = usuario_objeto)
    return redirect("/inicial")

#Cadasta Usuario
@app.route("/adm/cadastrar", methods = ["GET" , "POST"])
@login_required
def criar_usuario():
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):

        if(request.method == 'POST'):
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']
            adm = 'adm_cadastrar' in request.form
            nome = nome.strip()
            email = email.strip()
            senha = senha.strip()

            if(senha == confirmar_senha):
                try:
                    usuario_email = Usuario.query.filter_by(email=email).first()
                    if usuario_email:
                        flash("Email já Cadastrado", "error")
                        app.logger.info("Email já Cadastrado")
                        return redirect("/adm")
                    
                    usuario_nome = Usuario.query.filter_by(nome=nome).first()
                    if usuario_nome:
                        app.logger.info("Nome já Cadastrado")
                        flash("Nome já Cadastrado" , "error")
                        return redirect("/adm")
                    
                    if(not nome):
                        print("vasio")
                        flash("Campo Precisa Ser Prenchido", "error")
                        return redirect("/adm")
                    
                    if(not email):
                        print("vasio")
                        flash("Campo Precisa Ser Prenchido", "error")
                        return redirect("/adm")
                    
                    regex_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                    if not(re.match(regex_email, email)):
                        flash("e-mail precisar ter esse formato", "error")
                        return redirect("/adm")
                    
                    if(not senha):
                        print("vasio")
                        flash("Campo Precisa Ser Prenchido", "error")
                        return redirect("/adm")

                    if(len(senha) < 8):
                        flash("Senha precisa ter 8 caracteres no mínimo", "error")
                        return redirect("/adm")
                    
                    regex_senha = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$')

                    if not(regex_senha.match(senha)):
                        flash("Senha precisa ter caracteres especiais(!@#$%¨&*), letra maiúsculas e minúsculas e conter valores numéricos", "error")
                        return redirect("/adm")
                    
                    senha_hash = generate_password_hash(senha)

                    usuario = Usuario(nome, email, senha_hash, adm)
                    app.logger.info("Usuário criado com sucesso")
                    flash("Usuário Cadastrado com Sucesso!!", "success")
                    db.session.add(usuario)
                    db.session.commit()
                    return redirect("/adm")
                except Exception as e:
                    print("Erro" , e)
                    return redirect("/adm")
            flash("As Senhas Informadas são Diferentes", "error")    
            return redirect("/adm")
    return redirect("/inicial")
    
#Atualiza usuario
@app.route("/adm/<id>/atualizar", methods =["POST"])
@login_required
def atualiza_usuario(id):
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):
        usuario_objeto = Usuario.query.get(id)
        print(usuario_objeto.nome)

        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        nome = nome.strip()
        email = email.strip()
        senha = senha.strip()

        usuario_email = Usuario.query.filter_by(email=email).first()
        if(usuario_email):
            usuario_validar_email = usuario_email.email 
        else:
             usuario_validar_email = "email não existe"
             app.logger.info("email não encontrado!!!")  
        if (usuario_validar_email == usuario_objeto.email):
            app.logger.info("email Ok!!!")
        elif usuario_email:
            flash("Email já Cadastrado", "error")
            app.logger.info("Email já Cadastrado")
            return redirect("/adm")
        
                            
        usuario_nome = Usuario.query.filter_by(nome=nome).first()
        if(usuario_nome):
            usuario_validar_nome = usuario_nome.nome
        else:
             usuario_validar_nome = "nome não existe"
             app.logger.info("nome não encontrado!!!") 
        if (usuario_validar_nome == usuario_objeto.nome):
            app.logger.info("nome Ok!!!!")
        elif usuario_nome:
            app.logger.info("Nome já Cadastrado")
            flash("Nome já Cadastrado" , "error")
            return redirect("/adm")
        
        
        if(not nome):
            print("vasio")
            flash("Campo Precisa Ser Prenchido", "error")
            return redirect("/adm")
        
        if(not email):
            print("vasio")
            flash("Campo Precisa Ser Prenchido", "error")
            return redirect("/adm")
        
        regex_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not(re.match(regex_email, email)):
            flash("e-mail precisar ter esse formato", "error")
            return redirect("/adm")

        

        usuario_objeto.nome = nome
        usuario_objeto.email = email
        app.logger.info(senha)
        app.logger.info(usuario_objeto.senha)
        if(senha):
            if(len(senha) < 8):
                flash("Senha precisa ter 8 caracteres no mínimo", "error")
                return redirect("/adm")
        
            regex_senha = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$')

            if not(regex_senha.match(senha)):
                flash("Senha precisa ter caracteres especiais(!@#$%¨&*), letra maiúsculas e minúsculas e conter valores numéricos", "error")
                return redirect("/adm")
            app.logger.info(senha)
            app.logger.info(usuario_objeto.senha)
            usuario_objeto.senha = generate_password_hash(senha)
            app.logger.info(senha)
            app.logger.info(usuario_objeto.senha)
        
        
        if 'adm_alterar' in request.form:
            usuario_objeto.adm = True
        else:
            usuario_objeto.adm = False

        flash("Usuário Atualizado com Sucesso!!", "success")
        db.session.commit()
        return redirect('/adm')
    return redirect("/inicial")


@app.route("/adm/<id>/atualiza")
@login_required
def atualizar_usuario(id):
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):
        usuario_objeto = Usuario.query.get(id)

        return render_template("lista_usuarios.html", usuario_atualiza = usuario_objeto, atualizar = True)
    return redirect("/inicial")

#Deletar usuario
@app.route("/adm/<id>/deletar")
@login_required
def deleta_usuario(id):
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    if(usuario.adm == True):
        usuario_objeto = Usuario.query.get(id)
        try:
            flash("Usuário Deletado com Sucesso!!", "success")
            db.session.delete(usuario_objeto)
            db.session.commit()
            return redirect("/adm")
        except Exception as e:
            print("Erro", e)
            return redirect("/adm")
    return redirect("/inicial")


@app.route("/")
def inicial():
    return render_template("home.html")


@app.route("/login", methods= ["GET", "POST"])
def login():
    if(request.method == "POST"):
        nome = request.form['nome']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(nome=nome).first()
        if(usuario):
            if(check_password_hash(usuario.senha, senha) ):
                login_user(usuario)
                if(usuario.adm == True):
                    flash("Usuário logado com sucesso!!" , "success")
                    return redirect("/adm")
                else:
                    flash("Usuário logado com sucesso!!", "success")
                    return redirect("/inicial")
        flash("Verifique o Nome ou a Senha!!", "error")
        return redirect("/login")
    return render_template("login.html")

@app.route("/logout", methods= ["GET", "POST"])
@login_required
def log_out():
    logout_user()
    flash("Usuário Saiu da Aplicação com Sucesso!!", "success")
    return redirect("/login")

@app.route("/inicial")
@login_required
def Tela_Inicial():
    cidades = ["Abatiá", "Altamira do Paraná", "Alto Paraná", "Alto Piquiri", "Altônia", "Alvorada do Sul", "Ampére", "Anahy", "Andirá", "Ângulo",
  "Antônio Olinto", "Apucarana", "Arapoti", "Arapuã", "Araruna", "Araucária", "Ariranha do Ivaí", "Assaí", "Assis Chateaubriand", "Astorga",
  "Atalaia", "Balsa Nova", "Bandeirantes", "Barbosa Ferraz", "Barra do Jacaré", "Barracão", "Bela Vista da Caroba", "Bela Vista do Paraíso",
  "Bituruna", "Boa Esperança", "Boa Esperança do Iguaçu", "Boa Ventura de São Roque", "Boa Vista da Aparecida",
  "Bom Jesus do Sul", "Bom Sucesso", "Bom Sucesso do Sul", "Borrazópolis", "Braganey", "Brasilândia do Sul", "Cafeara",
  "Cafelândia", "Cafezal do Sul", "Califórnia", "Cambará", "Cambé", "Cambira", "Campina da Lagoa", "Campina do Simão",
  "Campo Bonito", "Campo do Tenente", "Campo Largo", "Campo Magro", "Campo Mourão", "Cândido de Abreu", "Candói", "Cantagalo", "Capanema",
  "Capitão Leônidas Marques", "Carambeí", "Carlópolis", "Cascavel", "Castro", "Catanduvas", "Centenário do Sul", "Céu Azul", "Chopinzinho",
  "Cianorte", "Cidade Gaúcha", "Clevelândia", "Colorado", "Congonhinhas", "Conselheiro Mairinck", "Contenda", "Corbélia", "Cornélio Procópio",
  "Coronel Domingos Soares", "Coronel Vivida", "Corumbataí do Sul", "Cruz Machado", "Cruzeiro do Iguaçu", "Cruzeiro do Oeste", "Cruzeiro do Sul",
  "Cruzmaltina", "Curiúva", "Diamante do Sul", "Diamante D'Oeste", "Dois Vizinhos", "Douradina", "Doutor Camargo", "Enéas Marques",
  "Engenheiro Beltrão", "Entre Rios do Oeste", "Espigão Alto do Iguaçu", "Farol", "Faxinal", "Fazenda Rio Grande", "Fênix", "Fernandes Pinheiro",
  "Figueira", "Flor da Serra do Sul", "Floraí", "Floresta", "Florestópolis", "Flórida", "Formosa do Oeste", "Foz do Iguaçu", "Foz do Jordão",
  "Francisco Alves", "Francisco Beltrão", "General Carneiro", "Godoy Moreira", "Goioerê", "Goioxim", "Grandes Rios", "Guaíra", "Guamiranga",
  "Guapirama", "Guaporema", "Guaraci", "Guaraniaçu", "Guarapuava", "Honório Serpa", "Ibaiti", "Ibema", "Ibiporã", "Icaraíma", "Iguaraçu",
  "Iguatu", "Imbaú", "Imbituva", "Indianópolis", "Ipiranga", "Iporã", "Iracema do Oeste", "Irati", "Iretama", "Itaguajé", "Itaipulândia",
  "Itambaracá", "Itambé", "Itapejara d'Oeste", "Ivaí", "Ivaiporã", "Ivatuba", "Jaboti", "Jaguapitã", "Jaguariaíva", "Jandaia do Sul",
  "Janiópolis", "Japira", "Japurá", "Jardim Alegre", "Jardim Olinda", "Jataizinho", "Jesuítas", "Joaquim Távora", "Jundiaí do Sul",
  "Juranda", "Jussara", "Kaloré", "Lapa", "Laranjal", "Laranjeiras do Sul", "Leópolis", "Lidianópolis", "Lindoeste", "Lobato", "Londrina",
  "Luiziana", "Lunardelli", "Lupionópolis", "Mallet", "Mamborê", "Mandaguaçu", "Mandaguari", "Mandirituba", "Manfrinópolis", "Mangueirinha",
  "Manoel Ribas", "Marechal Cândido Rondon", "Maria Helena", "Marialva", "Marilândia do Sul", "Mariluz", "Maringá", "Mariópolis", "Maripá",
  "Marmeleiro", "Marquinho", "Marumbi", "Matelândia", "Mauá da Serra", "Medianeira", "Mercedes", "Mirador", "Miraselva", "Missal",
  "Moreira Sales", "Munhoz de Melo", "Nossa Senhora das Graças", "Nova Aliança do Ivaí", "Nova América da Colina", "Nova Aurora", "Nova Cantu",
  "Nova Esperança", "Nova Esperança do Sudoeste", "Nova Fátima", "Nova Laranjeiras", "Nova Prata do Iguaçu", "Nova Santa Bárbara",
  "Nova Santa Rosa", "Nova Tebas", "Novo Itacolomi", "Ortigueira", "Ourizona", "Ouro Verde do Oeste", "Paiçandu", "Palmas", "Palmeira",
  "Palmital", "Palotina", "Paraíso do Norte", "Paranacity", "Paranapoema", "Paranavaí", "Pato Bragado", "Pato Branco", "Paula Freitas",
  "Paulo Frontin", "Peabiru", "Perobal", "Pérola d'Oeste", "Pinhal de São Bento", "Pinhalão", "Pinhão", "Piraí do Sul", "Piraquara",
  "Pitanga", "Pitangueiras", "Planalto", "Ponta Grossa", "Porecatu", "Porto Amazonas", "Porto Barreiro", "Porto Vitória", "Prado Ferreira",
  "Pranchita", "Presidente Castelo Branco", "Primeiro de Maio", "Prudentópolis", "Quarto Centenário", "Quatro Pontes", "Quedas do Iguaçu",
  "Querência do Norte", "Quinta do Sol", "Quitandinha", "Ramilândia", "Rancho Alegre", "Rancho Alegre D'Oeste", "Realeza", "Rebouças",
  "Renascença", "Reserva", "Reserva do Iguaçu", "Ribeirão Claro", "Ribeirão do Pinhal", "Rio Azul", "Rio Bom", "Rio Bonito do Iguaçu",
  "Rio Branco do Ivaí", "Rio Negro", "Rolândia", "Roncador", "Rondon", "Rosário do Ivaí", "Salgado Filho", "Salto do Itararé", "Salto do Lontra",
  "Santa Amélia", "Santa Cecília do Pavão", "Santa Cruz de Monte Castelo", "Santa Fé", "Santa Helena", "Santa Inês", "Santa Isabel do Ivaí",
  "Santa Izabel do Oeste", "Santa Lúcia", "Santa Maria do Oeste", "Santa Mariana", "Santa Mônica", "Santa Tereza do Oeste", "Santa Terezinha de Itaipu",
  "Santana do Itararé", "Santo Antônio da Platina", "Santo Antônio do Paraíso", "Santo Antônio do Sudoeste", "Santo Inácio", "São Carlos do Ivaí",
  "São Jerônimo da Serra", "São João", "São João do Ivaí", "São João do Triunfo", "São Jorge do Ivaí", "São Jorge do Patrocínio", "São Jorge d'Oeste",
  "São José da Boa Vista", "São José das Palmeiras", "São José dos Pinhais", "São Manoel do Paraná", "São Mateus do Sul", "São Miguel do Iguaçu",
  "São Pedro do Iguaçu", "São Pedro do Ivaí", "São Sebastião da Amoreira", "São Tomé", "Sapopema", "Sarandi", "Saudade do Iguaçu",
  "Sengés", "Serranópolis do Iguaçu", "Sertaneja", "Sertanópolis", "Siqueira Campos", "Sulina", "Tamarana", "Tamboara", "Teixeira Soares",
  "Telêmaco Borba", "Terra Boa", "Terra Roxa", "Tibagi", "Tijucas do Sul", "Toledo", "Tomazina", "Três Barras do Paraná", "Tuneiras do Oeste",
  "Tupãssi", "Turvo", "Ubiratã", "Umuarama", "União da Vitória", "Uniflor", "Uraí", "Ventania", "Vera Cruz do Oeste", "Verê", "Virmond",
  "Vitorino", "Wenceslau Braz"]

    return render_template("Tela_inicial.html", cidades=cidades, select_city='')


@app.route('/inicial', methods=['POST'])
@login_required
def index():
    cidades = ["Abatiá", "Altamira do Paraná", "Alto Paraná", "Alto Piquiri", "Altônia", "Alvorada do Sul", "Ampére", "Anahy", "Andirá", "Ângulo",
  "Antônio Olinto", "Apucarana", "Arapoti", "Arapuã", "Araruna", "Araucária", "Ariranha do Ivaí", "Assaí", "Assis Chateaubriand", "Astorga",
  "Atalaia", "Balsa Nova", "Bandeirantes", "Barbosa Ferraz", "Barra do Jacaré", "Barracão", "Bela Vista da Caroba", "Bela Vista do Paraíso",
  "Bituruna", "Boa Esperança", "Boa Esperança do Iguaçu", "Boa Ventura de São Roque", "Boa Vista da Aparecida",
  "Bom Jesus do Sul", "Bom Sucesso", "Bom Sucesso do Sul", "Borrazópolis", "Braganey", "Brasilândia do Sul", "Cafeara",
  "Cafelândia", "Cafezal do Sul", "Califórnia", "Cambará", "Cambé", "Cambira", "Campina da Lagoa", "Campina do Simão",
  "Campo Bonito", "Campo do Tenente", "Campo Largo", "Campo Magro", "Campo Mourão", "Cândido de Abreu", "Candói", "Cantagalo", "Capanema",
  "Capitão Leônidas Marques", "Carambeí", "Carlópolis", "Cascavel", "Castro", "Catanduvas", "Centenário do Sul", "Céu Azul", "Chopinzinho",
  "Cianorte", "Cidade Gaúcha", "Clevelândia", "Colorado", "Congonhinhas", "Conselheiro Mairinck", "Contenda", "Corbélia", "Cornélio Procópio",
  "Coronel Domingos Soares", "Coronel Vivida", "Corumbataí do Sul", "Cruz Machado", "Cruzeiro do Iguaçu", "Cruzeiro do Oeste", "Cruzeiro do Sul",
  "Cruzmaltina", "Curiúva", "Diamante do Sul", "Diamante D'Oeste", "Dois Vizinhos", "Douradina", "Doutor Camargo", "Enéas Marques",
  "Engenheiro Beltrão", "Entre Rios do Oeste", "Espigão Alto do Iguaçu", "Farol", "Faxinal", "Fazenda Rio Grande", "Fênix", "Fernandes Pinheiro",
  "Figueira", "Flor da Serra do Sul", "Floraí", "Floresta", "Florestópolis", "Flórida", "Formosa do Oeste", "Foz do Iguaçu", "Foz do Jordão",
  "Francisco Alves", "Francisco Beltrão", "General Carneiro", "Godoy Moreira", "Goioerê", "Goioxim", "Grandes Rios", "Guaíra", "Guamiranga",
  "Guapirama", "Guaporema", "Guaraci", "Guaraniaçu", "Guarapuava", "Honório Serpa", "Ibaiti", "Ibema", "Ibiporã", "Icaraíma", "Iguaraçu",
  "Iguatu", "Imbaú", "Imbituva", "Indianópolis", "Ipiranga", "Iporã", "Iracema do Oeste", "Irati", "Iretama", "Itaguajé", "Itaipulândia",
  "Itambaracá", "Itambé", "Itapejara d'Oeste", "Ivaí", "Ivaiporã", "Ivatuba", "Jaboti", "Jaguapitã", "Jaguariaíva", "Jandaia do Sul",
  "Janiópolis", "Japira", "Japurá", "Jardim Alegre", "Jardim Olinda", "Jataizinho", "Jesuítas", "Joaquim Távora", "Jundiaí do Sul",
  "Juranda", "Jussara", "Kaloré", "Lapa", "Laranjal", "Laranjeiras do Sul", "Leópolis", "Lidianópolis", "Lindoeste", "Lobato", "Londrina",
  "Luiziana", "Lunardelli", "Lupionópolis", "Mallet", "Mamborê", "Mandaguaçu", "Mandaguari", "Mandirituba", "Manfrinópolis", "Mangueirinha",
  "Manoel Ribas", "Marechal Cândido Rondon", "Maria Helena", "Marialva", "Marilândia do Sul", "Mariluz", "Maringá", "Mariópolis", "Maripá",
  "Marmeleiro", "Marquinho", "Marumbi", "Matelândia", "Mauá da Serra", "Medianeira", "Mercedes", "Mirador", "Miraselva", "Missal",
  "Moreira Sales", "Munhoz de Melo", "Nossa Senhora das Graças", "Nova Aliança do Ivaí", "Nova América da Colina", "Nova Aurora", "Nova Cantu",
  "Nova Esperança", "Nova Esperança do Sudoeste", "Nova Fátima", "Nova Laranjeiras", "Nova Prata do Iguaçu", "Nova Santa Bárbara",
  "Nova Santa Rosa", "Nova Tebas", "Novo Itacolomi", "Ortigueira", "Ourizona", "Ouro Verde do Oeste", "Paiçandu", "Palmas", "Palmeira",
  "Palmital", "Palotina", "Paraíso do Norte", "Paranacity", "Paranapoema", "Paranavaí", "Pato Bragado", "Pato Branco", "Paula Freitas",
  "Paulo Frontin", "Peabiru", "Perobal", "Pérola d'Oeste", "Pinhal de São Bento", "Pinhalão", "Pinhão", "Piraí do Sul", "Piraquara",
  "Pitanga", "Pitangueiras", "Planalto", "Ponta Grossa", "Porecatu", "Porto Amazonas", "Porto Barreiro", "Porto Vitória", "Prado Ferreira",
  "Pranchita", "Presidente Castelo Branco", "Primeiro de Maio", "Prudentópolis", "Quarto Centenário", "Quatro Pontes", "Quedas do Iguaçu",
  "Querência do Norte", "Quinta do Sol", "Quitandinha", "Ramilândia", "Rancho Alegre", "Rancho Alegre D'Oeste", "Realeza", "Rebouças",
  "Renascença", "Reserva", "Reserva do Iguaçu", "Ribeirão Claro", "Ribeirão do Pinhal", "Rio Azul", "Rio Bom", "Rio Bonito do Iguaçu",
  "Rio Branco do Ivaí", "Rio Negro", "Rolândia", "Roncador", "Rondon", "Rosário do Ivaí", "Salgado Filho", "Salto do Itararé", "Salto do Lontra",
  "Santa Amélia", "Santa Cecília do Pavão", "Santa Cruz de Monte Castelo", "Santa Fé", "Santa Helena", "Santa Inês", "Santa Isabel do Ivaí",
  "Santa Izabel do Oeste", "Santa Lúcia", "Santa Maria do Oeste", "Santa Mariana", "Santa Mônica", "Santa Tereza do Oeste", "Santa Terezinha de Itaipu",
  "Santana do Itararé", "Santo Antônio da Platina", "Santo Antônio do Paraíso", "Santo Antônio do Sudoeste", "Santo Inácio", "São Carlos do Ivaí",
  "São Jerônimo da Serra", "São João", "São João do Ivaí", "São João do Triunfo", "São Jorge do Ivaí", "São Jorge do Patrocínio", "São Jorge d'Oeste",
  "São José da Boa Vista", "São José das Palmeiras", "São José dos Pinhais", "São Manoel do Paraná", "São Mateus do Sul", "São Miguel do Iguaçu",
  "São Pedro do Iguaçu", "São Pedro do Ivaí", "São Sebastião da Amoreira", "São Tomé", "Sapopema", "Sarandi", "Saudade do Iguaçu",
  "Sengés", "Serranópolis do Iguaçu", "Sertaneja", "Sertanópolis", "Siqueira Campos", "Sulina", "Tamarana", "Tamboara", "Teixeira Soares",
  "Telêmaco Borba", "Terra Boa", "Terra Roxa", "Tibagi", "Tijucas do Sul", "Toledo", "Tomazina", "Três Barras do Paraná", "Tuneiras do Oeste",
  "Tupãssi", "Turvo", "Ubiratã", "Umuarama", "União da Vitória", "Uniflor", "Uraí", "Ventania", "Vera Cruz do Oeste", "Verê", "Virmond",
  "Vitorino", "Wenceslau Braz"]
    
    select_city = request.form.get('cidade')

    #grafico = Grafico_1(select_city)
    #imagem_do_grafico = grafico.grafico_plot()
    #fig = px.line(imagem_do_grafico, x='Ano', y=['Valores Previstos (Passado)', 'Valores Reais', 'Valores Previstos (Futuros)'],
    #                  labels={'Ano': 'Ano', 'value': 'Produção de Soja'}, title=f'Produção de Soja - Nome da Cidade - {select_city}')


    id = current_user.id
    historico = Historico(select_city, id)
    db.session.add(historico)
    db.session.commit()

    return redirect(f"/resultados/{select_city}")

@app.route('/resultados/<select_city>')
@login_required
def resultados(select_city):
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    grafico = Grafico_1(select_city)
    imagem_do_grafico = grafico.grafico_plot()
    fig_linha = px.line(imagem_do_grafico, x='Ano', y=['Valores Previstos (Passado)', 'Valores Reais', 'Valores Previstos (Futuros)'],
                      labels={'Ano': 'Ano', 'value': 'Produção de Soja'}, title=f'Produção de Soja - Nome da Cidade - {select_city}')

    fig_barra = px.bar(imagem_do_grafico, x='Ano', y=['Valores Previstos (Passado)', 'Valores Reais', 'Valores Previstos (Futuros)'],
             barmode='group',
             labels={'Ano': 'Ano', 'value': 'Produção de Soja'},
             title=f'Produção de Soja - Nome da Cidade - {select_city}')
    
    imagem_do_grafico.fillna('- -', inplace=True)
    
    return render_template("resultados.html", usuario = usuario, grafico_de_linha = fig_linha.to_html(), grafico_de_barras = fig_barra.to_html(), tabela = imagem_do_grafico.to_html())

@app.route('/historico_usuario', methods=["GET"])
@login_required
def historico_usuario():
    page = request.args.get('page', type=int, default=1)
    per_page = 10
    id = current_user.id
    nome_usuario = current_user.nome

    historico = Historico.query.filter_by(id_usuario=id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("historico_usuario.html", historico=historico, nome_usuario=nome_usuario)

@app.route('/historico_geral', methods=['GET'])
@login_required
def historico_geral():
    page = request.args.get('page', 1, type=int) 
    per_page = 10  
    id_usuario = current_user.id
    usuario = Usuario.query.get(id_usuario)
    
    if usuario.adm:
        query = db.session.query(Historico.id, Historico.nome, Historico.data_hora, Usuario.id, Usuario.nome).join(Historico)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        historico = pagination.items
        
        return render_template("historico_geral.html", historico=historico, pagination=pagination)
    
    return redirect("/inicial")


@app.route('/historico_geral/<id>', methods = ["GET" , "POST"])
@login_required
def garfico_historico_geral(id):
    id_historico = Historico.query.get(id)
    select_city = id_historico.nome

    return redirect(f"/resultados/{select_city}")

@app.route('/historico_usuario/<id>', methods = ["GET" , "POST"])
@login_required
def garfico_historico_usuario(id):
    id_historico = Historico.query.get(id)
    select_city = id_historico.nome

    return redirect(f"/resultados/{select_city}")



if __name__ == "__main__":
    app.run(debug=True)