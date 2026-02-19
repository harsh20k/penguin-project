import { type FormEvent, useState } from 'react';
import { StepLayout } from './StepLayout';

type SignupQuestionStepProps = {
  initialQuestion?: string;
  initialAnswer?: string;
  onBack: () => void;
  onNext: (data: { question: string; answer: string }) => void;
};

export function SignupQuestionStep({
  initialQuestion = '',
  initialAnswer = '',
  onBack,
  onNext,
}: SignupQuestionStepProps) {
  const [question, setQuestion] = useState(initialQuestion);
  const [answer, setAnswer] = useState(initialAnswer);
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const q = question.trim();
    const a = answer.trim();
    if (!q || !a) {
      setError('Question and answer are required');
      return;
    }
    onNext({ question: q, answer: a });
  }

  const footer = (
    <div className="footer-actions">
      <button type="button" className="button ghost" onClick={onBack}>
        Back
      </button>
      <button
        type="submit"
        form="signup-question-form"
        className="button primary"
      >
        Next
      </button>
    </div>
  );

  return (
    <StepLayout
      title="Step 2: Security question"
      subtitle="Create a security question and answer. You'll use this at login for factor 2."
      footer={footer}
    >
      <form
        id="signup-question-form"
        className="form"
        onSubmit={handleSubmit}
      >
        <label className="field">
          <span className="field-label">Question</span>
          <input
            className="input"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. What is your favorite color?"
            required
          />
        </label>
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
      </form>
    </StepLayout>
  );
}
