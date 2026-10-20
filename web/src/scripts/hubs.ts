// Scripts for the evergreen hubs (one bundle for the route; each part runs only where its markup is).
import './calc';

const pairEl = document.getElementById('pair-data');
if (pairEl) {
  const P: Record<string, string> = JSON.parse(pairEl.textContent || '{}');
  document.getElementById('pairForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const a = +(document.getElementById('pa') as HTMLSelectElement).value;
    const b = +(document.getElementById('pb') as HTMLSelectElement).value;
    const href = P[`${Math.min(a, b)}-${Math.max(a, b)}`];
    if (href) location.href = href;
  });
}
