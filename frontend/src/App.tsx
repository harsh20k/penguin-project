import { useState } from 'react';
import { LoginForm } from './components/LoginForm';
import { Factor2Question } from './components/Factor2Question';
import { Factor3Challenge } from './components/Factor3Challenge';
import { StepLayout } from './components/StepLayout';
import './App.css';

type Step = 'login' | 'factor2' | 'factor3' | 'done';

function App() {
  const [currentStep, setCurrentStep] = useState<Step>('login');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  function resetAll() {
    setSessionId(null);
    setToken(null);
    setCurrentStep('login');
  }

  function handleLoginSuccess(args: { sessionId: string; token: string }) {
    setSessionId(args.sessionId);
    setToken(args.token);
    setCurrentStep('factor2');
  }

  function handleFactor2Success() {
    setCurrentStep('factor3');
  }

  function handleFactor3Success() {
    setCurrentStep('done');
  }

  if (!token) {
    return <LoginForm onLoginSuccess={handleLoginSuccess} />;
  }

  if (currentStep === 'factor2') {
    return (
      <Factor2Question
        token={token}
        onBackToLogin={resetAll}
        onSuccess={handleFactor2Success}
      />
    );
  }

  if (currentStep === 'factor3') {
    return (
      <Factor3Challenge
        token={token}
        onBackToLogin={resetAll}
        onSuccess={handleFactor3Success}
      />
    );
  }

  return (
    <StepLayout
      title="Authenticated"
      subtitle="You have completed all three factors."
      footer={
        <button className="button primary" type="button" onClick={resetAll}>
          Start over
        </button>
      }
    >
      <div className="success-message">
        <p>Session established successfully.</p>
        {sessionId && (
          <p className="muted">
            Session ID: <code>{sessionId}</code>
          </p>
        )}
      </div>
    </StepLayout>
  );
}

export default App;
