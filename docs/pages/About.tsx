import React from "react";

const About: React.FC = () => {
  return (
    <div className="pt-32 px-6 md:px-12 max-w-4xl mx-auto pb-24">
      <h1 className="text-5xl md:text-7xl font-black uppercase tracking-tighter mb-12">
        Behind The <span className="sketch-underline">Logic.</span>
      </h1>

      <section className="mb-20 space-y-8">
        <div className="aspect-video bg-[#f0f0f0] border-2 border-black flex items-center justify-center overflow-hidden shadow-[12px_12px_0px_0px_rgba(26,26,26,1)]">
          <div className="text-center p-8">
            <p className="text-sm uppercase tracking-widest text-black/40 font-black mb-2">
              System Architecture Screenshot
            </p>
            <p className="text-xs text-black/30">
              Add a screenshot of the system architecture or pipeline here
            </p>
          </div>
        </div>
        <p className="text-xl leading-relaxed text-black/70 italic border-l-4 border-[#ff4d4d] pl-6 font-medium">
          "The most powerful ideas are often the simplest ones. We built Neural
          Notes to strip away the noise and focus on the raw architecture of
          progress."
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
        <div className="space-y-6">
          <h2 className="text-2xl font-black uppercase tracking-tight">
            The Vision
          </h2>
          <p className="text-black/60 leading-relaxed">
            AI News is an automated newsletter system that curates and delivers
            the most important artificial intelligence news directly to your
            inbox every day. Our system uses AI to analyze, rank, and summarize
            news from multiple sources, ensuring you stay informed about the
            latest developments in AI without information overload.
          </p>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-black uppercase tracking-tight">
            The Build
          </h2>
          <p className="text-black/60 leading-relaxed">
            Architected with a mobile-first philosophy. We utilize React and
            Tailwind for an ultra-fast, zero-bloat experience. Every component,
            from the 3D cube to the typography, is designed to evoke a sense of
            focused clarity.
          </p>
        </div>
      </div>

      <section className="mt-24 pt-12 border-t border-black/10">
        <h2 className="text-3xl font-black uppercase tracking-tighter mb-8">
          How It Works
        </h2>
        <div className="space-y-12">
          <div className="flex gap-8 items-start">
            <span className="text-4xl font-black text-[#ff4d4d]/20">01</span>
            <div>
              <h3 className="text-xl font-bold uppercase mb-2">
                News Collection
              </h3>
              <p className="text-black/60 leading-relaxed mb-4">
                Our system automatically fetches the latest AI news from
                multiple sources within a 24-hour window:
              </p>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-bold uppercase text-black/80 mb-1">
                    RSS Feed:
                  </p>
                  <p className="text-sm text-black/60">
                    • Techmeme (https://www.techmeme.com/feed.xml) - Aggregates
                    top tech news including AI developments
                  </p>
                </div>
                <div>
                  <p className="text-sm font-bold uppercase text-black/80 mb-1">
                    YouTube Channels (10 channels monitored):
                  </p>
                  <ul className="text-sm text-black/60 space-y-1 list-disc list-inside">
                    <li>@matthew_berman - AI news and tutorials</li>
                    <li>@aiDotEngineer - AI engineering insights</li>
                    <li>@aiadvantage - AI tools and updates</li>
                    <li>@aiexplained-official - AI explanations</li>
                    <li>@mreflow - AI and tech content</li>
                    <li>@Fireship - Fast-paced tech news</li>
                    <li>@IshanSharma7390 - AI and programming</li>
                    <li>@OpenAI - Official OpenAI channel</li>
                    <li>@anthropic-ai - Anthropic AI updates</li>
                    <li>@google - Google AI and tech announcements</li>
                  </ul>
                </div>
                <p className="text-sm text-black/60 mt-3">
                  The system fetches only content published in the last 24 hours
                  to ensure you receive the freshest news.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-8 items-start">
            <span className="text-4xl font-black text-[#ff4d4d]/20">02</span>
            <div>
              <h3 className="text-xl font-bold uppercase mb-2">
                Video Transcription
              </h3>
              <p className="text-black/60 leading-relaxed mb-4">
                For YouTube videos, we use a locally-run Whisper transcription
                worker that processes videos automatically:
              </p>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-bold uppercase text-black/80 mb-1">
                    Technology Stack:
                  </p>
                  <ul className="text-sm text-black/60 space-y-1 list-disc list-inside">
                    <li>
                      <strong>faster-whisper</strong> - Optimized Whisper
                      implementation for GPU acceleration
                    </li>
                    <li>
                      <strong>Model:</strong> distil-large-v3 (downloaded and
                      cached locally)
                    </li>
                    <li>
                      <strong>Device:</strong> CUDA GPU for fast transcription
                    </li>
                    <li>
                      <strong>yt-dlp:</strong> Downloads audio-only from YouTube
                      videos
                    </li>
                  </ul>
                </div>
                <div>
                  <p className="text-sm font-bold uppercase text-black/80 mb-1">
                    Process:
                  </p>
                  <ol className="text-sm text-black/60 space-y-1 list-decimal list-inside">
                    <li>
                      Server identifies top-ranked YouTube videos needing
                      transcription
                    </li>
                    <li>
                      Worker fetches video IDs and downloads audio files locally
                    </li>
                    <li>
                      Whisper model transcribes each video sequentially using
                      GPU acceleration
                    </li>
                    <li>
                      Transcripts are normalized and uploaded back to the server
                    </li>
                    <li>Temporary files are cleaned up automatically</li>
                  </ol>
                </div>
                <div className="mt-4 aspect-video bg-[#f0f0f0] border-2 border-black flex items-center justify-center overflow-hidden shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
                  <div className="text-center p-6">
                    <p className="text-xs uppercase tracking-widest text-black/40 font-black mb-2">
                      Transcription Worker Screenshot
                    </p>
                    <p className="text-[10px] text-black/30">
                      Add screenshot of worker processing videos or
                      transcription output here
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-8 items-start">
            <span className="text-4xl font-black text-[#ff4d4d]/20">03</span>
            <div>
              <h3 className="text-xl font-bold uppercase mb-2">
                AI Ranking & Selection
              </h3>
              <p className="text-black/60 leading-relaxed mb-4">
                Using Google Gemini AI, our system analyzes all collected
                content and ranks it based on:
              </p>
              <ul className="text-sm text-black/60 space-y-1 list-disc list-inside mb-4">
                <li>Relevance to AI and technology</li>
                <li>Importance and impact</li>
                <li>Timeliness</li>
                <li>Quality of content</li>
              </ul>
              <p className="text-black/60 leading-relaxed">
                Only the top 10 most significant stories make it into the daily
                newsletter, ensuring you receive only the highest-quality,
                most-relevant content.
              </p>
              <div className="mt-4 aspect-video bg-[#f0f0f0] border-2 border-black flex items-center justify-center overflow-hidden shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
                <div className="text-center p-6">
                  <p className="text-xs uppercase tracking-widest text-black/40 font-black mb-2">
                    Ranking Process Screenshot
                  </p>
                  <p className="text-[10px] text-black/30">
                    Add screenshot of AI ranking output or news selection
                    process here
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-8 items-start">
            <span className="text-4xl font-black text-[#ff4d4d]/20">04</span>
            <div>
              <h3 className="text-xl font-bold uppercase mb-2">
                Newsletter Generation
              </h3>
              <p className="text-black/60 leading-relaxed mb-4">
                The selected news items are compiled into a beautifully
                formatted email newsletter with:
              </p>
              <ul className="text-sm text-black/60 space-y-1 list-disc list-inside mb-4">
                <li>Summarized articles from RSS feeds</li>
                <li>Transcribed and summarized YouTube video content</li>
                <li>Key highlights and takeaways</li>
                <li>Direct links to original sources</li>
                <li>Mobile-friendly HTML email design</li>
              </ul>
              <div className="mt-4 aspect-video bg-[#f0f0f0] border-2 border-black flex items-center justify-center overflow-hidden shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
                <div className="text-center p-6">
                  <p className="text-xs uppercase tracking-widest text-black/40 font-black mb-2">
                    Newsletter Email Screenshot
                  </p>
                  <p className="text-[10px] text-black/30">
                    Add screenshot of the final newsletter email here
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-8 items-start">
            <span className="text-4xl font-black text-[#ff4d4d]/20">05</span>
            <div>
              <h3 className="text-xl font-bold uppercase mb-2">Delivery</h3>
              <p className="text-black/60 leading-relaxed">
                The newsletter is automatically sent to all active subscribers
                every morning at 9:00 AM Nepal Time (NPT), ensuring you start
                your day with the latest AI news. The entire pipeline runs
                automatically via scheduled jobs, requiring zero manual
                intervention.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-24 pt-12 border-t border-black/10">
        <h2 className="text-3xl font-black uppercase tracking-tighter mb-8">
          System Architecture
        </h2>
        <div className="space-y-6">
          <div className="aspect-video bg-[#f0f0f0] border-2 border-black flex items-center justify-center overflow-hidden shadow-[12px_12px_0px_0px_rgba(26,26,26,1)]">
            <div className="text-center p-8">
              <p className="text-sm uppercase tracking-widest text-black/40 font-black mb-2">
                Pipeline Flow Diagram
              </p>
              <p className="text-xs text-black/30">
                Add a diagram showing: RSS/YouTube → Ranking → Transcription →
                Newsletter → Email
              </p>
            </div>
          </div>
          <p className="text-black/60 leading-relaxed">
            The system consists of three main components: a backend server
            (hosted on Render) that orchestrates the pipeline, a local GPU
            worker that handles video transcription, and automated scheduled
            jobs that trigger the process daily.
          </p>
        </div>
      </section>

      <section className="mt-24 pt-12 border-t border-black/10">
        <h2 className="text-3xl font-black uppercase tracking-tighter mb-8">
          What You Get
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 border-2 border-black bg-white shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
            <h3 className="text-lg font-black uppercase mb-3">
              Daily Curated News
            </h3>
            <p className="text-sm text-black/60">
              Top 10 AI news stories from RSS feeds and YouTube channels,
              delivered to your inbox every morning.
            </p>
          </div>
          <div className="p-6 border-2 border-black bg-white shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
            <h3 className="text-lg font-black uppercase mb-3">
              Video Transcriptions
            </h3>
            <p className="text-sm text-black/60">
              Full transcriptions of YouTube videos using locally-run Whisper
              AI, so you can read the content without watching.
            </p>
          </div>
          <div className="p-6 border-2 border-black bg-white shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
            <h3 className="text-lg font-black uppercase mb-3">
              AI-Powered Summaries
            </h3>
            <p className="text-sm text-black/60">
              Each news item is summarized using Google Gemini AI to extract key
              insights and highlights.
            </p>
          </div>
          <div className="p-6 border-2 border-black bg-white shadow-[8px_8px_0px_0px_rgba(26,26,26,1)]">
            <h3 className="text-lg font-black uppercase mb-3">
              Mobile-Friendly Format
            </h3>
            <p className="text-sm text-black/60">
              Beautifully formatted HTML emails that look great on any device,
              from desktop to mobile.
            </p>
          </div>
        </div>
      </section>

      <div className="mt-24 p-12 bg-black text-white text-center rounded-sm">
        <h2 className="text-3xl font-black uppercase mb-6">
          Ready to upgrade?
        </h2>
        <p className="mb-8 text-white/60">
          Join researchers and engineers staying informed about AI.
        </p>
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="px-8 py-3 bg-[#ff4d4d] hover:bg-white hover:text-black transition-colors font-black uppercase text-sm tracking-widest"
        >
          Back to Top
        </button>
      </div>
    </div>
  );
};

export default About;
