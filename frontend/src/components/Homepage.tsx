import { StepLayout } from './StepLayout';

type HomepageProps = {
  sessionId: string | null;
  onLogout: () => void;
};

export function Homepage({ sessionId, onLogout }: HomepageProps) {
  return (
    <StepLayout
      title="Welcome to Penguin Auth"
      subtitle="You have successfully authenticated with all three factors."
      footer={
        <button className="button primary" type="button" onClick={onLogout}>
          Logout
        </button>
      }
    >
      <div className="homepage-content">
        <div className="success-icon">✓</div>
        <p className="success-message">Your session is active and secure.</p>
        {sessionId && (
          <div className="session-info">
            <p className="muted">
              Session ID: <code>{sessionId}</code>
            </p>
          </div>
        )}
        <div className="homepage-info">
          <h3>Three-Factor Authentication Complete</h3>
          <ul>
            <li>Factor 1: Password authentication via AWS Cognito</li>
            <li>Factor 2: Security question verification</li>
            <li>Factor 3: Caesar cipher challenge</li>
          </ul>
        </div>
      </div>
    </StepLayout>
  );
}
