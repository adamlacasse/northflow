// Cloudflare Worker: instant loading shell in front of a Railway origin.
//
// Behavior:
//   - Navigation requests (GET + Accept: text/html) try the origin with a short
//     timeout. If it responds in time, we proxy. If it doesn't, we return the
//     inlined loading page. The aborted subrequest still reaches Railway, which
//     kicks off the cold-start wake.
//   - /__status is polled by the loading page. It calls the origin's health
//     endpoint and reports ready/not-ready.
//   - All other requests (assets, API, XHR) proxy straight through. By the time
//     they fire, Railway is already warming from the initial subrequest.

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origin = env.ORIGIN_URL;               // e.g. https://your-app.up.railway.app
    const healthPath = env.HEALTH_PATH || "/health";
    const coldTimeout = Number(env.COLD_TIMEOUT_MS || 2500);

    if (url.pathname === "/__status") {
      try {
        const res = await fetch(origin + healthPath, {
          signal: AbortSignal.timeout(4000),
          cf: { cacheTtl: 0 },
        });
        return json({ ready: res.ok }, { status: res.ok ? 200 : 503 });
      } catch {
        return json({ ready: false }, { status: 503 });
      }
    }

    const isNav =
      request.method === "GET" &&
      (request.headers.get("Accept") || "").includes("text/html");

    if (isNav) {
      try {
        const upstream = await fetchWithTimeout(request, origin, coldTimeout);
        // Anything other than a connect/timeout failure is the real app's job
        // to render — even a 500 page is more informative than our shell.
        if (upstream) return upstream;
      } catch {
        // fall through to loading shell
      }
      return new Response(LOADING_HTML, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store",
        },
      });
    }

    return proxy(request, origin);
  },
};

async function fetchWithTimeout(request, origin, timeoutMs) {
  const url = new URL(request.url);
  return fetch(origin + url.pathname + url.search, {
    method: request.method,
    headers: forwardedHeaders(request),
    redirect: "manual",
    signal: AbortSignal.timeout(timeoutMs),
  });
}

function proxy(request, origin) {
  const url = new URL(request.url);
  return fetch(origin + url.pathname + url.search, {
    method: request.method,
    headers: forwardedHeaders(request),
    body: request.body,
    redirect: "manual",
  });
}

// Tell the origin what hostname the browser actually used, so Flask's
// ProxyFix can rebuild absolute URLs (OAuth callbacks, url_for(_external=True))
// against the public domain instead of the Railway backend hostname.
function forwardedHeaders(request) {
  const url = new URL(request.url);
  const h = new Headers(request.headers);
  h.set("X-Forwarded-Host", url.host);
  h.set("X-Forwarded-Proto", url.protocol.replace(":", ""));
  return h;
}

function json(data, init = {}) {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
      ...(init.headers || {}),
    },
  });
}

const LOADING_HTML = `
  <!doctype html>
  <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width,initial-scale=1" />
      <title>Starting up…</title>
      <style>
        html,
        body {
          height: 100%;
          margin: 0;
          font-family:
            -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
          background: #0b0c0e;
          color: #e8eaed;
        }
        .wrap {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 20px;
          padding: 24px;
          text-align: center;
        }
        .spinner {
          width: 36px;
          height: 36px;
          border: 3px solid rgba(255, 255, 255, 0.15);
          border-top-color: #7c9cff;
          border-radius: 50%;
          animation: spin 0.9s linear infinite;
        }
        .title {
          font-size: 18px;
          font-weight: 600;
        }
        .sub {
          font-size: 14px;
          opacity: 0.7;
          max-width: 32ch;
          line-height: 1.5;
        }
        .elapsed {
          font-size: 12px;
          opacity: 0.4;
          font-variant-numeric: tabular-nums;
        }
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="spinner" aria-hidden="true"></div>
        <div class="title">Waking up NorthFlow…</div>
        <div class="sub">
          This takes about 30–60 seconds the first time. It'll be instant after
          that.
        </div>
        <div class="sub">
          Namaste
        </div>
        <div class="elapsed" id="elapsed"></div>
      </div>
      <script>
        const start = Date.now();
        const el = document.getElementById("elapsed");
        const tick = () => {
          el.textContent = Math.floor((Date.now() - start) / 1000) + "s";
        };
        tick();
        setInterval(tick, 250);

        async function poll() {
          try {
            const r = await fetch("/__status", { cache: "no-store" });
            if (r.ok) {
              location.reload();
              return;
            }
          } catch {}
          setTimeout(poll, 1500);
        }
        setTimeout(poll, 800);
      </script>
    </body>
  </html>
`;
