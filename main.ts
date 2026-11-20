const { copyFileSync, mkdirSync } = require("node:fs");
const { join } = require("node:path");

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

try {
  mkdirSync(outputDir, { recursive: true });
  copyFileSync(join(botDir, "POST.json"), join(outputDir, "POST.json"));
} catch (error) {
  console.error(error);
  process.exit(1);
}
