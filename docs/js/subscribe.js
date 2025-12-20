// Subscription form handling

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("subscribe-form");
  const emailInput = document.getElementById("email-input");
  const submitButton = document.getElementById("submit-button");
  const statusDiv = document.getElementById("status-message");

  if (!form || !emailInput || !submitButton) {
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = emailInput.value.trim();

    // Basic client-side validation
    if (!email) {
      showStatus("Please enter your email address.", "error");
      return;
    }

    if (!isValidEmail(email)) {
      showStatus("Please enter a valid email address.", "error");
      return;
    }

    // Disable form during submission
    submitButton.disabled = true;
    emailInput.disabled = true;
    showStatus("Subscribing...", "loading");

    try {
      const response = await fetch(
        `${API_CONFIG.baseUrl}${API_CONFIG.endpoints.subscribe}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email: email }),
        }
      );

      const data = await response.json();

      if (data.ok) {
        if (data.already_subscribed) {
          showStatus("You're already subscribed to AI News!", "success");
        } else {
          showStatus(
            "You're subscribed! Check your inbox for a welcome email.",
            "success"
          );
          // Clear the form
          emailInput.value = "";
        }
      } else {
        showStatus(
          data.error || "Something went wrong. Please try again later.",
          "error"
        );
      }
    } catch (error) {
      console.error("Subscription error:", error);
      showStatus(
        "Network error. Please check your connection and try again.",
        "error"
      );
    } finally {
      // Re-enable form
      submitButton.disabled = false;
      emailInput.disabled = false;
      emailInput.focus();
    }
  });

  function showStatus(message, type) {
    if (!statusDiv) return;

    statusDiv.textContent = message;
    statusDiv.className = `status status--${type}`;
    statusDiv.style.display = "block";

    // Scroll to status message
    statusDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
});
