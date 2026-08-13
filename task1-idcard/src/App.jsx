import { useRef, useState } from "react";
import heic2any from "heic2any";
import hhGoaLogo from "./assets/SVGLogo.svg";

const BUILDER_CLASSES = [
  "THE SHIPPER",
  "THE ARCHITECT",
  "THE HACKER",
  "THE BUILDER",
  "THE DEBUGGER",
  "THE DISRUPTOR",
  "THE SYSTEM THINKER",
  "THE NIGHT OWL",
];

function App() {
  const fileInputRef = useRef(null);

  const [preview, setPreview] = useState(null);
  const [imageBlob, setImageBlob] = useState(null);
  const [name, setName] = useState("");
  const [stack, setStack] = useState("");
  const [builderClass, setBuilderClass] = useState("");
  const [isSharing, setIsSharing] = useState(false);

  // -----------------------------
  // HANDLE IMAGE UPLOAD
  // -----------------------------

  const handleFile = async (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    try {
      let imageFile = file;

      const isHEIC =
        file.type === "image/heic" ||
        file.type === "image/heif" ||
        file.name.toLowerCase().endsWith(".heic") ||
        file.name.toLowerCase().endsWith(".heif");

      if (isHEIC) {
        const converted = await heic2any({
          blob: file,
          toType: "image/jpeg",
          quality: 0.92,
        });

        imageFile = Array.isArray(converted)
          ? converted[0]
          : converted;
      }

      const imageUrl = URL.createObjectURL(imageFile);

      setPreview(imageUrl);
      setImageBlob(imageFile);

      const randomClass =
        BUILDER_CLASSES[
          Math.floor(
            Math.random() * BUILDER_CLASSES.length
          )
        ];

      setBuilderClass(randomClass);
    } catch (error) {
      console.error(error);

      alert(
        "Couldn't process that image. Try another photo."
      );
    }
  };

  // -----------------------------
  // LOAD IMAGE
  // -----------------------------

  const loadImage = (src) =>
    new Promise((resolve, reject) => {
      const image = new Image();

      image.onload = () => resolve(image);
      image.onerror = reject;

      image.src = src;
    });

  // -----------------------------
  // COVER IMAGE
  // -----------------------------

  const drawCoverImage = (
    ctx,
    image,
    x,
    y,
    width,
    height
  ) => {
    const imageRatio =
      image.width / image.height;

    const boxRatio = width / height;

    let sourceWidth;
    let sourceHeight;
    let sourceX;
    let sourceY;

    if (imageRatio > boxRatio) {
      sourceHeight = image.height;
      sourceWidth =
        image.height * boxRatio;

      sourceX =
        (image.width - sourceWidth) / 2;

      sourceY = 0;
    } else {
      sourceWidth = image.width;
      sourceHeight =
        image.width / boxRatio;

      sourceX = 0;

      sourceY =
        (image.height - sourceHeight) / 2;
    }

    ctx.drawImage(
      image,
      sourceX,
      sourceY,
      sourceWidth,
      sourceHeight,
      x,
      y,
      width,
      height
    );
  };

  // -----------------------------
  // GENERATE FINAL CARD
  // -----------------------------

  const createCardBlob = async () => {
    if (!imageBlob) return null;

    const canvas =
      document.createElement("canvas");

    const width = 1080;
    const height = 1500;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");

    if (!ctx) {
      throw new Error(
        "Canvas is not supported."
      );
    }

    const imageUrl =
      URL.createObjectURL(imageBlob);

    const image =
      await loadImage(imageUrl);

    URL.revokeObjectURL(imageUrl);

    // -----------------------------
    // BACKGROUND
    // -----------------------------

    ctx.fillStyle = "#006B45";

    ctx.fillRect(
      0,
      0,
      width,
      height
    );

    // -----------------------------
    // HEADER
    // -----------------------------

    ctx.fillStyle = "#006B45";

    ctx.fillRect(
      0,
      0,
      width,
      100
    );

    ctx.fillStyle = "#FFD900";
    ctx.font = "bold 30px Arial";
    ctx.textAlign = "left";

    ctx.fillText(
      "HH",
      55,
      50
    );

    ctx.textAlign = "right";

    ctx.fillText(
      "GOA '26",
      width - 55,
      50
    );

    // -----------------------------
    // HH GOA LOGO
    // -----------------------------

    const logo =
      await loadImage(hhGoaLogo);

    const logoH = 56;

    const logoW =
      (logo.width / logo.height) *
      logoH;

    const logoX =
      (width - logoW) / 2;

    const logoY =
      Math.round(
        (50 - logoH / 2) - 4
      );

    ctx.drawImage(
      logo,
      logoX,
      logoY,
      logoW,
      logoH
    );

    // -----------------------------
    // DATE
    // -----------------------------

    ctx.fillStyle = "#FFD900";
    ctx.font = "bold 20px Arial";
    ctx.globalAlpha = 0.85;
    ctx.textAlign = "left";

    ctx.fillText(
      "GOA, INDIA · 28–31 OCT 2026",
      55,
      80
    );

    ctx.globalAlpha = 1;

    // -----------------------------
    // PHOTO
    // -----------------------------

    const photoX = 55;
    const photoY = 120;
    const photoWidth = width - 110;
    const photoHeight = photoWidth;

    drawCoverImage(
      ctx,
      image,
      photoX,
      photoY,
      photoWidth,
      photoHeight
    );

    // -----------------------------
    // INFORMATION
    // -----------------------------

    const infoY =
      photoY + photoHeight + 70;

    // NAME

    ctx.fillStyle = "#FFD900";
    ctx.font = "bold 68px Arial";
    ctx.textAlign = "left";

    const displayName = (
      name || "YOUR NAME"
    ).toUpperCase();

    ctx.fillText(
      displayName,
      55,
      infoY
    );

    // STACK

    ctx.font = "bold 26px Arial";
    ctx.fillStyle =
      "rgba(255,255,255,0.65)";

    ctx.fillText(
      (
        stack || "YOUR STACK / ROLE"
      ).toUpperCase(),
      55,
      infoY + 45
    );

    // BUILDER CLASS

    const classText =
      builderClass || "BUILDER CLASS";

    ctx.font = "bold 25px Arial";

    const classWidth =
      ctx.measureText(classText).width +
      40;

    ctx.fillStyle = "#F5007D";

    ctx.fillRect(
      55,
      infoY + 80,
      classWidth,
      52
    );

    ctx.fillStyle = "#f1eee5";

    ctx.fillText(
      classText,
      75,
      infoY + 115
    );

    // -----------------------------
    // FOOTER
    // -----------------------------

    ctx.fillStyle = "#FFD900";
    ctx.font = "bold 21px Arial";

    const footerY = height - 150;

    ctx.textAlign = "left";

    ctx.fillText(
      "LESS NOISE.",
      55,
      footerY
    );

    ctx.textAlign = "right";

    ctx.fillText(
      "MORE SIGNAL.",
      width - 55,
      footerY
    );

    ctx.textAlign = "left";

    // -----------------------------
    // RETURN PNG
    // -----------------------------

    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          resolve(blob);
        },
        "image/png"
      );
    });
  };

  // -----------------------------
  // DOWNLOAD
  // -----------------------------

  const generateCard = async () => {
    if (!imageBlob) return;

    try {
      const blob =
        await createCardBlob();

      if (!blob) {
        alert(
          "Couldn't generate the image."
        );
        return;
      }

      const url =
        URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = url;

      link.download =
        "HH-Goa-2026-Builder-ID.png";

      link.style.display = "none";

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 1000);
    } catch (error) {
      console.error(error);

      alert(
        "Couldn't generate the Builder ID."
      );
    }
  };

  // -----------------------------
  // SHARE TO X
  // -----------------------------

  const shareToX = async () => {
    if (!imageBlob || isSharing) return;

    try {
      setIsSharing(true);

      const blob =
        await createCardBlob();

      if (!blob) {
        throw new Error(
          "Couldn't generate card."
        );
      }

      // Convert PNG to base64 data URL

      const dataUrl =
        await new Promise(
          (resolve, reject) => {
            const reader =
              new FileReader();

            reader.onload = () =>
              resolve(reader.result);

            reader.onerror = reject;

            reader.readAsDataURL(blob);
          }
        );

      // Upload to Vercel API

      const response =
        await fetch(
          "/api/upload",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              image: dataUrl,
            }),
          }
        );

      if (!response.ok) {
        throw new Error(
          `Upload failed: ${response.status}`
        );
      }

      const data =
        await response.json();

      if (!data.url) {
        throw new Error(
          "No image URL returned."
        );
      }

      // -----------------------------
      // X CAPTION
      // -----------------------------

      const caption =
        "Just made my Builder ID. Looking forward to building, learning, and connecting at HH Goa 2026. Hoping to see you in Goa! #FrameInGoa";

      // -----------------------------
      // SHARE PAGE
      // -----------------------------

      const shareUrl =
        `${window.location.origin}/api/share` +
        `?image=${encodeURIComponent(
          data.url
        )}` +
        `&name=${encodeURIComponent(
          name ||
            "HH Goa 2026 Builder"
        )}`;

      // -----------------------------
      // OPEN X
      // -----------------------------

      const xUrl =
        "https://twitter.com/intent/tweet" +
        "?text=" +
        encodeURIComponent(
          caption
        ) +
        "&url=" +
        encodeURIComponent(
          shareUrl
        );

      window.open(
        xUrl,
        "_blank",
        "noopener,noreferrer"
      );
    } catch (error) {
      console.error(error);

      alert(
        "Couldn't prepare your Builder ID for X. Please try again."
      );
    } finally {
      setIsSharing(false);
    }
  };

  // -----------------------------
  // UI
  // -----------------------------

  return (
    <main className="app">

      <nav className="navbar">

        <div className="brand">
          HH GOA 2026
        </div>

        <div className="nav-label">
          BUILDER ID / 01
        </div>

      </nav>

      <section className="builder">

        {/* LEFT SIDE */}

        <div className="builder-copy">

          <p className="eyebrow">
            HACKER HOUSE GOA
          </p>

          <h1>
            Build your
            <br />
            <span>identity.</span>
          </h1>

          <p className="description">
            Your photo. Your stack. Your
            builder class. One HH Goa
            identity ready to share.
          </p>

          <div className="form">

            {/* NAME */}

            <label>
              NAME

              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) =>
                  setName(
                    e.target.value
                  )
                }
                maxLength={32}
              />
            </label>

            {/* STACK */}

            <label>
              STACK / ROLE

              <input
                type="text"
                placeholder="e.g. AI / Full Stack / Designer"
                value={stack}
                onChange={(e) =>
                  setStack(
                    e.target.value
                  )
                }
                maxLength={40}
              />
            </label>

            {/* UPLOAD */}

            <button
              type="button"
              className="upload-button"
              onClick={() =>
                fileInputRef.current?.click()
              }
            >
              {preview
                ? "Change Photo"
                : "Upload Photo"}
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept="
                image/png,
                image/jpeg,
                image/heic,
                image/heif
              "
              onChange={handleFile}
              hidden
            />

            <p className="formats">
              JPG · PNG · HEIC
            </p>

            {/* DOWNLOAD + SHARE */}

            {preview && (
              <>
                <button
                  type="button"
                  className="download-button"
                  onClick={generateCard}
                >
                  DOWNLOAD BUILDER ID
                </button>

                <button
                  type="button"
                  className="share-button"
                  onClick={shareToX}
                  disabled={isSharing}
                >
                  {isSharing
                    ? "PREPARING..."
                    : "SHARE TO X"}
                </button>
              </>
            )}

          </div>

        </div>

        {/* RIGHT SIDE */}

        <div className="card-area">

          <div className="builder-card">

            {/* CARD HEADER */}

            <div className="card-top">

              <div className="card-top-row">

                <span>
                  HH
                </span>

                <img
                  src={hhGoaLogo}
                  alt="Hacker House Goa"
                  className="card-top-logo"
                />

                <span>
                  GOA '26
                </span>

              </div>

              <div className="card-top-date">
                GOA, INDIA · 28–31 OCT 2026
              </div>

            </div>

            {/* PHOTO */}

            <div className="photo-container">

              {preview ? (

                <img
                  src={preview}
                  alt="Builder"
                />

              ) : (

                <div className="photo-placeholder">

                  <span>
                    UPLOAD
                  </span>

                  <strong>
                    PHOTO
                  </strong>

                </div>

              )}

            </div>

            {/* CARD INFORMATION */}

            <div className="card-info">

              <div className="builder-name">
                {name ||
                  "YOUR NAME"}
              </div>

              <div className="builder-stack">
                {stack ||
                  "YOUR STACK / ROLE"}
              </div>

              <div className="builder-class">
                {builderClass ||
                  "BUILDER CLASS"}
              </div>

            </div>

            {/* CARD FOOTER */}

            <div className="card-bottom">

              <span>
                LESS NOISE.
              </span>

              <span>
                MORE SIGNAL.
              </span>

            </div>

          </div>

        </div>

      </section>

    </main>
  );
}

export default App;