// Backend API configuration
// You can override the base URL by setting window.API_BASE_URL before this script loads
const API_CONFIG = {
  baseUrl: window.API_BASE_URL || "https://ai-news-web.onrender.com",
  endpoints: {
    subscribe: "/api/subscribe",
    unsubscribe: "/unsubscribe",
  },
};
