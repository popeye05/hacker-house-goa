import { put } from "@vercel/blob";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    // Vercel reliably parses application/json bodies into req.body.
    // The client sends { image: "data:image/png;base64,..." }
    const { image } = req.body || {};

    if (!image || typeof image !== "string") {
      return res.status(400).json({ error: "No image received" });
    }

    // Strip the data URL prefix to get raw base64
    // "data:image/png;base64,<data>" -> "<data>"
    const base64 = image.replace(/^data:image\/\w+;base64,/, "");
    const buffer = Buffer.from(base64, "base64");

    if (buffer.length === 0) {
      return res.status(400).json({ error: "Empty image" });
    }

    console.log("Upload received:", buffer.length, "bytes");

    const blob = await put(
      `hh-goa-${Date.now()}.png`,
      buffer,
      {
        access: "public",
        contentType: "image/png",
        token: process.env.BLOB_READ_WRITE_TOKEN,
      }
    );

    console.log("Upload successful:", blob.url);

    return res.status(200).json({ url: blob.url });
  } catch (error) {
    console.error("Upload error:", error);
    return res.status(500).json({
      error: error.message || "Failed to upload image",
    });
  }
}
