const API_BASE_URL = (
  import.meta.env.VITE_API_BASE ?? import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
).replace(/\/$/, '');

export type LoginResponse = {
  session_id: string;
  token: string;
  id_token?: string;
  access_token?: string;
};

export type Factor2QuestionResponse = {
  question: string;
};

export type Factor2VerifyResponse = {
  success: boolean;
};

export type Factor3ChallengeResponse = {
  plaintext: string;
};

export type Factor3VerifyResponse = {
  authenticated: boolean;
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body && typeof body.detail === 'string') {
        message = body.detail;
      }
    } catch {
      // ignore JSON parse errors, keep default message
    }
    throw new Error(message);
  }
  return (await res.json()) as T;
}

function authHeaders(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  return handleResponse<LoginResponse>(res);
}


export async function signup(args: {
  email: string;
  password: string;
  role?: string;
  question?: string;
  answer?: string;
  rotation?: number;
}): Promise<{ user_id: string }> {
  const res = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: args.email,
      password: args.password,
      role: args.role ?? 'client',
      question: args.question,
      answer: args.answer,
      rotation: args.rotation,
    }),
  });
  return handleResponse<{ user_id: string }>(res);
}

export async function getFactor2Question(token: string): Promise<Factor2QuestionResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/factor2/question`, {
    headers: authHeaders(token),
  });
  return handleResponse<Factor2QuestionResponse>(res);
}

export async function verifyFactor2(token: string, answer: string): Promise<Factor2VerifyResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/factor2/verify`, {
    method: 'POST',
    headers: {
      ...authHeaders(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ answer }),
  });
  return handleResponse<Factor2VerifyResponse>(res);
}

export async function getFactor3Challenge(token: string): Promise<Factor3ChallengeResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/factor3/challenge`, {
    headers: authHeaders(token),
  });
  return handleResponse<Factor3ChallengeResponse>(res);
}

export async function verifyFactor3(
  token: string,
  ciphertext: string,
): Promise<Factor3VerifyResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/factor3/verify`, {
    method: 'POST',
    headers: {
      ...authHeaders(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ ciphertext }),
  });
  return handleResponse<Factor3VerifyResponse>(res);
}

