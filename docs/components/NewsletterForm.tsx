import React, { useState } from "react";
import { subscribe } from "../services/api";

const NewsletterForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
      setStatus("error");
      setMessage("Please enter a valid email address.");
      return;
    }

    setStatus("loading");
    setMessage("");

    try {
      const result = await subscribe(email.trim());

      if (result.ok) {
        if (result.already_subscribed) {
          setStatus("success");
          setMessage("You're already subscribed!");
        } else {
          setStatus("success");
          setMessage(
            "Thanks for joining our orbit. Check your inbox for a welcome email."
          );
          setEmail("");
        }
      } else {
        setStatus("error");
        setMessage(
          result.error || "Something went wrong. Please try again later."
        );
      }
    } catch (error) {
      setStatus("error");
      setMessage("Network error. Please check your connection and try again.");
    }
  };

  return (
    <div className="w-full max-w-md">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="flex border-2 border-black overflow-hidden bg-white shadow-[8px_8px_0px_0px_rgba(26,26,26,1)] transition-transform group-hover:translate-x-1 group-hover:translate-y-1 group-hover:shadow-[4px_4px_0px_0px_rgba(26,26,26,1)]">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="ENTER YOUR EMAIL"
            disabled={status === "loading" || status === "success"}
            className="flex-grow px-6 py-4 outline-none uppercase text-sm font-bold tracking-widest placeholder:text-black/20"
          />
          <button
            type="submit"
            disabled={status === "loading" || status === "success"}
            className={`px-8 py-4 bg-black text-white font-black uppercase text-sm tracking-tighter transition-colors hover:bg-[#ff4d4d] ${
              status === "loading" ? "cursor-not-allowed opacity-50" : ""
            }`}
          >
            {status === "loading" ? "JOINING..." : "JOIN"}
          </button>
        </div>

        {message && (
          <p
            className={`mt-6 text-xs font-black uppercase tracking-widest ${
              status === "error" ? "text-red-600" : "text-green-600"
            }`}
          >
            {message}
          </p>
        )}
      </form>
    </div>
  );
};

export default NewsletterForm;
