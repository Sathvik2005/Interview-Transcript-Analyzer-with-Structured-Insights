export type AnalysisResponse = {
  topics_covered: string[];
  profile: {
    role: string;
    level: string;
    justification: string;
  };
  candidate_summary: string;
};

export async function analyzeTranscript(transcript: string): Promise<AnalysisResponse> {
  const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
  const isLocalhostTarget = (() => {
    if (!configuredBaseUrl) {
      return false;
    }

    try {
      const parsed = new URL(configuredBaseUrl);
      return parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1';
    } catch {
      return false;
    }
  })();
  const isLocalRuntime = /^localhost$|^127\.0\.0\.1$/.test(window.location.hostname);
  const baseUrl = isLocalhostTarget && !isLocalRuntime ? '' : configuredBaseUrl;
  const response = await fetch(`${baseUrl}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ transcript, provider: import.meta.env.VITE_LLM_PROVIDER }),
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const body = await response.json();
      if (typeof body?.detail === 'string' && body.detail.trim()) {
        message = body.detail;
      } else if (Array.isArray(body?.detail) && body.detail.length > 0) {
        message = body.detail.map((item: { msg?: string }) => item?.msg).filter(Boolean).join('; ') || message;
      }
    } catch {
      const text = await response.text();
      if (text.trim()) {
        message = text;
      }
    }

    throw new Error(message);
  }

  return response.json();
}
