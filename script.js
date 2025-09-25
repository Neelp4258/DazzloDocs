const $ = (id) => document.getElementById(id);

function updateScaleLabel() {
  const scale = parseFloat($("scale").value);
  $("scaleValue").textContent = `${scale.toFixed(2)}x`;
}

function buildPreviewHtml(html) {
  const styles = `
    <style>
      html, body { margin: 0; padding: 0; }
      body { font-family: -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial; line-height: 1.5; }
      .page { padding: 16px; }
    </style>
  `;
  return `<!doctype html><html><head><meta charset="utf-8">${styles}</head><body><div class="page">${html}</div></body></html>`;
}

function setPreviewContent(htmlString) {
  const iframe = $("previewFrame");
  const doc = iframe.contentDocument || iframe.contentWindow.document;
  doc.open();
  doc.write(buildPreviewHtml(htmlString));
  doc.close();
}

function sampleHtml() {
  return `
  <div style="display:flex; align-items:center; gap:16px;">
    <div>
      <h1>HTML to PDF Demo</h1>
      <p>This is a sample document to demonstrate <b>portrait</b> and <b>landscape</b> PDF generation with different page sizes and margins.</p>
      <ul>
        <li>High-quality rendering using html2canvas</li>
        <li>Vector text PDF using jsPDF</li>
        <li>Custom margins and scaling</li>
      </ul>
      <p>Try switching orientation to <i>landscape</i> and page size to <i>Letter</i>.</p>
    </div>
  </div>
  <table style="width:100%; border-collapse:collapse; margin-top:20px;">
    <thead>
      <tr>
        <th style="border:1px solid #ccc; padding:8px; text-align:left;">Item</th>
        <th style="border:1px solid #ccc; padding:8px; text-align:right;">Qty</th>
        <th style="border:1px solid #ccc; padding:8px; text-align:right;">Price</th>
      </tr>
    </thead>
    <tbody>
      ${Array.from({length: 20}, (_, i) => `<tr><td style="border:1px solid #eee; padding:8px;">Product ${i+1}</td><td style="border:1px solid #eee; padding:8px; text-align:right;">${(i%5)+1}</td><td style="border:1px solid #eee; padding:8px; text-align:right;">$${((i%7)+1)*9}.00</td></tr>`).join("")}
    </tbody>
  </table>
  <p style="margin-top:24px;">Page footer example — generated on ${new Date().toLocaleString()}.</p>
  `;
}

async function generatePdf() {
  const filename = $("filename").value.trim() || "document.pdf";
  const orientation = $("orientation").value; // 'portrait' | 'landscape'
  const pageSize = $("pageSize").value; // e.g., 'a4'
  const margin = $("margin").value; // e.g., '0.5in'
  const scale = parseFloat($("scale").value);
  const htmlContent = $("htmlInput").value || sampleHtml();

  // Build a hidden container for rendering to canvas for best fidelity
  const tempContainer = document.createElement("div");
  tempContainer.style.position = "fixed";
  tempContainer.style.left = "-10000px";
  tempContainer.style.top = "0";
  tempContainer.style.width = "800px"; // neutral width; html2canvas will scale per options
  tempContainer.innerHTML = htmlContent;
  document.body.appendChild(tempContainer);

  const opt = {
    margin: margin,
    filename: filename,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: {
      scale: Math.max(1, Math.min(3, scale * 2)),
      useCORS: true,
      letterRendering: true,
      logging: false
    },
    jsPDF: {
      unit: "in",
      format: pageSize,
      orientation: orientation
    },
    pagebreak: { mode: ["css", "legacy"], avoid: [".no-break"] }
  };

  await html2pdf().set(opt).from(tempContainer).save();
  tempContainer.remove();
}

function init() {
  updateScaleLabel();
  $("scale").addEventListener("input", updateScaleLabel);

  $("loadSample").addEventListener("click", () => {
    const html = sampleHtml();
    $("htmlInput").value = html;
    setPreviewContent(html);
  });

  $("previewBtn").addEventListener("click", () => {
    const html = $("htmlInput").value || sampleHtml();
    setPreviewContent(html);
  });

  $("downloadBtn").addEventListener("click", () => {
    generatePdf().catch(err => {
      console.error(err);
      alert("Failed to generate PDF. See console for details.");
    });
  });

  // Load initial sample and preview
  const initial = sampleHtml();
  $("htmlInput").value = initial;
  setPreviewContent(initial);
}

document.addEventListener("DOMContentLoaded", init);

