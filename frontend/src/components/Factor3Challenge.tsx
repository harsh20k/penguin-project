import { type FormEvent, useEffect, useState } from 'react';
import { type Factor3ChallengeResponse, getFactor3Challenge, verifyFactor3 } from '../api/client';
import { StepLayout } from './StepLayout';

type Factor3ChallengeProps = {
  token: string;
  onBackToLogin: () => void;
  onSuccess: () => void;
};

function caesarCipher(input: string, rotation: number): string {
  const shift = ((rotation % 26) + 26) % 26;
  return Array.from(input)
    .map((ch) => {
      const code = ch.charCodeAt(0);
      if (code >= 65 && code <= 90) {
        // A-Z
        return String.fromCharCode(((code - 65 + shift) % 26) + 65);
      }
      if (code >= 97 && code <= 122) {
        // a-z
        return String.fromCharCode(((code - 97 + shift) % 26) + 97);
      }
      return ch;
    })
    .join('');
}

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

  function handleAutoGenerate() {
    if (!challenge) return;
    const generated = caesarCipher(challenge.plaintext, challenge.rotation);
    setCiphertext(generated);
  }

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
            <div>
              <span className="field-label">Rotation</span>
              <code className="code-pill">{challenge?.rotation}</code>
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
            <div className="footer-actions">
              <button
                type="button"
                className="button secondary"
                onClick={handleAutoGenerate}
                disabled={!challenge}
              >
                Auto-generate from plaintext
              </button>
              <button className="button primary" type="submit" disabled={submitting}>
                {submitting ? 'Verifying…' : 'Verify'}
              </button>
            </div>
            {error && <p className="error-text">{error}</p>}
          </form>
        </>
      )}
    </StepLayout>
  );
}

