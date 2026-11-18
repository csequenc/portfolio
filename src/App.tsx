import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  House, FolderKanban, FileText, ScanSearch, MessageCircle, Mail,
  X, Maximize2, Minimize2, ArrowUpRight, Github, Linkedin, Copy,
  Download, Send, Check, ChevronRight, FileSearch
} from 'lucide-react';
import projects from './content/projects.json';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

type AppId = 'welcome' | 'projects' | 'resume' | 'matcher' | 'ask' | 'contact';
type ChatMessage = { role: 'user' | 'assistant'; content: string; sources?: string[] };

type MatchItem = {
  skill?: string;
  requirement?: string;
  status?: 'strong' | 'partial' | 'missing' | string;
  importance?: string;
  resume_evidence?: string;
  evidence?: string;
  explanation?: string;
  gap?: string;
  relevant_projects?: string[];
  [key: string]: unknown;
};

type JDMatchResult = {
  skill_score: number;
  score_label: string;
  score_rationale: string;
  technical_matches: MatchItem[];
  education_matches: MatchItem[];
  experience_matches: MatchItem[];
  overall_assessment: string;
};

const apps: { id: AppId; label: string; icon: typeof House; hint: string }[] = [
  { id: 'welcome', label: 'Welcome', icon: House, hint: 'A quick introduction' },
  { id: 'projects', label: 'Projects', icon: FolderKanban, hint: 'Selected work' },
  { id: 'resume', label: 'Resume', icon: FileText, hint: 'Experience and education' },
  { id: 'matcher', label: 'JD Matcher', icon: ScanSearch, hint: 'Compare a role with my profile' },
  { id: 'ask', label: 'Ask Ishaan', icon: MessageCircle, hint: 'Ask about my work' },
  { id: 'contact', label: 'Contact', icon: Mail, hint: 'Get in touch' },
];

const initialChat: ChatMessage[] = [{
  role: 'assistant',
  content: "Hi. I can answer questions about the projects, tools, methods, and details documented in Ishaan's portfolio. I won't guess beyond that information."
}];

function getInitialChat(): ChatMessage[] {
  try {
    const saved = sessionStorage.getItem('ishaan-portfolio-chat');
    return saved ? JSON.parse(saved) as ChatMessage[] : initialChat;
  } catch {
    return initialChat;
  }
}

function Welcome({ open }: { open: (id: AppId) => void }) {
  return <div className="welcome-page">
    <div className="welcome-copy">
      <div className="eyebrow"><span className="status-dot" /> OPEN TO SELECT OPPORTUNITIES</div>
      <h1>Ishaan<br /><span>Maheshwari.</span></h1>
      <p className="welcome-role">Applied AI Engineering <i>·</i> Computer Science</p>
      <p className="welcome-intro">I build intelligent systems and study how they behave — from retrieval and persistent memory to language-model fine-tuning and evaluation.</p>
      <div className="welcome-actions">
        <button className="primary-action" onClick={() => open('projects')}>Explore selected work <ArrowUpRight size={15} /></button>
        <button className="text-action" onClick={() => open('resume')}>View resume <ChevronRight size={14} /></button>
      </div>
    </div>
    <div className="welcome-bottom"><span>BASED IN INDIA</span><span>SCROLL LESS. BUILD MORE.</span><span>PORTFOLIO / 2026</span></div>
  </div>;
}

function Projects() {
  const [selected, setSelected] = useState<string>(projects[0].id);
  const active = projects.find((p) => p.id === selected) ?? projects[0];

  return <div className="projects-layout">
    <div className="section-intro">
      <div className="eyebrow">01 / SELECTED WORK</div>
      <h2>Projects<span className="period">.</span></h2>
      <p>Systems, experiments, and the reasoning behind them.</p>
    </div>
    <div className="projects-content">
      <div className="project-list" role="tablist" aria-label="Projects">
        {projects.map((p, i) => <button
          key={p.id}
          className={`project-tab ${selected === p.id ? 'selected' : ''}`}
          onClick={() => setSelected(p.id)}
          role="tab"
          aria-selected={selected === p.id}
        >
          <span className="project-index">0{i + 1}</span>
          <span className="project-tab-copy"><strong>{p.title}</strong><small>{p.subtitle}</small></span>
          <ChevronRight size={16} />
        </button>)}
      </div>
      <AnimatePresence mode="wait">
        <motion.article
          key={active.id}
          className="project-detail"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: .18 }}
        >
          <div className="detail-top">
            <span className="eyebrow">{active.status}</span>
            <span className="detail-counter">{String(projects.findIndex(p => p.id === active.id) + 1).padStart(2, '0')} / 03</span>
          </div>
          <h3>{active.title}</h3>
          <p className="detail-subtitle">{active.subtitle}</p>
          <p className="detail-summary">{active.summary}</p>
          <div className="detail-rule" />
          <div className="eyebrow detail-label">WHAT I BUILT</div>
          <ul className="achievement-list">{active.bullets.map((b) => <li key={b}>{b}</li>)}</ul>
          <div className="eyebrow detail-label">TECHNOLOGIES</div>
          <div className="tag-list">{active.stack.map((s) => <span key={s}>{s}</span>)}</div>
          <a className="inline-link" href={active.github} target="_blank" rel="noreferrer">View repository <ArrowUpRight size={14} /></a>
        </motion.article>
      </AnimatePresence>
    </div>
  </div>;
}

function Resume() {
  return <div className="resume-page">
    <div className="section-intro resume-heading">
      <div className="eyebrow">02 / DOCUMENT</div>
      <h2>Resume<span className="period">.</span></h2>
      <p>Education, selected projects, and technical focus.</p>
    </div>
    <div className="resume-toolbar">
      <span><FileText size={15} /> Ishaan_Maheshwari_Resume.pdf</span>
      <a href="/resume.pdf" download="Ishaan_Maheshwari_Resume.pdf"><Download size={15} /> Download PDF</a>
    </div>
    <div className="resume-frame">
      <iframe src="/resume.pdf#toolbar=0&navpanes=0" title="Ishaan Maheshwari resume" />
    </div>
  </div>;
}

function getStatus(item: MatchItem): string {
  return String(item.status ?? 'unknown').toLowerCase();
}

function getItemName(item: MatchItem): string {
  return String(item.skill ?? item.requirement ?? 'Requirement');
}

function getItemEvidence(item: MatchItem): string {
  const evidence = item.resume_evidence ?? item.evidence ?? item.explanation;
  return typeof evidence === 'string' ? evidence : '';
}

function JDMatcher() {
  const [jd, setJd] = useState('');
  const [result, setResult] = useState<JDMatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyze = async () => {
    if (jd.trim().length < 50 || loading) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/jd-match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_description: jd.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'The analysis could not be completed.');
      }

      setResult(data as JDMatchResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not connect to the matcher API.');
    } finally {
      setLoading(false);
    }
  };

  const technical = result?.technical_matches ?? [];
  const strong = technical.filter(item => getStatus(item) === 'strong');
  const partial = technical.filter(item => getStatus(item) === 'partial');
  const missing = technical.filter(item => getStatus(item) === 'missing');

  const gaps = [...partial, ...missing].slice(0, 4);

  const education = result?.education_matches ?? [];
  const experience = result?.experience_matches ?? [];

  const educationStatus = education[0] ? getStatus(education[0]) : 'unknown';
  const experienceStatus = experience[0] ? getStatus(experience[0]) : 'unknown';

  return <div className="matcher-page">
    <div className="section-intro">
      <div className="eyebrow">03 / ROLE ANALYSIS</div>
      <h2>JD Matcher<span className="period">.</span></h2>
      <p>Compare a job description with the experience documented in my resume.</p>
    </div>

    <div className="matcher-grid">
      <div className="matcher-input">
        <label htmlFor="jd">JOB DESCRIPTION</label>
        <textarea
          id="jd"
          value={jd}
          maxLength={12000}
          onChange={(e) => {
            setJd(e.target.value);
            setResult(null);
            setError('');
          }}
          placeholder="Paste the role requirements here…"
        />
        <div className="matcher-actions">
          <span>{jd.length.toLocaleString()} / 12,000 characters</span>
          <button
            className="primary-action"
            onClick={analyze}
            disabled={jd.trim().length < 50 || loading}
          >
            {loading ? 'Analyzing…' : 'Analyze role'}
            {!loading && <ArrowUpRight size={14} />}
          </button>
        </div>
        {error && <p className="matcher-error">{error}</p>}
      </div>

      <div className="matcher-output">
        {loading ? (
          <div className="matcher-empty">
            <span className="chat-loading">…</span>
            <strong>Analyzing the role.</strong>
            <p>Extracting requirements and comparing them with the documented profile.</p>
          </div>
        ) : result ? (
          <div className="jd-results">
            <div className="eyebrow">TECHNICAL SKILL MATCH</div>

            <div className="jd-score">
              <strong>{result.skill_score}<small>%</small></strong>
              <span>{result.score_label || 'Technical Skill Match'}</span>
            </div>

            <p className="jd-score-rationale">{result.score_rationale}</p>

            <div className="jd-stats">
              <div>
                <strong>{strong.length}</strong>
                <span>Strong</span>
              </div>
              <div>
                <strong>{partial.length}</strong>
                <span>Partial</span>
              </div>
              <div>
                <strong>{missing.length}</strong>
                <span>Missing</span>
              </div>
            </div>

            {gaps.length > 0 && <div className="jd-gaps">
              <div className="eyebrow">AREAS TO LOOK AT</div>
              {gaps.map((item, index) => (
                <div className="jd-gap-item" key={`${getItemName(item)}-${index}`}>
                  <span>{getItemName(item)}</span>
                  <small className={`jd-status ${getStatus(item)}`}>{getStatus(item)}</small>
                </div>
              ))}
            </div>}

            <div className="jd-education">
              <div>
                <span>Education</span>
                <strong className={`jd-status ${educationStatus}`}>{educationStatus}</strong>
              </div>
              <div>
                <span>Experience</span>
                <strong className={`jd-status ${experienceStatus}`}>{experienceStatus}</strong>
              </div>
            </div>

            <details className="jd-breakdown">
              <summary>View detailed assessment <ChevronRight size={14} /></summary>

              <div className="jd-detail-list">
                <h4>Technical requirements</h4>
                {technical.map((item, index) => (
                  <div className="jd-detail-item" key={`${getItemName(item)}-${index}`}>
                    <div className="jd-detail-heading">
                      <strong>{getItemName(item)}</strong>
                      <span className={`jd-status ${getStatus(item)}`}>{getStatus(item)}</span>
                    </div>
                    {getItemEvidence(item) && <p>{getItemEvidence(item)}</p>}
                    {typeof item.gap === 'string' && item.gap && <p>{item.gap}</p>}
                    {Array.isArray(item.relevant_projects) && item.relevant_projects.length > 0 && (
                      <small>Projects: {item.relevant_projects.join(', ')}</small>
                    )}
                  </div>
                ))}

                {education.length > 0 && <>
                  <h4>Education</h4>
                  {education.map((item, index) => (
                    <div className="jd-detail-item" key={`education-${index}`}>
                      <div className="jd-detail-heading">
                        <strong>{getItemName(item)}</strong>
                        <span className={`jd-status ${getStatus(item)}`}>{getStatus(item)}</span>
                      </div>
                      {getItemEvidence(item) && <p>{getItemEvidence(item)}</p>}
                    </div>
                  ))}
                </>}

                {experience.length > 0 && <>
                  <h4>Experience</h4>
                  {experience.map((item, index) => (
                    <div className="jd-detail-item" key={`experience-${index}`}>
                      <div className="jd-detail-heading">
                        <strong>{getItemName(item)}</strong>
                        <span className={`jd-status ${getStatus(item)}`}>{getStatus(item)}</span>
                      </div>
                      {getItemEvidence(item) && <p>{getItemEvidence(item)}</p>}
                    </div>
                  ))}
                </>}
              </div>
            </details>
          </div>
        ) : (
          <div className="matcher-empty">
            <FileSearch size={23} />
            <strong>Your assessment will appear here.</strong>
            <p>Paste a job description and analyze it to see the technical match, key gaps, and qualification assessment.</p>
          </div>
        )}
      </div>
    </div>

    <p className="disclaimer">
      The score reflects technical skill alignment only. It is not a hiring probability or an overall suitability score.
    </p>
  </div>;
}

function AskIshaan() {
  const [messages, setMessages] = useState<ChatMessage[]>(getInitialChat);
  const [question, setQuestion] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    try {
      sessionStorage.setItem('ishaan-portfolio-chat', JSON.stringify(messages));
    } catch {
      /* storage may be unavailable */
    }
  }, [messages]);

  const send = async () => {
    const q = question.trim();
    if (!q || busy) return;

    setQuestion('');
    setBusy(true);

    const userMessage: ChatMessage = { role: 'user', content: q };
    setMessages((current) => [...current, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: q,
          history: messages.slice(-8).map(({ role, content }) => ({ role, content })),
        }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || 'The assistant is temporarily unavailable.');

      setMessages((current) => [
        ...current,
        { role: 'assistant', content: data.answer, sources: data.sources ?? [] },
      ]);
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : 'Could not reach the assistant. Please try again.';

      setMessages((current) => [
        ...current,
        { role: 'assistant', content: `${message} If this continues, the portfolio API may be offline.` },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setMessages(initialChat);
    try {
      sessionStorage.removeItem('ishaan-portfolio-chat');
    } catch {
      /* ignore */
    }
  };

  return <div className="ask-page">
    <div className="section-intro">
      <div className="eyebrow">04 / PROJECT KNOWLEDGE</div>
      <h2>Ask Ishaan<span className="period">.</span></h2>
      <p>A constrained assistant for the work documented here.</p>
    </div>

    <div className="chat-shell">
      <div className="chat-top">
        <div><span className="live-indicator" /> PORTFOLIO KNOWLEDGE BASE <small>AI ASSISTANT</small></div>
        <button onClick={reset}>Clear session</button>
      </div>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={`${i}-${m.role}`} className={`chat-message ${m.role}`}>
            <div className="chat-avatar">{m.role === 'assistant' ? 'I.' : 'YOU'}</div>
            <div className="chat-bubble">
              <p>{m.content}</p>
              {m.sources && <div className="source-cites">
                {m.sources.map(s => <span key={s}>SOURCE / {s}</span>)}
              </div>}
            </div>
          </div>
        ))}

        <div className="chat-suggestions">
          <span>TRY ASKING</span>
          {['What is MemoryMesh?', 'How was LoRA compared with DoRA?', 'What tools are in the RAG system?'].map(q => (
            <button key={q} onClick={() => setQuestion(q)}>{q}<ArrowUpRight size={12} /></button>
          ))}
        </div>
      </div>

      <form className="chat-compose" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about projects, methods, or technologies…"
        />
        <button type="submit" disabled={!question.trim() || busy} aria-label="Send question">
          {busy ? <span className="chat-loading">…</span> : <Send size={16} />}
        </button>
      </form>
    </div>

    <p className="disclaimer">
      Answers are generated by an AI model using curated portfolio information. The assistant is instructed not to invent details outside that context.
    </p>
  </div>;
}

function Contact() {
  const [copied, setCopied] = useState(false);
  const email = 'ishaan.maheshwari.07@gmail.com';

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(email);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      window.location.href = `mailto:${email}`;
    }
  };

  return <div className="contact-page">
    <div className="section-intro">
      <div className="eyebrow">05 / CONNECTION</div>
      <h2>Contact<span className="period">.</span></h2>
      <p>For internships, collaboration, or a thoughtful technical conversation.</p>
    </div>

    <div className="contact-main">
      <div className="contact-headline">Have something<br />interesting in mind<span className="period">?</span></div>
      <p className="contact-note">I'm interested in applied AI engineering, building useful systems, and evaluating how models behave in practice.</p>

      <button className="email-copy" onClick={copy}>
        <span><small>EMAIL</small><strong>{email}</strong></span>
        {copied ? <Check size={18} /> : <Copy size={18} />}
      </button>

      <div className="social-links">
        <a href="https://github.com/csequenc" target="_blank" rel="noreferrer"><Github size={17} /> GitHub <ArrowUpRight size={13} /></a>
        <a href="https://linkedin.com/in/maheshwari-ishaan" target="_blank" rel="noreferrer"><Linkedin size={17} /> LinkedIn <ArrowUpRight size={13} /></a>
        <a href="mailto:ishaan.maheshwari.07@gmail.com"><Mail size={17} /> Email <ArrowUpRight size={13} /></a>
      </div>
    </div>

    <div className="contact-footer">
      <span>ISHAAN MAHESHWARI / INDIA</span>
      <span>THANKS FOR STOPPING BY.</span>
    </div>
  </div>;
}

function AppContent({ id, open }: { id: AppId; open: (id: AppId) => void }) {
  switch (id) {
    case 'welcome': return <Welcome open={open} />;
    case 'projects': return <Projects />;
    case 'resume': return <Resume />;
    case 'matcher': return <JDMatcher />;
    case 'ask': return <AskIshaan />;
    case 'contact': return <Contact />;
  }
}

export default function App() {
  const [active, setActive] = useState<AppId | null>('welcome');
  const [maximized, setMaximized] = useState(false);
  const activeApp = useMemo(() => apps.find(a => a.id === active), [active]);

  const open = (id: AppId) => {
    setActive(id);
    setMaximized(false);
  };

  const close = () => {
    setActive(null);
    setMaximized(false);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (active) close();
      }

      if (e.altKey && e.key === 'ArrowRight') {
        const index = apps.findIndex(a => a.id === active);
        open(apps[(index + 1 + apps.length) % apps.length].id);
      }
    };

    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [active]);

  return <div className="desktop-shell">
    <div className="wallpaper-grain" />

    <div className="ambient-dots" aria-hidden="true">
      {Array.from({ length: 32 }, (_, i) => (
        <span
          key={i}
          style={{
            left: `${(i * 37 + 11) % 100}%`,
            top: `${(i * 53 + 7) % 100}%`,
            animationDelay: `${(i % 9) * -1.7}s`,
            opacity: .12 + (i % 4) * .055,
          }}
        />
      ))}
    </div>

    <aside className="sidebar">
      <button className="brand-mark" onClick={() => open('welcome')} aria-label="Open welcome">
        <span>I</span><i>.</i>
      </button>

      <div className="side-divider" />

      <nav className="app-nav" aria-label="Portfolio applications">
        {apps.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`nav-icon ${active === id ? 'active' : ''}`}
            onClick={() => open(id)}
            aria-label={label}
            title={label}
          >
            <Icon size={19} strokeWidth={1.55} />
            {active === id && <span className="active-indicator" />}
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <span className="side-version">V.01</span>
        <span className="side-mark">●</span>
      </div>
    </aside>

    <main className="desktop-area">
      <div className="desktop-meta">
        <span>IM PORTFOLIO <i>/</i> 01</span>
        <span>COMPUTER SCIENCE <i>·</i> APPLIED AI</span>
      </div>

      <AnimatePresence mode="wait">
        {active && activeApp && (
          <motion.section
            key={active}
            className={`app-window ${maximized ? 'maximized' : ''} app-${active}`}
            initial={{ opacity: 0, y: 12, scale: .985 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: .99 }}
            transition={{ duration: .22, ease: 'easeOut' }}
          >
            <header className="window-bar">
              <div className="window-app-name">
                <span className="window-app-glyph">
                  {active === 'welcome' ? <span className="mini-logo">I.</span> : activeApp.label.slice(0, 1)}
                </span>
                <span>{activeApp.label}</span>
              </div>

              <div className="window-controls">
                <button
                  onClick={() => setMaximized(v => !v)}
                  aria-label={maximized ? 'Restore window' : 'Maximize window'}
                  title={maximized ? 'Restore' : 'Maximize'}
                >
                  {maximized ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                </button>
                <button className="close-window" onClick={close} aria-label="Close window" title="Close">
                  <X size={16} />
                </button>
              </div>
            </header>

            <div className="window-content">
              <AppContent id={active} open={open} />
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {!active && (
        <motion.div className="empty-desktop" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="empty-mark">I.</div>
          <p>DESKTOP / IDLE</p>
          <span>Select an application from the sidebar.</span>
        </motion.div>
      )}

      <footer className="desktop-footer">
        <span>© 2026 ISHAAN MAHESHWARI</span>
        <span>DESIGNED WITH INTENTION.</span>
      </footer>
    </main>

    <nav className="mobile-nav" aria-label="Applications">
      {apps.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => open(id)}
          className={active === id ? 'active' : ''}
          aria-label={label}
        >
          <Icon size={19} />
        </button>
      ))}
    </nav>
  </div>;
}