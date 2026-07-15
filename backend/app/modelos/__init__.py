# Importa todos os modelos para que o SQLAlchemy os registre na metadata do Base
# Necessário para que Base.metadata.create_all() em main.py crie todas as tabelas corretamente
from app.modelos.Empresa import Empresa, EmpresaConfiguracao
from app.modelos.Condominio import Condominio
from app.modelos.Usuarios import Usuario
from app.modelos.Chamados import Chamado
from app.modelos.Mensagens import Mensagem
from app.modelos.SessaoRevogada import SessaoRevogada
from app.modelos.RefreshToken import RefreshToken
from app.modelos.CoberturaTurno import CoberturaTurno
