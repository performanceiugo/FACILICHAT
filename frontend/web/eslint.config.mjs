// Config explícita do ESLint (flat config) — substitui o assistente interativo do "next lint",
// que será removido no Next.js 16. FlatCompat traduz os presets legados do Next.js
// ("next/core-web-vitals", "next/typescript") para o formato flat.
import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  // .next/out/build sao artefatos gerados; next lint os ignorava por padrao, o eslint . direto não
  { ignores: [".next/**", "out/**", "build/**", "next-env.d.ts"] },
  ...compat.extends("next/core-web-vitals", "next/typescript"),
];

export default eslintConfig;
