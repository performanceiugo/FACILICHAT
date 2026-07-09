# Hasher de senha centralizado (item B6 do plano).
#
# Antes, `PasswordHash.recommended()` era instanciado de forma duplicada em Autenticacao.py,
# Usuarios.py e no script gerenciar_banco.py. Centralizar aqui garante que os três pontos usam
# sempre o mesmo algoritmo/parâmetros (argon2) sem risco de divergirem no futuro.

from pwdlib import PasswordHash

# Instância única do hasher, reaproveitada por toda a aplicação.
pwd = PasswordHash.recommended()
