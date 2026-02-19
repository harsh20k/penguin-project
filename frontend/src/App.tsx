import { useState } from 'react';
import { login, signup } from './api/client';
import { LoginForm } from './components/LoginForm';
import { SignupQuestionStep } from './components/SignupQuestionStep';
import { SignupRotationStep, type SignupPayload } from './components/SignupRotationStep';
import { Factor2Question } from './components/Factor2Question';
import { Factor3Challenge } from './components/Factor3Challenge';
import { StepLayout } from './components/StepLayout';
import './App.css';

type Step = 'login' | 'factor2' | 'factor3' | 'done';
type SignupStep = 1 | 2 | 3;

type SignupData = {
  email: string;
  password: string;
  question?: string;
  answer?: string;
  rotation?: number;
};

function App() {
  const [currentStep, setCurrentStep] = useState<Step>('login');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [signupMode, setSignupMode] = useState(false);
  const [signupStep, setSignupStep] = useState<SignupStep>(1);
  const [signupData, setSignupData] = useState<SignupData>({ email: '', password: '' });

  function resetAll() {
    setSessionId(null);
    setToken(null);
    setCurrentStep('login');
    setSignupMode(false);
    setSignupStep(1);
    setSignupData({ email: '', password: '' });
  }

  function handleLoginSuccess(args: { sessionId: string; token: string }) {
    setSessionId(args.sessionId);
    setToken(args.token);
    setCurrentStep('factor2');
  }

  function handleSignupStart(data: { email: string; password: string }) {
    setSignupData({ ...data });
    setSignupMode(true);
    setSignupStep(2);
  }

  async function handleCreateAccount(fullData: SignupPayload) {
    await signup({
      email: fullData.email,
      password: fullData.password,
      role: 'client',
      question: fullData.question,
      answer: fullData.answer,
      rotation: fullData.rotation,
    });
    const res = await login(fullData.email, fullData.password);
    handleLoginSuccess({ sessionId: res.session_id, token: res.token });
  }

  function handleFactor2Success() {
    setCurrentStep('factor3');
  }

  function handleFactor3Success() {
    setCurrentStep('done');
  }

  if (!token) {
    if (signupMode && signupStep === 2) {
      return (
        <SignupQuestionStep
          initialQuestion={signupData.question}
          initialAnswer={signupData.answer}
          onBack={() => {
            setSignupMode(false);
            setSignupStep(1);
          }}
          onNext={(data) => {
            setSignupData((prev) => ({ ...prev, ...data }));
            setSignupStep(3);
          }}
        />
      );
    }
    if (signupMode && signupStep === 3) {
      return (
        <SignupRotationStep
          signupData={{
            email: signupData.email,
            password: signupData.password,
            question: signupData.question ?? '',
            answer: signupData.answer ?? '',
          }}
          onBack={() => setSignupStep(2)}
          onCreateAccount={handleCreateAccount}
        />
      );
    }
    return (
      <LoginForm
        onLoginSuccess={handleLoginSuccess}
        onSignupStart={handleSignupStart}
      />
    );
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
