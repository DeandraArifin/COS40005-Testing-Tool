const http = require("node:http");

const PORT = 3453;

const html = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Broken UI App</title>
  </head>
  <body>
    <h1>Broken UI App</h1>
    <p>This page is meant to fail Playwright checks.</p>
    <script>
      console.error("Payment API failed");
      throw new Error("Checkout crashed");
    </script>
  </body>
</html>`;

const server = http.createServer((request, response) => {
  response.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
  response.end(html);
});

server.listen(PORT, () => {
  process.stdout.write(`Server running at http://localhost:${PORT}\n`);
});
