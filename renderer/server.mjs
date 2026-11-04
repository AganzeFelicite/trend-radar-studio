import { createServer } from "node:http";

// ponytail: health only for V1.2; the render endpoint arrives with V4.1.
createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    return res.end(JSON.stringify({ status: "ok" }));
  }
  res.writeHead(404).end();
}).listen(3000, () => console.log("renderer listening on :3000"));
