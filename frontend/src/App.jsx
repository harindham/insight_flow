export default function App() {
  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">insightFlow</p>
        <h1>Analytics that move as fast as your ideas.</h1>
        <p className="subhead">
          Your React + FastAPI starter is ready. Hook this UI to the API and
          start shipping insights.
        </p>
        <div className="cta-row">
          <button type="button">Explore</button>
          <a className="secondary" href="/health" onClick={(event) => event.preventDefault()}>
            API health
          </a>
        </div>
      </header>
      <section className="card-grid">
        <article>
          <h2>Frontend</h2>
          <p>Vite + React setup in minutes with a clean starter layout.</p>
        </article>
        <article>
          <h2>Backend</h2>
          <p>FastAPI with CORS enabled for your local dev loop.</p>
        </article>
        <article>
          <h2>Next Step</h2>
          <p>Wire up real endpoints and visualizations for your data.</p>
        </article>
      </section>
    </div>
  );
}
