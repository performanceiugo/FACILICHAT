# Importa todos os modelos para que o SQLAlchemy os registre na metadata do Base
# Necessário para que Base.metadata.create_all() em main.py crie todas as tabelas corretamente
from Modelos.Usuarios import Usuario
from Modelos.Chamados import Chamado
from Modelos.Mensagens import Mensagem
