// Hook PreToolUse: bloqueia edicoes acidentais nos arquivos de plano.
// A regra principal vive em CLAUDE.md; este hook e a cerca mecanica para o Claude Code.
const fs = require("fs");
const path = require("path");

let raw = "";

process.stdin.on("data", (chunk) => (raw += chunk));

process.stdin.on("end", () => {
  try {
    const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
    const approvalFlag = path.join(projectDir, ".claude", "plan-edit-approved.flag");
    const input = JSON.parse(raw);
    const toolInput = input.tool_input || {};
    const filePath = String(toolInput.file_path || toolInput.path || "").replace(/\\/g, "/");
    const protectedPaths = [
      "docs/plano-implementacao.md",
      "docs/implementation/",
    ];
    const isProtected = protectedPaths.some((protectedPath) =>
      protectedPath.endsWith("/")
        ? filePath.includes(protectedPath)
        : filePath.endsWith(protectedPath)
    );

    if (!isProtected) {
      return;
    }

    if (hasFreshApproval(approvalFlag)) {
      return;
    }

    console.log(
      JSON.stringify({
        decision: "block",
        reason:
          "TRAVA DO PLANO: antes de alterar docs/plano-implementacao.md ou docs/implementation/**, " +
          "avise o usuario em mensagem visivel e obtenha confirmacao explicita quando a mudanca " +
          "alterar escopo, prioridade, status, ordem, criterio de aceite ou itens do roadmap. " +
          "Depois da confirmacao, crie a flag local .claude/plan-edit-approved.flag e registre " +
          "claramente qual arquivo/item/CU sera alterado. A flag vale por 30 minutos.",
      })
    );
  } catch (e) {
    // Se o payload vier invalido, nao bloqueia ferramentas nao relacionadas.
  }
});

function hasFreshApproval(approvalFlag) {
  try {
    const stats = fs.statSync(approvalFlag);
    const maxAgeMs = 30 * 60 * 1000;
    return Date.now() - stats.mtimeMs <= maxAgeMs;
  } catch (e) {
    return false;
  }
}
