import { type FormEvent, useEffect, useState } from 'react';
import { getFactor2Question, verifyFactor2 } from '../api/client';
import { StepLayout } from './StepLayout';

type Factor2QuestionProps = {
  token: string;
  onBackToLogin: () => void;
  onSuccess: () => void;
};

export function Factor2Question({ token, onBackToLogin, onSuccess }: Factor2QuestionProps) {
  const [question, setQuestion] = useState<string | null>(null);
  const [answer, setAnswer] = useState('blue');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    getFactor2Question(token)
      .then((res) => {
        if (!cancelled) {
          setQuestion(res.question);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load question';
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
      const res = await verifyFactor2(token, answer);
      if (res.success) {
        onSuccess();
      } else {
        setError('Invalid answer');
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
      title="Step 2: Security question"
      subtitle="Answer your security question to complete factor 2."
      footer={footer}
    >
      {loading ? (
        <p className="muted">Loading question…</p>
      ) : error && !question ? (
        <p className="error-text">{error}</p>
      ) : (
        <form className="form" onSubmit={handleSubmit}>
          <p className="question-text">{question}</p>
          <label className="field">
            <span className="field-label">Answer</span>
            <input
              className="input"
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              required
            />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button className="button primary" type="submit" disabled={submitting}>
            {submitting ? 'Verifying…' : 'Verify'}
          </button>
        </form>
      )}
    </StepLayout>
  );
}

