import os
import sys
import django

# Make sure this is set before any Django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# Append project path to sys.path if needed
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Initialize Django
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

# Now you can safely import your models
from django.contrib.auth.models import User
from core.models import Client

# The data to be imported (you can also load this data from a file if needed)
data = """
09940055535742005;Ademir Whitman
02222303000092009;Adriana Santana Gomes Gomides
02227601004329003;Alex Tonaco Milhomem
02222345000001009;Alice Rodrigues
09880008014104003;Ana Maria Vilarins
00881404000689008;Andre Saraiva Da Silva
02228000000812000;Cleber Mendes
00306151000256000;Dalton Oliveira
02223167000189001;Danubia Carlos Fernandes
02220411002142000;Dilene De Sousa Martins
09941984254390004;Diogo Almeida de Souza
02222303000068000;Divina Margarida
02220969000036010;Eder Coelho
09942271251884005;Edivanio Pereira Silva Vasconcelos
02220607000177013;Edson Fernandes
08650001387261103;Eduardo Rocha Rosa Camargo
00482083141009866;Esio Harrison
09942115505953308;Ester de Cassia
00643740000035122;Filipe Simoes
01782428011707004;GUSTAVO LUZ VALADAO
02220768000181000;Helainy Brito Leopoldino Mendes
02222303000045000;Iraildes Alves Hawat
02227604001810007;Iulia Lima da Silva
02220937000092035;Ivonete Cirqueira
03174071400054323;Jordana Marques Silva
00648000068721718;Jose Francisco
02222303000024003;Luis Carlos Pereira Coelho
09942271251852014;LUSINETE RUBINS SANTOS GAMA
02222303000153008;Maria Alice Alves Dos Santos
02222303000119012;Maria do Espirito Santo
02640103760001800;Maria Gabriela
02222055000218006;Maria Rodrigues Barros
02222200000080000;Mayda Pimenta
08650002978591014;Naide Reis Araujo
02538441000001825;Nicolas Andre Oliveira Zilio
01830000000399723;Nilda de Godoy
02220411000034137;Pedro Lucas Mota
02222303000084006;Raimundo Aguiar Rosado
08650002661679007;Rosalice Martins de S. Moura
02220764001154012;Rosyvonne Caliar
08650001114424009;Sabrine Araújo
00060503633005014;Savia Barbosa
02229000000489094;Shavio Rocha Cabral
08650002253077004;Tatiane de Jesus
02220448000277012;Terezinha de Jesus Barroso Gomes
02222303000031018;Tomariza das Merces Parente Lopes
02223167000166001;Veraluce Teodoro Goncalves
02220639000062028;Helena Fonseca De Abreu
03178600200014108;Gilson Gabriel Matias Rocha
02220411002215031;Havila Stefen Fernandes
09942407267443004;HEYTOR VICTOR ARAUJO SILVA
00648000004960002;Deusanira Carneiro Gomes
02220910000711027;Gilson Rodrigues Gama
03175051100327007;Terezinha Carreiro da Silva
08650004379257008;THAIZ M L A
09942216536415000;WILLIAM MELO DOS SANTOS
02223167000256019;Gael Martins Maciel
09942368288525307;Maria Laura Costa Silva
08650002473651010;Maria Miriam Fogaca Maricato
00291600577000120;Claudia Barros Pereira Battistela
00648000003060008;Maria Lina Peres de Souza
03175476100001013;EDILEUZA OLIVEIRA HONORIO
09942265505547000;CARLOS EDUARDO GOMES CARVALHO
02640102690705008;Carlos Eduardo
02220639000776012;BELLA BASTOS AZEVEDO
03175051100707004;Luciana Batista Martins
02220448000467016;Nilce Eth da Silva Santos
02640102690586009;Moises Lucio Medeiro
02222303000083000;Eliane de Fatima Brito
02228000000812019;Maria do Socorro Sousa Mota
08650002978590000;Edison Mendes
09700030002086338;Pedro Claudino de Oliveira Neto
08650002253024016;LETICIA COIMBRA DAME
02222303000090006;Sueli Vieira de Faria
02222303000039035;Jucileia Pereira Roberto Torres
08650003239231008;Celio Pereira Rodrigues
02222303000169010;WAGNER RAFAEL SOARES LEMOS
02222380000001007;Iraci Rodrigues Santana
02220411001958014;Benavinuta Lira
02223167000171030;Onilza Naves Rabelo
08650004173988015;Elaine Alves Souza
02222507000017002;Maria Eurlene Gomes Carvalho
00648000007241007;MARIA MARLENE LEAO FERREIRA MIRANDA
08650002975986000;HELSON DIAS BEZERRA
02222362000001033;Ester Monteiro Camargo
02223167000125003;CELIA MARIA FREITAS
02220607000033003;Cidiclei Alcione Biavatti
02220764001512008;JAKELINE DE MORAIS E OLIVEIRA SANTOS
02220642000081022;Pedro Henrique Rodrigues Roque de Oliveira
02286235000363011;TAYNARA RIBEIRO FERNANDES MENDES
00649117002814099;Kaline Lima Ramos
02222343000001010;SELENITA CARDOSO DA SILVA
02228000000867034;Murilo Jose Carvalho
01920600334213587;MATHEUS MARTINS LIMA
02223187000001007;Dulcilene Freitas Oliveira
08650001888659312;RUTE FARIAS ALVES
02227601001834009;Rosinalva Ferreira Bringel Viana
08650002578147001;Emivaldo Rocha Gomes
02222303000071036;Simone Martins Araujo Bandeira
02223167000108010;Fabio Melo Gomes
08650003288554001;Timoteo Candido Lopes da Silva
02222395000002001;Denys Kerson Ferreira da Mota
02222303000004010;GIOVANNA ARAUJO GAMA DE ALMEIDA
03175950200188016;Marcos Antonio Dias
02227602002005004;Fabiana Guida Pereira Abreu
02640107700004008;Edina Correia Miguel
02223167000167016;Maria Cirqueira
09941852262087000;Tahiana Miranda
02223167000292007;Matheus Abraao
02640102690660004;Paulo Ernane
00482071683013832;Maria Antonia
00648000140799005;Bernardo Barale Afonso
02223167000111002;Alvina Maria de Jesus Santos
02222346000001023;Rodrigo Garcia Martins
00648000077390672;Maria de Fatima Lima de Oliveira
02220448000883125;Mateus Junior Rocha Soares
00643740000035092;SEBASTIANA REGINA DIAS
02223078000001001;Adao Pereira Mota
02220607000033011;Iramar Alessandra Medeiros Assuncao
02223187000001023;Jorge Luiz Barros Oliveira
08650002975654015;HELLEN PRESTES GOMES
09880157001500031;Cristina Sardinha Wanderley
02220648000013000;Antonia Pinheiro Barbosa
02220411002261033;Gyzely Gonçalves da Silva
02220411000006516;Roseli Pereira da Silva
01960834030000007;Cristiane Rempel
02222303000146010;Custodia Maria Teles
02220607001617033;Arthur Aires dos Santos Santana
02222342000001004;Joelma Mendes Rodrigues Nogueira
02640102690268317;MARIA EDUARDA TUPINAMBA OLIVEIRA
02222222000109513;Maria Arlete Reis de Azevedo
09942306256765108;Eduardo Oliveira MEDEIROS
09942306256765000;Wagner Marinho
02222383000001001;Maria Eterna Ferreira Pimenta
01782428011704005;Thiago Emanoel Rodrigues Alves
02220770000016001;Simon Barbosa Ferreira Borges
02227603001736003;Joao Pedro Cardoso Ramos
02222303000140003;Francisco Carlos Macedo Barbosa
08650000659729012;Sonia Aparecida Veras Santana
02222292000081008;RAFAEL RODRIGUES ALMEIDA
08650002252730014;VERA LUCIA BEZERRA DA LUZ
09949369256910309;Laura Rodrigues Camargo
02222303000128011;Maria Jose dos Reis Castro
00640000000136700;Cristino Ribeiro Malta Neto
02222303000125020;VERA REGINA ALVES
08650004097197008;IRON TEODORO DA SILVA
08650003691582000;BRUNO PEREIRA DOS SANTOS 
00340087000332008;MARIA FATIMA ALVES SILVA
02222303000012005;ALDEMAR BRUSTOLONI
02223167000021003;Rosilene Rodrigues Costa
00648000163321004;KARLA SABRINA NASCIMENTO OLIVEIRA
02220401000323107;Joao Pedro Conceicao Renz
02222303000076003;ELIANE RODRIGUES MARINHO
02222303000142006;Florineide Costa Caldeira Mota
02223136000002009;Maria das Merces da Conceicao Luz Ferreira
02222303000061006;Maria Eliete Santos
08650002252700000;Agmar Borba de Miranda
02640102690567004;JOSE VILSON NOLETO CAMPOS
02220411000034013;Leila dos Santos Mota
02220411000135103;Marcos Emanuel Miranda Mendes
02220411000142010;Isabela Cristine Martins Lima Macedo
09942314264472026;KALLITA RIBEIRO SILVA
00649999020019004;Luis Eduardo Veras Santos
02222303000025000;Gisanne Gomes da Silva Miranda
01020000003514015;Hugo Puhl Bif
09942271251429006;Diana da Sena Pereia
02223150000001016;Marcia Helena Mendes Rosa Silva
09942136536501002;Cesar Augusto de Sa Moreira
02220401000323026;Tatiana Da Silva Conceicao Renz
02220764001223014;Anderson Parente Santos
02222303000004002;Ercalenia Araujo Gama de Almeida
02222303000141026;Gabriela Rodrigues Barros
00690000165698007;ALEXANDRE RENTZ SOLEK
02223167000151004;JOELMA MARINHO DE SOUZA
02222386000001006;NADIR MARIA RIBEIRO
00060504717791000;FRANCISCO DE PAULA FERREIRA
08650002975502320;ISADORAH SANTOS MONTEL LOURENÇO
02222303000118008;MARIA MENDONCA MARTINS
02222303000138009;GEICE LEA DIAS DE OLIVEIRA LEMOS
02227601002031015;EDERSON HIDEKI NAKATA
08650001387232014;ANA CRISTINA NEVES OVANDO
00648000091810683;VALTENIO A B
09942271251635013;ANNE C S V
00482071683004230;Renata Marinho de Castro
02222303000040017;MARIA A G D S
09941521251238020;Osmair de Jesus Rua
02220411001129000;NILSON P S
02640103300058000;BRUNA CESÁRIO BARBOSA
02223059000279003;Kelly Cristina Nascente
"""
# Split the data into id_card and name pairs
client_data = [line.split(";") for line in data.strip().split("\n")]


def import_clients():
    for codigo_beneficiario, nome_beneficiario in client_data:
        Client.objects.get_or_create(
            codigo_beneficiario=codigo_beneficiario,
            nome_beneficiario=nome_beneficiario,
            tipo_atendimento="3",
            quantidade="1",
            active=True,
            user=User.objects.first(),  # Or any other user logic
        )

    print("Data import completed.")


# Call the import function
import_clients()