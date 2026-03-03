import { useState } from 'react';
import { StepLayout } from './StepLayout';

type Role = 'client' | 'dispatch';

type SignupRoleStepProps = {
  initialRole?: Role;
  onBack: () => void;
  onNext: (role: Role) => void;
};

const ROLES: { value: Role; label: string; description: string }[] = [
  { value: 'client', label: 'Client / Customer', description: 'Place and track shipment orders.' },
  { value: 'dispatch', label: 'Dispatch Operator', description: 'Manage and dispatch shipment orders.' },
];

export function SignupRoleStep({ initialRole, onBack, onNext }: SignupRoleStepProps) {
  const [selected, setSelected] = useState<Role>(initialRole ?? 'client');

  const footer = (
    <div className="footer-actions">
      <button type="button" className="button ghost" onClick={onBack}>
        Back
      </button>
      <button type="button" className="button primary" onClick={() => onNext(selected)}>
        Next
      </button>
    </div>
  );

  return (
    <StepLayout
      title="Step 1: Select your role"
      subtitle="Choose the role that best describes how you'll use the system."
      footer={footer}
    >
      <div className="role-options">
        {ROLES.map((role) => (
          <label
            key={role.value}
            className={`role-option${selected === role.value ? ' role-option--selected' : ''}`}
          >
            <input
              type="radio"
              name="role"
              value={role.value}
              checked={selected === role.value}
              onChange={() => setSelected(role.value)}
            />
            <div className="role-option-text">
              <span className="role-option-label">{role.label}</span>
              <span className="role-option-desc">{role.description}</span>
            </div>
          </label>
        ))}
      </div>
    </StepLayout>
  );
}
