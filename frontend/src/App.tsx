import { AnimatePresence, motion } from 'framer-motion'
import { AppShell } from './components/layout/AppShell'
import { SignalIntakeScreen } from './components/screens/Screen1_SignalIntake/SignalIntakeScreen'
import { InvestigationScreen } from './components/screens/Screen2_Investigation/InvestigationScreen'
import { ConvergenceScreen } from './components/screens/Screen3_Convergence/ConvergenceScreen'
import { useStore } from './store'

const screenVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -16 },
}

export function App() {
  const activeScreen = useStore((s) => s.activeScreen)

  return (
    <AppShell>
      <AnimatePresence mode="wait">
        {activeScreen === 0 && (
          <motion.div
            key="screen1"
            variants={screenVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="h-full overflow-hidden"
          >
            <SignalIntakeScreen />
          </motion.div>
        )}

        {activeScreen === 1 && (
          <motion.div
            key="screen2"
            variants={screenVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="h-full overflow-hidden"
          >
            <InvestigationScreen />
          </motion.div>
        )}

        {activeScreen === 2 && (
          <motion.div
            key="screen3"
            variants={screenVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className="h-full overflow-hidden"
          >
            <ConvergenceScreen />
          </motion.div>
        )}
      </AnimatePresence>
    </AppShell>
  )
}
