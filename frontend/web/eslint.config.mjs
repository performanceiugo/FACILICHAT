// Config explícita do ESLint (flat config nativo do Next.js 16 — item V5). Substitui o
// assistente interativo do "next lint" (removido na v16) e o shim `FlatCompat` usado até a v15
// para traduzir os presets legados: `eslint-config-next` agora exporta flat config direto.
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // .next/out/build sao artefatos gerados; next lint os ignorava por padrao, o eslint . direto não
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);

export default eslintConfig;
