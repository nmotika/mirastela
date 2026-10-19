/** Minimal, safe Markdown → HTML for model output: ## / ### headings, paragraphs, lists, **bold**, *italic*. */
function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
function inline(s: string): string {
  return esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*?)\*/g, '$1<em>$2</em>');
}
/** basisLabel: '> ' lines (the astrological basis in report format v2) become a collapsed details box. */
export function mdToHtml(md: string, basisLabel = ''): string {
  const out: string[] = [];
  let para: string[] = [];
  let list: string[] | null = null;
  let quote: string[] = [];
  const flush = () => {
    if (para.length) { out.push(`<p>${inline(para.join(' '))}</p>`); para = []; }
    if (list) { out.push(`<ul>${list.map((li) => `<li>${inline(li)}</li>`).join('')}</ul>`); list = null; }
    if (quote.length) {
      const body = `<p>${inline(quote.join(' '))}</p>`;
      out.push(basisLabel ? `<details class="basis"><summary>${esc(basisLabel)}</summary>${body}</details>` : `<blockquote>${body}</blockquote>`);
      quote = [];
    }
  };
  for (const raw of md.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) { flush(); continue; }
    const q = /^>\s?(.*)$/.exec(line);
    if (q) { if (para.length || list) flush(); quote.push(q[1]); continue; }
    if (quote.length) flush();
    const h = /^(#{1,4})\s+(.*)$/.exec(line);
    if (h) {
      flush();
      const level = Math.min(Math.max(h[1].length, 2), 3);
      out.push(`<h${level}>${inline(h[2])}</h${level}>`);
      continue;
    }
    const li = /^[-*]\s+(.*)$/.exec(line);
    if (li) {
      if (para.length) { out.push(`<p>${inline(para.join(' '))}</p>`); para = []; }
      (list ??= []).push(li[1]);
      continue;
    }
    if (list) flush();
    para.push(line);
  }
  flush();
  return out.join('\n');
}
