export const dynamic = "force-dynamic";

type Health = { status: string; db?: string; redis?: string; workers?: number };

async function apiHealth(): Promise<Health> {
  try {
    const res = await fetch(`${process.env.API_URL}/health`, { cache: "no-store" });
    return await res.json();
  } catch {
    return { status: "unreachable" };
  }
}

export default async function Home() {
  const h = await apiHealth();
  return (
    <main>
      <h1>Video Studio</h1>
      <p>
        API: <b id="api-status">{h.status}</b> · db {h.db ?? "?"} · redis {h.redis ?? "?"} · workers {h.workers ?? "?"}
      </p>
    </main>
  );
}
