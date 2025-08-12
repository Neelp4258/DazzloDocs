const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class UltimateHTMLToPDFConverter {
    constructor(options = {}) {
        this.browser = null;
        this.defaultOptions = {
            format: 'A4',
            margin: {
                top: '12mm',
                right: '10mm',
                bottom: '14mm',
                left: '10mm'
            },
            printBackground: true,
            preferCSSPageSize: true,
            displayHeaderFooter: false,
            scale: 1.0,
            landscape: false,
            ...options
        };
    }

    async initialize() {
        if (this.browser) return;

        this.browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        });

        // Set default viewport
        const page = await this.browser.newPage();
        await page.setViewport({ width: 1200, height: 800 });

        // Inject print-specific CSS rules
        await page.evaluateOnNewDocument(() => {
            const style = document.createElement('style');
            style.textContent = `
                @media print {
                    * {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                    img, table, h1, h2, h3, h4, h5, h6, ul, ol, p {
                        page-break-inside: avoid;
                    }
                    h1, h2, h3, h4, h5, h6 {
                        page-break-after: avoid;
                    }
                }
            `;
            document.head.appendChild(style);
        });

        await page.close();
    }

    wrapWithLetterhead(htmlContent, baseDir, letterheadType = 'trivanta') {
        // Extract head and body content
        const headMatch = htmlContent.match(/<head[\s\S]*?>([\s\S]*?)<\/head>/i);
        const bodyMatch = htmlContent.match(/<body[\s\S]*?>([\s\S]*?)<\/body>/i);
        
        const innerHead = headMatch ? headMatch[1] : '';
        const innerBody = bodyMatch ? bodyMatch[1] : htmlContent;

        let letterheadCSS, headerHTML, footerHTML;

        if (letterheadType === 'dazzlo') {
            // Dazzlo Letterhead CSS
            letterheadCSS = `
                @page {
                    size: A4;
                    margin: 12mm 10mm 14mm 10mm;
                }
                html, body {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                body {
                    margin: 0 !important;
                    padding-top: 32mm !important;
                    padding-bottom: 16mm !important;
                    background: #ffffff !important;
                }
                * {
                    box-sizing: border-box;
                }
                .pdf-header, .pdf-header *, .pdf-header table, .pdf-header td, .pdf-header tr, .pdf-header img {
                    border: none !important;
                    outline: none !important;
                    box-shadow: none !important;
                    background: transparent !important;
                }
                .pdf-header {
                    position: fixed !important;
                    top: 0 !important; 
                    left: 0 !important; 
                    right: 0 !important;
                    height: 28mm !important;
                    box-sizing: border-box !important;
                    padding: 15px 25px !important;
                    border-bottom: 3px solid #d4af37 !important;
                    background: #ffffff !important;
                    font-family: 'Times New Roman', serif !important;
                    z-index: 1000 !important;
                    overflow: hidden !important;
                }
                .pdf-header table {
                    width: 100% !important;
                    border-collapse: collapse !important;
                    border: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border-spacing: 0 !important;
                    background: transparent !important;
                }
                .pdf-header td {
                    border: none !important;
                    outline: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    background: transparent !important;
                    vertical-align: bottom !important;
                }
                .pdf-header .company-name {
                    font-size: 24px !important; 
                    font-weight: bold !important; 
                    color: #333 !important;
                    margin-bottom: 6px !important;
                    line-height: 1.2 !important;
                }
                .pdf-header .tagline {
                    font-size: 13px !important; 
                    font-style: italic !important; 
                    color: #666 !important;
                    line-height: 1.2 !important;
                }
                .pdf-header .contact-info {
                    font-size: 12px !important; 
                    font-weight: bold !important; 
                    line-height: 1.4 !important; 
                    color: #333 !important;
                    text-align: right !important;
                }
                .pdf-header img {
                    width: 60px !important;
                    height: 60px !important;
                    border: none !important;
                    outline: none !important;
                    display: block !important;
                }
                .pdf-footer {
                    position: fixed !important;
                    bottom: 0 !important; 
                    left: 0 !important; 
                    right: 0 !important;
                    height: 12mm !important;
                    box-sizing: border-box !important;
                    border-top: 1px solid #ddd !important;
                    text-align: center !important;
                    padding: 8px 0 !important;
                    font: italic 10px 'Times New Roman', serif !important;
                    color: #666 !important;
                    background: #ffffff !important;
                    z-index: 1000 !important;
                }
            `;

            // Dazzlo Letterhead HTML
            headerHTML = `
                <div class="pdf-header">
                    <table>
                        <tr>
                            <td style="width: 60px;">
                                <img src="logo.png">
                            </td>
                            <td style="padding-left: 25px;">
                                <div class="company-name">Dazzlo Enterprises Pvt Ltd</div>
                                <div class="tagline">Redefining lifestyle with Innovations and Dreams</div>
                            </td>
                            <td class="contact-info">
                                Tel: +91 9373015503<br>
                                Email: info@dazzlo.co.in<br>
                                Address: Kalyan, Maharashtra 421301
                            </td>
                        </tr>
                    </table>
                </div>
            `;

            footerHTML = `
                <div class="pdf-footer">
                    info@dazzlo.co.in | www.dazzlo.co.in
                </div>
            `;
        } else {
            // Trivanta Letterhead CSS (default)
            letterheadCSS = `
                @page {
                    size: A4;
                    margin: 12mm 10mm 14mm 10mm;
                }
                html, body {
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                body {
                    margin: 0 !important;
                    padding-top: 32mm !important;
                    padding-bottom: 16mm !important;
                    background: #ffffff !important;
                }
                * {
                    box-sizing: border-box;
                }
                .pdf-header, .pdf-header *, .pdf-header table, .pdf-header td, .pdf-header tr, .pdf-header img {
                    border: none !important;
                    outline: none !important;
                    box-shadow: none !important;
                    background: transparent !important;
                }
                .pdf-header {
                    position: fixed !important;
                    top: 0 !important; 
                    left: 0 !important; 
                    right: 0 !important;
                    height: 28mm !important;
                    box-sizing: border-box !important;
                    padding: 10px 20px !important;
                    border-bottom: 3px solid #2c5282 !important;
                    background: #ffffff !important;
                    font-family: 'Times New Roman', serif !important;
                    z-index: 1000 !important;
                    overflow: hidden !important;
                }
                .pdf-header table {
                    width: 100% !important;
                    border-collapse: collapse !important;
                    border: none !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border-spacing: 0 !important;
                    background: transparent !important;
                }
                .pdf-header td {
                    border: none !important;
                    outline: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    background: transparent !important;
                    vertical-align: bottom !important;
                }
                .pdf-header .company-name {
                    font-size: 22px !important; 
                    font-weight: bold !important; 
                    color: #1a365d !important;
                    margin-bottom: 5px !important;
                    line-height: 1.2 !important;
                }
                .pdf-header .tagline {
                    font-size: 11px !important; 
                    font-style: italic !important; 
                    color: #2c5282 !important;
                    line-height: 1.2 !important;
                }
                .pdf-header .contact-info {
                    font-size: 10px !important; 
                    font-weight: bold !important; 
                    line-height: 1.4 !important; 
                    color: #1a365d !important;
                    text-align: right !important;
                }
                .pdf-header img {
                    width: 60px !important;
                    height: 60px !important;
                    border: none !important;
                    outline: none !important;
                    display: block !important;
                }
                .pdf-footer {
                    position: fixed !important;
                    bottom: 0 !important; 
                    left: 0 !important; 
                    right: 0 !important;
                    height: 12mm !important;
                    box-sizing: border-box !important;
                    border-top: 1px solid #ddd !important;
                    text-align: center !important;
                    padding: 8px 0 !important;
                    font: italic 10px 'Times New Roman', serif !important;
                    color: #666 !important;
                    background: #ffffff !important;
                    z-index: 1000 !important;
                }
                .pdf-footer .website { 
                    font-weight: bold !important; 
                    color: #1a365d !important; 
                }
            `;

            // Trivanta Letterhead HTML
            headerHTML = `
                <div class="pdf-header">
                    <table>
                        <tr>
                            <td style="width: 60px;">
                                <img src="trivanta.png">
                            </td>
                            <td style="padding-left: 20px;">
                                <div class="company-name">Trivanta Edge</div>
                                <div class="tagline">From Land to Legacy — with Edge</div>
                            </td>
                            <td class="contact-info">
                                sales@trivantaedge.com<br>
                                info@trivantaedge.com<br>
                                +91 9373015503<br>
                                Kalyan, Maharashtra
                            </td>
                        </tr>
                    </table>
                </div>
            `;

            footerHTML = `
                <div class="pdf-footer">
                    © 2025 Trivanta Edge. All rights reserved. | <span class="website">www.trivantaedge.com</span>
                </div>
            `;
        }

        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <base href="file:///${baseDir.replace(/\\/g, '/')}/">
    ${innerHead}
    <style>${letterheadCSS}</style>
</head>
<body>
    ${headerHTML}
    ${footerHTML}
    ${innerBody}
</body>
</html>`;
    }

    async convertHTMLToPDF(htmlContent, outputPath, customOptions = {}) {
        if (!this.browser) {
            throw new Error('Converter not initialized. Call initialize() first.');
        }

        const options = { ...this.defaultOptions, ...customOptions };
        const tempHtmlPath = path.join(__dirname, '..', 'temp', `temp_${uuidv4()}.html`);
        
        try {
            // Ensure temp directory exists
            await fs.ensureDir(path.dirname(tempHtmlPath));

            // Enhance HTML with print-friendly CSS
            let enhancedHTML = this.enhanceHTML(htmlContent);

            // Add letterhead if requested
            if (options.letterhead) {
                const baseDir = path.dirname(tempHtmlPath);
                enhancedHTML = this.wrapWithLetterhead(enhancedHTML, baseDir, options.letterheadType || 'trivanta');
            }

            // Write enhanced HTML to temporary file
            await fs.writeFile(tempHtmlPath, enhancedHTML, 'utf8');

            const page = await this.browser.newPage();
            
            // Navigate to the temporary HTML file
            await page.goto(`file://${tempHtmlPath}`, { 
                waitUntil: ['networkidle0', 'domcontentloaded'] 
            });

            // Wait for images to load
            await page.evaluate(() => {
                return Promise.all(
                    Array.from(document.images)
                        .filter(img => !img.complete)
                        .map(img => new Promise(resolve => {
                            img.onload = img.onerror = resolve;
                        }))
                );
            });

            // Generate PDF
            const pdfBuffer = await page.pdf({
                format: options.format,
                margin: options.margin,
                printBackground: options.printBackground,
                preferCSSPageSize: options.preferCSSPageSize,
                displayHeaderFooter: options.displayHeaderFooter,
                scale: options.scale,
                landscape: options.landscape
            });

            await page.close();

            // Write PDF to output path
            await fs.writeFile(outputPath, pdfBuffer);

            return {
                success: true,
                outputPath,
                fileSize: pdfBuffer.length,
                pageCount: await this.getPageCount(outputPath)
            };

        } catch (error) {
            throw new Error(`PDF conversion failed: ${error.message}`);
        } finally {
            // Clean up temporary file
            try {
                await fs.remove(tempHtmlPath);
            } catch (cleanupError) {
                console.warn('Warning: Could not clean up temporary file:', cleanupError.message);
            }
        }
    }

    enhanceHTML(htmlContent) {
        const printCSS = `
            <style>
                /* Print-friendly enhancements */
                * {
                    box-sizing: border-box;
                }
                
                body {
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                
                /* Prevent overlapping */
                div, p, h1, h2, h3, h4, h5, h6 {
                    margin: 0;
                    padding: 0;
                    page-break-inside: avoid;
                }
                
                /* Table improvements */
                table {
                    border-collapse: collapse;
                    width: 100%;
                    page-break-inside: avoid;
                }
                
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                
                /* Image handling */
                img {
                    max-width: 100%;
                    height: auto;
                    page-break-inside: avoid;
                }
                
                /* List improvements */
                ul, ol {
                    page-break-inside: avoid;
                }
                
                li {
                    page-break-inside: avoid;
                }
                
                /* Code blocks */
                pre, code {
                    page-break-inside: avoid;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                
                /* Print-specific rules */
                @media print {
                    * {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }
                    
                    body {
                        margin: 0;
                        padding: 0;
                    }
                    
                    /* Page break controls */
                    h1, h2, h3, h4, h5, h6 {
                        page-break-after: avoid;
                    }
                    
                    img, table, pre, code {
                        page-break-inside: avoid;
                    }
                    
                    /* Orphans and widows control */
                    p {
                        orphans: 3;
                        widows: 3;
                    }
                }
            </style>
        `;

        // Insert the CSS into the HTML head
        if (htmlContent.includes('</head>')) {
            return htmlContent.replace('</head>', `${printCSS}</head>`);
        } else {
            return `<html><head>${printCSS}</head><body>${htmlContent}</body></html>`;
        }
    }

    async getPageCount(pdfPath) {
        try {
            const fs = require('fs');
            const buffer = fs.readFileSync(pdfPath);
            const match = buffer.toString().match(/\/Count\s+(\d+)/);
            return match ? parseInt(match[1]) : 1;
        } catch (error) {
            return 1; // Default to 1 page if we can't determine
        }
    }

    async convertFile(inputPath, outputPath, options = {}) {
        const htmlContent = await fs.readFile(inputPath, 'utf8');
        return this.convertHTMLToPDF(htmlContent, outputPath, options);
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            this.browser = null;
        }
    }
}

module.exports = UltimateHTMLToPDFConverter;
