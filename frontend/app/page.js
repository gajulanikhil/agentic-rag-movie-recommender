"use client";

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from './page.module.css';

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [mood, setMood] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Loading Messages State
  const loadingMessages = [
    "Finding your next movie...",
    "Scanning the film universe...",
    "Rolling the reels...",
    "Analyzing critical reviews...",
    "Preparing your marquee..."
  ];
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);

  // Speech Recognition state
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  // Filters state
  const [genre, setGenre] = useState("All");
  const [minYear, setMinYear] = useState(1950);
  const [minRating, setMinRating] = useState(0.0);
  const [contentType, setContentType] = useState("All");

  const moods = [
    { emoji: "🤩", label: "Fun", color: "#f39c12" },
    { emoji: "🦉", label: "Thrilling", color: "#e74c3c" },
    { emoji: "❤️", label: "Romantic", color: "#e84393" },
    { emoji: "🚀", label: "SC-Fi", color: "#9b59b6" },
    { emoji: "🤔", label: "Surprise Me", color: "#3498db" }
  ];

  // Cycling Loading Messages
  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length);
      }, 2500);
    } else {
      setLoadingMessageIndex(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Initialize Speech Recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setPrompt(currentTranscript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      setPrompt(""); // Clear previous text when starting new speech
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  const handleSend = async () => {
    if (!prompt.trim()) return;
    const currentPrompt = prompt;
    setPrompt(""); // clear early to feel responsive
    setMessages(prev => [...prev, { type: 'user', content: currentPrompt }]);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: currentPrompt,
          mood,
          genre,
          min_year: minYear,
          max_year: 2024,
          min_rating: minRating,
          content_type: contentType
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { type: 'ai', content: data.response, sources: data.sources || [] }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'ai', content: "Error communicating with AI server." }]);
    }
    setLoading(false);
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={`${styles.sidebar} glass-panel`}>
        <div className={styles.sidebarTitle}>
          <span style={{ fontSize: '1.5rem' }}>⚙️</span> Settings
        </div>
        <div className={styles.sidebarTitle} style={{ color: 'white', textShadow: 'none', marginTop: '10px' }}>
          <span style={{ fontSize: '1.5rem' }}>🎯</span> Filters
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Genre</label>
          <select className={styles.selectBox} value={genre} onChange={(e) => setGenre(e.target.value)}>
            <option>Choose an option</option>
            <option>Action</option>
            <option>Sci-Fi</option>
            <option>Drama</option>
            <option>Comedy</option>
            <option>All</option>
          </select>
        </div>

        <div className={styles.sliderContainer}>
          <label className={styles.filterLabel}>Release Year</label>
          <div className={styles.sliderLabels}>
            <span>1950</span><span>2024</span>
          </div>
          <input type="range" min="1950" max="2024" value={minYear} onChange={(e) => setMinYear(Number(e.target.value))} className={styles.slider} />
          <div className={styles.sliderLabels} style={{ marginTop: '2px' }}>
            <span>{minYear}</span><span>2024</span>
          </div>
        </div>

        <div className={styles.sliderContainer}>
          <label className={styles.filterLabel}>Minimum Rating</label>
          <div className={styles.sliderLabels}>
            <span>0.00</span><span>10</span>
          </div>
          <input type="range" min="0" max="10" step="0.1" value={minRating} onChange={(e) => setMinRating(Number(e.target.value))} className={`${styles.slider} ${styles.yellowThumb}`} />
          <div className={styles.sliderLabels} style={{ marginTop: '2px' }}>
            <span>{minRating.toFixed(2)}</span>
          </div>
        </div>

        <div className={styles.filterGroup}>
          <label className={styles.filterLabel}>Content Type</label>
          <select className={styles.selectBox} value={contentType} onChange={(e) => setContentType(e.target.value)}>
            <option>All</option>
            <option>Movies</option>
            <option>TV Shows</option>
          </select>
        </div>

        <button className={styles.resetBtn}>RESET Filters</button>
      </aside>

      {/* Main Content */}
      <main className={styles.main}>
        {/* Header */}
        <header className={`${styles.header} glass-panel`}>
          <div className={styles.iconGroup}>
            <div className={styles.iconBtn}>🎙️</div>
            <div className={styles.iconBtn}>🔍</div>
            <div className={styles.iconBtn}>↗️</div>
          </div>
          <h1 className={styles.title}>AI Movie Recommender</h1>
          <div className={styles.iconGroup}>
            <div className={styles.iconBtn}>💡</div>
            <div className={styles.iconBtn}>🏦</div>
            <div className={styles.iconBtn}>📝</div>
          </div>
        </header>

        {/* Chat Region */}
        <div className={`${styles.chatRegion} glass-panel`}>
          {/* Avatar side image removed */}

          <div className={styles.contentZ}>
            {/* Avatar & Greeting (Only show if no messages yet) */}
            {messages.length === 0 && (
              <div className={styles.avatarSection}>
                <div className={styles.avatarRing} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '3rem' }}>
                  🤖
                </div>
                <div className={styles.greetingBox}>
                  <p><b>Hello!</b> Let's find the perfect movie for you.</p>
                  <p>What are you in the mood for?</p>
                </div>
              </div>
            )}

            {/* Mood Buttons (Only show if no messages yet) */}
            {messages.length === 0 && (
              <div className={styles.moodRow}>
                {moods.map(m => (
                  <button
                    key={m.label}
                    className={styles.moodBtn}
                    style={{ borderColor: mood === m.label ? m.color : 'var(--glass-border)', boxShadow: mood === m.label ? `0 0 10px ${m.color}` : 'none' }}
                    onClick={() => setMood(m.label)}
                  >
                    {m.emoji} {m.label}
                  </button>
                ))}
              </div>
            )}

            {/* Chat History */}
            <div className={styles.chatHistory}>
              {messages.map((msg, idx) => (
                <div key={idx} className={msg.type === 'user' ? styles.userMessage : styles.aiMessage}>
                  {msg.type === 'user' ? (
                    <div className={styles.userBubble}>{msg.content}</div>
                  ) : (
                    <div className={styles.aiBubble}>
                      <div className={styles.markdownContent}>
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>

                      {/* Dynamic Recommended Movie Cards */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className={styles.resultsArea} style={{ marginTop: '20px' }}>
                          <h3 style={{ color: 'var(--text-muted)' }}>Source Material</h3>
                          <div className={styles.moviesCarousel}>
                            {msg.sources.map((src, sIdx) => (
                              <div key={sIdx} className={styles.movieCard}>
                                <img
                                  src={src.poster_path || "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=220&h=300"}
                                  alt={src.title}
                                  style={{ borderRadius: '8px', height: '180px', objectFit: 'cover' }}
                                  onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=220&h=300"; }}
                                />
                                <h3 className={styles.movieTitle}>{src.title}</h3>
                                <div className={styles.movieMeta}>
                                  <span>{src.year || "N/A"}</span>
                                  {src.rating && (
                                    <span className={styles.movieRating}>★ {src.rating}</span>
                                  )}
                                  <span style={{ background: '#ffcc00', color: 'black', padding: '2px 6px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>TMDB</span>
                                </div>
                                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '5px 0', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                                  {src.overview || src.description || "A recommended movie based on your prompt."}
                                </p>
                                <button className={styles.playBtn}>▶ View Details <span>+</span></button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}

              {/* Loading Indicator */}
              {loading && (
                <div className={styles.aiMessage}>
                  <div className={styles.aiBubble} style={{ display: 'inline-block', width: 'auto', animation: 'pulse 1.5s infinite', border: '1px solid var(--neon-purple)' }}>
                    <span style={{ fontSize: '1.2rem', color: 'var(--neon-blue)', fontWeight: 'bold' }}>
                      ✨ {loadingMessages[loadingMessageIndex]}
                    </span>
                  </div>
                </div>
              )}

              {/* Invisible div to scroll to */}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Bar */}
            <div className={`${styles.inputContainer} ${isListening ? styles.listeningActive : ''}`}>
              <button
                className={styles.micBtn}
                onClick={toggleListening}
                style={{
                  color: isListening ? 'var(--neon-purple)' : 'var(--text-muted)',
                  animation: isListening ? 'pulse 1.5s infinite' : 'none'
                }}
                title="Click to speak"
              >
                🎙️
              </button>
              <input
                type="text"
                className={styles.textInput}
                placeholder={isListening ? "Listening..." : "Ask me anything..."}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              />
              <button className={styles.submitBtn} onClick={handleSend} disabled={loading || !prompt.trim()}>
                {loading ? '...' : '→'}
              </button>
            </div>


          </div>
        </div>
      </main>
    </div>
  );
}
