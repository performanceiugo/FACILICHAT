# Arquivo de cabeçalho: inspeciona o ambiente local do Codex no workspace para separar problema de projeto de limitação operacional.
param()

# Este bloco define a raiz do projeto e os caminhos usados nas checagens locais.
$workspace = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $workspace
$webEnvLocal = Join-Path $repoRoot "frontend\web\.env.local"
$claudeDir = Join-Path $repoRoot ".claude"
$codexDir = Join-Path $repoRoot ".codex"
$tempProbe = Join-Path $repoRoot ".tmp-codex-write-test.txt"

# Este bloco executa uma escrita controlada no workspace para verificar se a sessão consegue editar arquivos no repositório.
$workspaceWritable = $false
try {
    Set-Content -LiteralPath $tempProbe -Value "probe" -Encoding utf8
    Remove-Item -LiteralPath $tempProbe -Force
    $workspaceWritable = $true
} catch {
    $workspaceWritable = $false
}

# Este bloco coleta sinais locais que não dependem de rede nem de integrações externas.
$dockerVersion = try { docker compose version 2>$null | Select-Object -First 1 } catch { "indisponivel" }
$nodeVersion = try { node --version 2>$null } catch { "indisponivel" }
$gitStatus = try { git status --short 2>$null } catch { "indisponivel" }

# Este bloco imprime um resumo operacional curto para uso manual.
[pscustomobject]@{
    RepoRoot = $repoRoot
    WorkspaceWritable = $workspaceWritable
    ClaudeDirExists = Test-Path $claudeDir
    CodexDirExists = Test-Path $codexDir
    WebEnvLocalExists = Test-Path $webEnvLocal
    DockerCompose = $dockerVersion
    Node = $nodeVersion
    GitStatusSample = if ($gitStatus -is [array]) { ($gitStatus | Select-Object -First 5) -join "; " } else { $gitStatus }
    Nota = "ClickUp MCP e outras ferramentas da sessao precisam ser validadas pelo proprio agente; este script so cobre ambiente local."
} | Format-List
