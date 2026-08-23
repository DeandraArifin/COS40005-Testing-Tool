const http = require("node:http");
const { calculateInvoiceTotal } = require("./invoice");

const PORT = 3452;

const html = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Messy App</title>
  </head>
  <body>
    <h1>Messy App</h1>
    <p>Invoice total: ${calculateInvoiceTotal([{ price: 20, qty: 2 }])}</p>
  </body>
</html>`;

const server = http.createServer((request, response) => {
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(html);
});

server.listen(PORT, () => {
  process.stdout.write(`Server running at http://localhost:${PORT}\n`);
});
