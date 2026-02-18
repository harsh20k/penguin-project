import { Component, type ReactNode, StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) {
    return { error }
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: '2rem', fontFamily: 'system-ui', maxWidth: '480px', margin: '0 auto' }}>
          <h1 style={{ color: '#b91c1c', marginTop: 0 }}>Something went wrong</h1>
          <pre style={{ background: '#fef2f2', padding: '1rem', borderRadius: '8px', overflow: 'auto' }}>
            {this.state.error.message}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}

const root = document.getElementById('root')
if (!root) throw new Error('Root element #root not found')
createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
