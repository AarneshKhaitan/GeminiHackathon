import { motion } from 'framer-motion'
import { useStore } from '../../../store'

const lines = [
  { text: 'Every risk system today does the same thing.', delay: 0 },
  { text: 'Data in. Summary out. Single pass. One shot.', delay: 1.5 },
  {
    text: 'Detecting that something is wrong is a solved problem.',
    delay: 3.5,
  },
  {
    text: 'ML models, statistical signals, anomaly detection — these work.',
    delay: 4.5,
  },
  { text: 'The hard problem is what comes next.', delay: 7, highlight: true },
  {
    text: 'When evidence contradicts itself. When context grows across cycles.',
    delay: 8.5,
  },
  { text: 'When you need to reason, not summarize.', delay: 9.5 },
]

const TITLE_DELAY = 11.5
const TAGLINE_DELAY = 12.5
const BUTTON_DELAY = 13.5

export function ColdOpenScreen() {
  const setActiveScreen = useStore((s) => s.setActiveScreen)

  return (
    <div
      className="h-full flex flex-col items-center justify-center p-10"
      style={{ backgroundColor: '#0C0A07' }}
    >
      <div className="max-w-2xl space-y-2">
        {/* Staggered narrative lines */}
        {lines.map(({ text, delay, highlight }) => (
          <motion.p
            key={text}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.6, ease: 'easeOut' }}
            className={`font-mono leading-relaxed ${highlight ? 'text-[15px]' : 'text-[13px]'}`}
            style={{ color: highlight ? '#EDE4D4' : '#A89575' }}
          >
            {text}
          </motion.p>
        ))}

        {/* Title block */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: TITLE_DELAY, duration: 0.6 }}
          className="pt-10"
        >
          <div
            className="tracking-[0.35em] mb-3"
            style={{
              fontFamily: 'Syne, sans-serif',
              fontWeight: 700,
              fontSize: '11px',
              color: '#5A4D3A',
            }}
          >
            ITERATIVE HYPOTHESIS ELIMINATION ENGINE
          </div>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: TAGLINE_DELAY, duration: 0.6, ease: 'easeOut' }}
          style={{
            fontFamily: 'Syne, sans-serif',
            fontWeight: 800,
            fontSize: '1.5rem',
            color: '#EDE4D4',
          }}
        >
          This system doesn't summarize. It investigates.
        </motion.p>

        {/* CTA button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: BUTTON_DELAY, duration: 0.5 }}
          className="pt-8"
        >
          <button
            onClick={() => setActiveScreen(0)}
            className="text-[10px] font-mono tracking-wider px-5 py-2.5 transition-colors"
            style={{
              border: '1px solid #2E2820',
              backgroundColor: '#161310',
              color: '#C8912A',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#C8912A'
              e.currentTarget.style.backgroundColor = '#2D1E07'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#2E2820'
              e.currentTarget.style.backgroundColor = '#161310'
            }}
          >
            BEGIN INVESTIGATION →
          </button>
        </motion.div>
      </div>
    </div>
  )
}
