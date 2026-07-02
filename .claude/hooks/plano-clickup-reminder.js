// Hook PostToolUse (Edit|Write): quando docs/plano-implementacao.md muda, lembra o Claude
// de sincronizar os status correspondentes na lista ClickUp "Roadmap de Implementacao".
// Não chama a API do ClickUp diretamente (sem token) — só injeta contexto para a sessão atual,
// que então usa as ferramentas MCP do ClickUp (já autenticadas na sessão) para sincronizar.
let raw = "";
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  try {
    const input = JSON.parse(raw);
    const filePath = (input.tool_input && input.tool_input.file_path) || "";
    if (filePath.replace(/\\/g, "/").includes("docs/plano-implementacao.md")) {
      const reminder =
        "O arquivo docs/plano-implementacao.md foi alterado. Sincronize os status " +
        "correspondentes na lista ClickUp \"Roadmap de Implementacao\" (list_id 901114027434) " +
        "antes de encerrar esta tarefa: cada item do plano carrega seu \"CU:\" (ID da subtarefa) " +
        "ao lado — use esse ID com as ferramentas MCP do ClickUp para mover a subtarefa ao status " +
        "correspondente. O proprio .md e a fonte da verdade dos IDs (nao ha arquivo de mapa separado).";
      console.log(
        JSON.stringify({
          hookSpecificOutput: {
            hookEventName: "PostToolUse",
            additionalContext: reminder,
          },
        })
      );
    }
  } catch (e) {
    // entrada inválida ou não-JSON: não bloqueia nada, só não emite lembrete
  }
});
