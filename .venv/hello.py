from flask import Flask, render_template, request, Response, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import json
from teste import Grafico_1
import plotly.express as px
import plotly.graph_objects as go




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
    senha = db.Column(db.String(45))
    adm = db.Column(db.Boolean, default= False)

    def __init__(self, nome, email, senha, adm):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.adm = adm
        

# Rota para retornar todos os usuários
@app.route("/adm", methods=["GET"])
def selecionar_todos_usuarios():
    usuarios_objetos = Usuario.query.all() 

    return render_template("lista_usuarios.html", usuario_final = usuarios_objetos)


#retorna um usuario
@app.route("/adm/<id>", methods = ["GET"])
def selecionar_um_usuario(id):
    usuario_objeto = Usuario.query.get(id)

    return render_template("lista_usuarios.html", usuario = usuario_objeto)

#Cadasta Usuario
@app.route("/adm/cadastrar", methods = ["GET" , "POST"])
def criar_usuario():
    

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
              usuario_email = Usuario.query.filter_by(nome=nome).first()
              if usuario_email:
                  return redirect("/adm")
              usuario_nome = Usuario.query.filter_by(email=email).first()
              if usuario_nome:
                  return redirect("/adm")
              if(not nome):
                  print("cadastrar nome")
                  return redirect("/adm")
              if(not email):
                  print("cadastrar email")
                  return redirect("/adm")
              if(not senha):
                  print("cadastrar senha")
                  return redirect("/adm")
              
              usuario = Usuario(nome, email, senha, adm)
              db.session.add(usuario)
              db.session.commit()
              return redirect("/adm")
          except Exception as e:
              print("Erro" , e)
              return redirect("/adm")
        return redirect("/adm")
    
#Atualiza usuario
@app.route("/adm/<id>/atualizar", methods =["POST"])
def atualiza_usuario(id):
    usuario_objeto = Usuario.query.get(id)
    print(usuario_objeto.nome)

    usuario_objeto.nome = request.form['nome']
    usuario_objeto.email = request.form['email']
    usuario_objeto.senha = request.form['senha']
    
    if 'adm_alterar' in request.form:
        usuario_objeto.adm = True
    else:
        usuario_objeto.adm = False

    db.session.commit()
    return redirect('/adm')


@app.route("/adm/<id>/atualiza")
def atualizar_usuario(id):
    usuario_objeto = Usuario.query.get(id)

    return render_template("lista_usuarios.html", usuario_atualiza = usuario_objeto, atualizar = True)

#Deletar usuario
@app.route("/adm/<id>/deletar")
def deleta_usuario(id):
    usuario_objeto = Usuario.query.get(id)
    try:
        db.session.delete(usuario_objeto)
        db.session.commit()
        return redirect("/adm")
    except Exception as e:
        print("Erro", e)
        return gera_response(400, "usuario", {}, "Erro ao deletar o usuario")

    

#Reposta padrão
def gera_response(status, nome_do_conteudo, conteudo, mensagem = False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem
    
    return Response(json.dumps(body), status = status, mimetype="aplication/json")


@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route("/login", methods= ["GET", "POST"])
def login():
    if(request.method == "POST"):
        nome = request.form['nome']
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(nome=nome).first()
        if(usuario):
            if(senha == usuario.senha):
                login_user(usuario)
                return redirect("/inicial")
        return redirect("/login")
    return render_template("login.html")

@app.route("/logout", methods= ["GET", "POST"])
@login_required
def log_out():
    logout_user()
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
    #grafico = Grafico(select_city)
    #imagem_do_grafico = grafico.grafico_plot() 
    grafico = Grafico_1(select_city)
    imagem_do_grafico = grafico.grafico_plot()

    return render_template("Tela_inicial.html", cidades=cidades, select_city = imagem_do_grafico.to_html())



if __name__ == "__main__":
    app.run(debug=True)