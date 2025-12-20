import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { unsubscribe } from "../services/api";

const Unsubscribe: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid unsubscribe link.");
      return;
    }

    const handleUnsubscribe = async () => {
      try {
        const result = await unsubscribe(token);

        if (result.ok) {
          setStatus("success");
          setMessage(
            result.message || "You've been unsubscribed successfully."
          );
          if (result.email) {
            setEmail(result.email);
          }
        } else {
          setStatus("error");
          setMessage(
            result.error ||
              "This unsubscribe link is invalid or has already been used."
          );
        }
      } catch (error) {
        setStatus("error");
        setMessage(
          "Network error. Please check your connection and try again."
        );
      }
    };

    handleUnsubscribe();
  }, [token]);

  return (
    <div className="pt-32 px-6 md:px-12 max-w-4xl mx-auto pb-24 min-h-screen flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="border-2 border-black bg-white shadow-[12px_12px_0px_0px_rgba(26,26,26,1)] p-12">
          {status === "loading" && (
            <div className="text-center">
              <div className="text-4xl font-black uppercase tracking-tighter mb-4">
                Processing...
              </div>
              <p className="text-sm text-black/60 uppercase tracking-widest">
                Please wait
              </p>
            </div>
          )}

          {status === "success" && (
            <div className="text-center">
              <div className="text-4xl font-black uppercase tracking-tighter mb-6 text-green-600">
                Unsubscribed
              </div>
              {email && (
                <p className="text-sm text-black/60 mb-4 uppercase tracking-widest">
                  {email}
                </p>
              )}
              <p className="text-sm text-black/70 mb-8 leading-relaxed">
                {message}
              </p>
              <Link
                to="/"
                className="inline-block px-8 py-3 bg-black text-white font-black uppercase text-sm tracking-widest hover:bg-[#ff4d4d] transition-colors"
              >
                Subscribe Again
              </Link>
            </div>
          )}

          {status === "error" && (
            <div className="text-center">
              <div className="text-4xl font-black uppercase tracking-tighter mb-6 text-red-600">
                Error
              </div>
              <p className="text-sm text-black/70 mb-8 leading-relaxed">
                {message}
              </p>
              <Link
                to="/"
                className="inline-block px-8 py-3 bg-black text-white font-black uppercase text-sm tracking-widest hover:bg-[#ff4d4d] transition-colors"
              >
                Back to Home
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Unsubscribe;
