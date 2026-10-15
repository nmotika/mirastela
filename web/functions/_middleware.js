// Send *.pages.dev traffic to the canonical domain, which sits behind Cloudflare Access.
export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname.endsWith('.pages.dev')) {
    url.hostname = 'mirastela.com';
    url.port = '';
    return Response.redirect(url.toString(), 301);
  }
  return next();
}
