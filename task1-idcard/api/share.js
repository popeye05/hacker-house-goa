function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export default async function handler(req, res) {
  const { image, name } = req.query;

  if (!image) {
    return res.status(400).send("Missing image");
  }

  const safeName = escapeHtml(name || "HH Goa 2026 Builder");
  const safeImage = escapeHtml(image);

  res.setHeader("Content-Type", "text/html; charset=utf-8");

  res.status(200).send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />

  <title>${safeName} · HH Goa 2026</title>

  <meta
    name="description"
    content="I just built my HH Goa 2026 identity. See you in Goa!"
  />

  <meta property="og:type" content="website" />
  <meta property="og:title" content="${safeName} · HH Goa 2026" />
  <meta
    property="og:description"
    content="I just built my HH Goa 2026 identity. See you in Goa!"
  />
  <meta property="og:image" content="${safeImage}" />
  <meta property="og:image:width" content="1080" />
  <meta property="og:image:height" content="1500" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${safeName} · HH Goa 2026" />
  <meta
    name="twitter:description"
    content="I just built my HH Goa 2026 identity. See you in Goa!"
  />
  <meta name="twitter:image" content="${safeImage}" />
</head>

<body>
  <h1>${safeName} · HH Goa 2026</h1>
  <img
    src="${safeImage}"
    alt="HH Goa 2026 Builder ID"
    style="max-width:100%;height:auto;"
  />
</body>
</html>
  `);
}