// API service for making requests to the backend

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "https://ai-news-web-j6uy.onrender.com";

export interface SubscribeResponse {
  ok: boolean;
  email?: string;
  is_active?: boolean;
  already_subscribed?: boolean;
  error?: string;
}

export interface UnsubscribeResponse {
  ok: boolean;
  message?: string;
  email?: string;
  error?: string;
}

/**
 * Subscribe an email address to the newsletter
 */
export async function subscribe(email: string): Promise<SubscribeResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/subscribe`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Subscription error:", error);
    return {
      ok: false,
      error: "Network error. Please check your connection and try again.",
    };
  }
}

/**
 * Unsubscribe using a token from the email link
 */
export async function unsubscribe(token: string): Promise<UnsubscribeResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/unsubscribe/${token}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Unsubscribe error:", error);
    return {
      ok: false,
      error: "Network error. Please check your connection and try again.",
    };
  }
}
