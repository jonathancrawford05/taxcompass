import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="z-10 max-w-5xl w-full items-center justify-center">
        <h1 className="text-5xl md:text-6xl font-bold text-center mb-4">
          TaxCompass 🧭
        </h1>
        <p className="text-xl md:text-2xl text-center mb-6">
          AI-Powered Cross-Border Tax Analysis
        </p>
        <p className="text-center text-muted-foreground mb-12 text-base md:text-lg max-w-2xl mx-auto">
          Smart tax residency analysis and optimization for international professionals
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-16">
          <Link
            href="/analysis"
            className="inline-flex items-center justify-center rounded-md bg-primary px-8 py-4 text-lg font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Start Analysis
          </Link>
          <a
            href="http://localhost:8000/api/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-8 py-4 text-lg font-semibold hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            API Docs
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center mb-12">
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-2">🤖</div>
            <h3 className="font-bold text-xl mb-2">AI-Powered</h3>
            <p className="text-sm text-muted-foreground">
              LangGraph agents analyze your situation using real CRA tax law
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-2">🔒</div>
            <h3 className="font-bold text-xl mb-2">Privacy First</h3>
            <p className="text-sm text-muted-foreground">
              Local Ollama LLM processing with no data sent to external APIs
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <div className="text-3xl mb-2">📖</div>
            <h3 className="font-bold text-xl mb-2">Open Source</h3>
            <p className="text-sm text-muted-foreground">
              AGPL-3.0 licensed - audit the code and self-host
            </p>
          </div>
        </div>

        <div className="text-center text-sm text-muted-foreground border-t pt-6">
          <p className="font-semibold mb-1">⚠️ Disclaimer</p>
          <p>This is an analysis tool, not professional tax advice.</p>
          <p>Always consult a qualified tax professional for your specific situation.</p>
        </div>
      </div>
    </main>
  )
}
