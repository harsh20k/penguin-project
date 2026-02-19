import { type FormEvent, useState } from 'react';
import { StepLayout } from './StepLayout';

export type SignupPayload = {
  email: string;
  password: string;
  question: string;
  answer: string;
  rotation: number;
};

type SignupRotationStepProps = {
  signupData: {
    email: string;
    password: string;
    question: string;
    answer: string;
  };
  onBack: () => void;
  onCreateAccount: (fullData: SignupPayload) => Promise<void>;
};

const MIN_ROTATION = 1;
const MAX_ROTATION = 25;

export function SignupRotationStep({
  signupData,
  onBack,
  onCreateAccount,
}: SignupRotationStepProps) {
  const [rotation, setRotation] = useState(7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const r = Math.floor(Number(rotation));
    if (r < MIN_ROTATION || r > MAX_ROTATION) {
      setError(`Rotation must be between ${MIN_ROTATION} and ${MAX_ROTATION}`);
      return;
    }
    setLoading(true);
    try {
      await onCreateAccount({ ...signupData, rotation: r });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Create account failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  const footer = (
    <div className="footer-actions">
      <button type="button" className="button ghost" onClick={onBack} disabled={loading}>
        Back
      </button>
      <button
        type="submit"
        form="signup-rotation-form"
        className="button primary"
        disabled={loading}
      >
        {loading ? 'Creating account…' : 'Create account'}
      </button>
    </div>
  );

  return (
    <StepLayout
      title="Step 3: Caesar cipher rotation"
      subtitle="Choose a rotation (1–25) for your Caesar cipher. You'll use this at login for factor 3."
      footer={footer}
    >
      <form
        id="signup-rotation-form"
        className="form"
        onSubmit={handleSubmit}
      >
        <label className="field">
          <span className="field-label">Rotation</span>
          <input
            className="input"
            type="number"
            min={MIN_ROTATION}
            max={MAX_ROTATION}
            value={rotation}
            onChange={(e) => setRotation(e.target.value)}
            required
          />
        </label>
        {error && <p className="error-text">{error}</p>}
      </form>
    </StepLayout>
  );
}
