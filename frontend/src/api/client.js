/**
 * 백엔드 API 호출 래퍼.
 *
 * VITE_API_BASE_URL 환경변수로 baseURL 변경 가능 (기본: 빈 문자열 → 동일 origin).
 * 개발 환경: vite.config.js의 proxy로 /api → localhost:8000
 * 프로덕션: nginx가 같은 origin에서 /api를 백엔드 컨테이너로 프록시
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!res.ok) {
    let detail = res.status === 429
      ? '요청이 너무 많아요. 잠시 후 다시 시도해주세요.'
      : `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      // body가 JSON이 아니면 status만 사용
    }
    throw new ApiError(detail, res.status);
  }

  // DELETE 등 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

export const api = {
  generate: (payload) =>
    request('/api/reviews/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  translate: (reviewId, lang) =>
    request(`/api/reviews/${reviewId}/translate`, {
      method: 'POST',
      body: JSON.stringify({ lang }),
    }),

  history: (limit = 20, offset = 0) =>
    request(`/api/reviews/history?limit=${limit}&offset=${offset}`),

  getReview: (id) =>
    request(`/api/reviews/${id}`),

  deleteReview: (id) =>
    request(`/api/reviews/${id}`, { method: 'DELETE' }),
};

export { ApiError };
