// Runs the JavaScript and TypeScript exercise tests with Node's built-in test runner.
//
//   npm test                                  # every JS and TS exercise
//   npm test -- javascript                    # one set
//   npm test -- javascript/01_greet_user      # one exercise
//
// No packages to install. TypeScript files run through Node's built-in type
// stripping (on by default from Node 22.18 and 23.6), which removes the types
// and runs the rest as JavaScript. It does NOT type-check your code.
import { readdirSync, statSync, existsSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = fileURLToPath(new URL(".", import.meta.url));
const [major] = process.versions.node.split(".").map(Number);
if (major < 22) {
  console.error(`Node ${process.versions.node} is too old. Install Node 22.18+ (or the current LTS).`);
  process.exit(1);
}

const targets = process.argv.slice(2);
const roots = (targets.length ? targets : ["javascript", "typescript"]).map((t) => join(here, t));

const files = [];
for (const root of roots) {
  if (!existsSync(root)) {
    console.error(`No such folder: ${relative(here, root) || root}`);
    process.exit(1);
  }
  if (statSync(root).isFile()) { files.push(root); continue; }
  for (const rel of readdirSync(root, { recursive: true })) {
    const parts = rel.split(sep);
    if (parts.includes("solution") || parts.includes("node_modules")) continue;
    if (/\.test\.(js|mjs|ts)$/.test(rel)) files.push(join(root, rel));
  }
}
if (!files.length) {
  console.error("No test files found.");
  process.exit(1);
}

const flags = process.features?.typescript ? [] : ["--experimental-strip-types"];
const result = spawnSync(process.execPath, [...flags, "--test", ...files.sort()], { stdio: "inherit", cwd: here });
process.exit(result.status ?? 1);
