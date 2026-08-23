const fs = require("node:fs");
const path = require("node:path");

const dist = path.join(__dirname, "..", "dist");
fs.mkdirSync(dist, { recursive: true });
fs.copyFileSync(
  path.join(__dirname, "..", "src", "math.js"),
  path.join(dist, "math.js"),
);
process.stdout.write("Build complete\n");
