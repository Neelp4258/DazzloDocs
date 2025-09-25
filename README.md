# HTML → PDF Converter (Client-side)

A lightweight, zero-backend HTML to PDF converter that runs entirely in the browser using html2pdf.js (html2canvas + jsPDF). Supports portrait/landscape orientation, multiple page sizes, margins, scaling, and a live preview.

## Quick start

Open `index.html` in any modern browser.

- Enter or paste HTML in the textarea
- Choose orientation, page size, margins, and scaling
- Click Preview to see the result
- Click Download PDF to save the file

## Notes

- Orientation and `format` (page size) are provided to jsPDF through html2pdf.js options.
- Complex CSS is rasterized by html2canvas. For best vector text results, prefer system fonts.
- Large pages: use pagebreak CSS classes or the `pagebreak` option. This UI enables `css` and `legacy` automatically.

## Tech

- html2pdf.js via CDN
- No build step required

## License

MIT

