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


function wait(milliseconds) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

export async function warmBackend() {
  try {
    await fetch(
      `${API_BASE_URL}/api/health`,
      {
        method: "GET",
        cache: "no-store",
      }
    );

    return true;
  } catch {
    // A failed first request can still trigger
    // a sleeping Render service to wake up.
    return false;
  }
}

export async function apiFetchWithRetry(
  path,
  options = {},
  retryDelays = [
    0,
    1500,
    2500,
  ]
) {
  const REQUEST_TIMEOUT_MS = 8000;

  for (
    let attempt = 0;
    attempt < retryDelays.length;
    attempt += 1
  ) {
    const delay = retryDelays[attempt];

    if (delay > 0) {
      await wait(delay);
    }

    const controller = new AbortController();

    const timeoutId = window.setTimeout(
      () => controller.abort(),
      REQUEST_TIMEOUT_MS
    );

    try {
      const response = await fetch(
        `${API_BASE_URL}${path}`,
        {
          ...options,
          signal: controller.signal,
        }
      );

      const retryable =
        response.status === 502 ||
        response.status === 503 ||
        response.status === 504;

      if (!retryable) {
        return response;
      }

      if (
        attempt ===
        retryDelays.length - 1
      ) {
        throw new Error(
          "EduPath server is still starting. " +
          "Please wait a few seconds and try again."
        );
      }
    } catch (error) {
      if (
        attempt ===
        retryDelays.length - 1
      ) {
        throw new Error(
          "EduPath server is taking longer than expected to respond. " +
          "Please wait a few seconds and try again."
        );
      }
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  throw new Error(
    "Unable to connect to the EduPath server."
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
