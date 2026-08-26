const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8003";

const ACCESS_TOKEN_KEY = "edupath_access_token";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token) {
  if (!token) {
    return;
  }

  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    token
  );
}

export function clearAccessToken() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );
}

export async function authFetch(
  path,
  options = {}
) {
  const token = getAccessToken();

  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization =
      `Bearer ${token}`;
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers,
    }
  );

  if (
    response.status === 401 &&
    token
  ) {
    clearAccessToken();

    window.dispatchEvent(
      new Event(
        "edupath-auth-expired"
      )
    );
  }

  return response;
}

export async function readApiError(
  response,
  fallbackMessage = "Request failed."
) {
  try {
    const data = await response.json();

    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join(" ");
    }

    if (typeof data?.message === "string") {
      return data.message;
    }
  } catch {
    // Ignore invalid JSON response bodies.
  }

  return fallbackMessage;
}

export default API_BASE_URL;
