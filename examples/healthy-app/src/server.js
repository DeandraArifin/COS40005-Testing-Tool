const http = require("node:http");
const { add, formatCurrency } = require("./math");

const PORT = 3451;

const html = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Healthy App</title>
  </head>
  <body>
    <h1>Healthy App</h1>
    <p>Total: ${formatCurrency(add(19.99, 5))}</p>
  </body>
</html>`;

const server = http.createServer((request, response) => {
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(html);
});

server.listen(PORT, () => {
  process.stdout.write(`Server running at http://localhost:${PORT}\n`);
});
