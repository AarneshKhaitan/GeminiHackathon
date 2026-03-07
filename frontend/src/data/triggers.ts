import type { TriggerEvent } from '../types/api'

export const TRIGGERS: TriggerEvent[] = [
  {
    id: 'TRIGGER_SVB_001',
    entity: 'Silicon Valley Bank',
    ticker: 'SIVB',
    event: 'After-hours stock collapse of 60.41% following capital raise announcement',
    date: '2023-03-08',
    magnitudeSigma: 4.2,
    description: 'SIVB collapsed 60.41% after hours after announcing a $1.75B capital raise, signaling balance sheet stress.',
  },
  {
    id: 'TRIGGER_CS_001',
    entity: 'Credit Suisse',
    ticker: 'CS',
    event: 'CDS spreads widened 300bps; major shareholder refuses additional capital injection',
    date: '2023-03-15',
    magnitudeSigma: 3.8,
    description: 'Credit Suisse CDS surged to crisis levels after largest shareholder ruled out additional capital.',
  },
  {
    id: 'TRIGGER_FRC_001',
    entity: 'First Republic Bank',
    ticker: 'FRC',
    event: 'Stock suspended after 97% decline; emergency liquidity injection from major banks',
    date: '2023-04-28',
    magnitudeSigma: 5.1,
    description: 'FRC suspended trading after collapse. 11 major banks injected $30B in deposits failed to stem run.',
  },
]
