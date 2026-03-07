import type { TriggerEvent } from '../types/api'

export const TRIGGERS: TriggerEvent[] = [
  {
    id: 'TRIGGER_CS_001',
    entity: 'Credit Suisse',
    ticker: 'CS',
    event: 'Q4 2022 earnings reveal CHF 110.5 billion deposit outflows',
    date: '2023-02-09',
    magnitudeSigma: 4.5,
    description: 'Credit Suisse reported CHF 110.5B in deposit outflows (8% of AUM) in Q4 2022, signaling massive confidence crisis.',
  },
]
