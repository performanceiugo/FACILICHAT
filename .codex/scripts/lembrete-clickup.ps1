# Arquivo de cabeçalho: emite um lembrete operacional de sincronização do ClickUp a partir do plano local quando o Codex não tiver integração ativa.
param()

# Este bloco localiza o plano do projeto e lê apenas as linhas que contêm tabela com status.
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$planPath = Join-Path $repoRoot "docs\plano-implementacao.md"
$planLines = Get-Content -LiteralPath $planPath | Where-Object { $_ -match '^\| `\[[ ~x]\]` \|' }

# Este bloco destaca itens em andamento e itens pendentes sem automação de board.
$inProgress = $planLines | Where-Object { $_ -match '\| `\[~\]` \|' }
$pending = $planLines | Where-Object { $_ -match '\| `\[\ \]` \|' } | Select-Object -First 10

Write-Output "Lembrete: se o item alterado tiver CU no plano, sincronize o status correspondente no ClickUp."
Write-Output "Se o Codex nao tiver MCP de ClickUp nesta sessao, faca a sincronizacao manualmente."
Write-Output ""
Write-Output "Itens em andamento encontrados no plano:"
if ($inProgress) {
    $inProgress
} else {
    Write-Output "- nenhum item [~] encontrado"
}
Write-Output ""
Write-Output "Amostra de itens pendentes:"
if ($pending) {
    $pending
} else {
    Write-Output "- nenhum item [ ] encontrado"
}
