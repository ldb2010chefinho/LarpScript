/*
  Service worker do LarpStudios: um ajudante que fica entre a página e a internet.
  1) Guarda tudo em cache: depois da primeira visita o LarpStudios abre até sem internet (app/PWA).
  2) Acrescenta dois cabeçalhos de segurança (COOP e COEP) nas respostas do próprio site.
     Com eles o navegador libera o SharedArrayBuffer, e o input() pode PARAR e esperar você digitar.
     (O GitHub Pages não deixa configurar esses cabeçalhos, então o service worker faz isso.)
*/
const CACHE = "larpstudios-v1";
const BASE = ["./", "./index.html", "./manifest.json", "./logo.svg", "./icone-192.png", "./icone-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(BASE)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const nome of await caches.keys()) if (nome !== CACHE) await caches.delete(nome);
    await self.clients.claim();
  })());
});

function comCabecalhos(resposta) {
  if (!resposta || resposta.status === 0 || resposta.type === "opaque") return resposta;
  const h = new Headers(resposta.headers);
  h.set("Cross-Origin-Opener-Policy", "same-origin");
  h.set("Cross-Origin-Embedder-Policy", "credentialless");
  return new Response(resposta.body, { status: resposta.status, statusText: resposta.statusText, headers: h });
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  if (req.cache === "only-if-cached" && req.mode !== "same-origin") return;
  const url = new URL(req.url);

  if (url.origin === self.location.origin) {
    // o próprio site: tenta a internet primeiro (para pegar a versão nova); sem internet, usa o cache
    e.respondWith((async () => {
      try {
        const r = await fetch(req);
        if (r.ok) (await caches.open(CACHE)).put(req, r.clone());
        return comCabecalhos(r);
      } catch (erro) {
        const guardada = await caches.match(req, { ignoreSearch: true }) || await caches.match("./index.html");
        return comCabecalhos(guardada);
      }
    })());
    return;
  }

  if (/^(cdn\.jsdelivr\.net|fonts\.googleapis\.com|fonts\.gstatic\.com)$/.test(url.hostname)) {
    // editor, Python (Pyodide) e fontes: versões fixas, então o cache vale para sempre
    e.respondWith((async () => {
      const guardada = await caches.match(req);
      if (guardada) return guardada;
      const r = await fetch(req);
      if (r.ok || r.type === "opaque") (await caches.open(CACHE)).put(req, r.clone());
      return r;
    })());
  }
});
