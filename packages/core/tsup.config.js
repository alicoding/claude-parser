import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["cjs", "esm"],
  dts: true,
  clean: true,
  treeshake: true,
  minify: true,
  target: "es2020",
  splitting: false,
  sourcemap: true,
  outDir: "dist",
  metafile: true,
  onSuccess: "echo '✅ @claude-parser/core build complete'"
})