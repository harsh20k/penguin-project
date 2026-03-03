import { type FormEvent, useEffect, useState } from 'react';
import { type Factor3ChallengeResponse, getFactor3Challenge, verifyFactor3 } from '../api/client';
import { StepLayout } from './StepLayout';

export function Factor3Challenge({ token, onBackToLogin, onSuccess }: Factor3ChallengeProps) {
  const [challenge, setChallenge] = useState<Factor3ChallengeResponse | null>(null);
  const [ciphertext, setCiphertext] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getFactor3Challenge(token)
      .then((res) => {
        if (!cancelled) {
          setChallenge(res);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load challenge';
          setError(message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await verifyFactor3(token, ciphertext);
      if (res.authenticated) {
        onSuccess();
      } else {
        setError('Invalid ciphertext');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Verification failed';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  }

  const footer = (
    <div className="footer-actions">
      <button type="button" className="button ghost" onClick={onBackToLogin}>
        Back to login
      </button>
    </div>
  );

  return (
    <StepLayout
      title="Step 3: Caesar challenge"
      subtitle="Encode the plaintext using the given rotation, then submit the ciphertext."
      footer={footer}
    >
      {loading ? (
        <p className="muted">Loading challenge…</p>
      ) : error && !challenge ? (
        <p className="error-text">{error}</p>
      ) : (
        <>
          <div className="challenge-summary">
            <div>
              <span className="field-label">Plaintext</span>
              <code className="code-pill">{challenge?.plaintext}</code>
            </div>
          </div>
          <form className="form" onSubmit={handleSubmit}>
            <label className="field">
              <span className="field-label">Ciphertext</span>
              <input
                className="input"
                type="text"
                value={ciphertext}
                onChange={(e) => setCiphertext(e.target.value)}
                required
              />
            </label>
            <button className="button primary" type="submit" disabled={submitting}>
              {submitting ? 'Verifying…' : 'Verify'}
            </button>
            {error && <p className="error-text">{error}</p>}
          </form>
        </>
      )}
    </StepLayout>
  );
}

