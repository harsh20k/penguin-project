import { type FormEvent, useState } from 'react';
import { login, signup } from '../api/client';
import { StepLayout } from './StepLayout';

type LoginFormProps = {
  onLoginSuccess: (args: { sessionId: string; token: string }) => void;
};

export function LoginForm({ onLoginSuccess }: LoginFormProps) {
  const [username, setUsername] = useState('dev@local');
  const [password, setPassword] = useState('devpass');
  const [loading, setLoading] = useState(false);
  const [signingUp, setSigningUp] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await login(username, password);
      onLoginSuccess({ sessionId: res.session_id, token: res.token });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSignup(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSigningUp(true);
    try {
      await signup({
        email: username,
        password,
        role: 'client',
        question: 'What is your favorite color?',
        answer: 'blue',
        rotation: 7,
      });
      const res = await login(username, password);
      onLoginSuccess({ sessionId: res.session_id, token: res.token });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Signup failed';
      setError(message);
    } finally {
      setSigningUp(false);
    }
  }

  return (
    <StepLayout
      title="Step 1: Login"
      subtitle="Use the dev credentials to start a session."
      footer={
        <p className="helper-text">
          Default creds: <code>dev@local</code> / <code>devpass</code>
        </p>
      }
    >
      <form className="form" onSubmit={handleSubmit}>
        <label className="field">
          <span className="field-label">Email</span>
          <input
            className="input"
            type="email"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>
        <label className="field">
          <span className="field-label">Password</span>
          <input
            className="input"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error-text">{error}</p>}
        <div className="footer-actions">
          <button className="button primary" type="submit" disabled={loading || signingUp}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
          <button
            className="button secondary"
            type="button"
            onClick={handleSignup}
            disabled={loading || signingUp}
          >
            {signingUp ? 'Signing up…' : 'Sign up'}
          </button>
        </div>
      </form>
    </StepLayout>
  );
}

