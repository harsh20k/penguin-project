import type { ReactNode } from 'react';

type StepLayoutProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  footer?: ReactNode;
};

export function StepLayout({ title, subtitle, children, footer }: StepLayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">Penguin Auth Demo</h1>
        <p className="app-subtitle">Three-factor auth flow against the Penguin backend</p>
      </header>
      <main className="app-main">
        <section className="card">
          <h2 className="card-title">{title}</h2>
          {subtitle && <p className="card-subtitle">{subtitle}</p>}
          <div className="card-body">{children}</div>
          {footer && <div className="card-footer">{footer}</div>}
        </section>
      </main>
    </div>
  );
}

