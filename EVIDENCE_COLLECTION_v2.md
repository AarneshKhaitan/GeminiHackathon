# Evidence Collection — Hypothesis Elimination Engine (v2)

## Context

Building an iterative hypothesis elimination engine for Gemini 3 hackathon (March 7, 2026). Full architecture is in `hypothesis_elimination_engine_architecture.md` in this project. Teammates handling frontend + agent orchestration. My job: assemble evidence packages for two events.

## The Key Constraint: This Must Not Be Rigged

The demo only works if the evidence package is **realistic, not curated**. That means:

1. **Include counter-evidence.** Reassuring analyst notes, regulatory support statements, management denials, positive market signals. If a real analyst would have seen it that week, it goes in. The system's job is to reason through contradiction, not to process a clean narrative.

2. **Include noise.** Not every article that week was about the crisis. There were earnings from other companies, macro data releases, unrelated geopolitical news. Some of this should be in the mix — the system needs to demonstrate that it can focus on what matters.

3. **Include evidence that supports the WRONG hypothesis.** The SNB saying "CS meets capital requirements" is evidence for "this is fine." The system needs to process that and correctly identify that the existence of the reassurance is itself a stress signal. That's the demo's most powerful moment.

4. **Don't over-curate the volume.** In reality, a risk desk sees 10-15 headlines per second across all names. We can't replicate that, but the evidence should feel like a *slice of the firehose*, not a carefully arranged museum exhibit. Err on the side of too much rather than too little.

## What We're NOT Doing

- NOT targeting a specific token count. Just collect what's real. We'll trim later if needed.
- NOT pre-assigning evidence to cycles. The system should request what it needs. We just need the evidence available when it asks.
- NOT restricting to "important" articles only. Include the forgettable stuff too.

## Two Evidence Categories

**STRUCTURAL (permanent system properties — the crown jewels):**
Things that were true before the crisis, during, and after. Contract terms. Regulatory powers. Market mechanics. Legal frameworks. These don't change with time — they tell you what CAN happen. They enable forward simulation.

**EMPIRICAL (timestamped observations):**
Everything else. News, prices, quotes, filings, social media, interviews. These tell you what IS happening. They include signal, noise, contradiction, and misdirection — all mixed together, just like reality.

---

## EVENT 1: CREDIT SUISSE (March 2023)

**Timeline:** The acute crisis runs March 9-19, 2023. But the backstory matters — CS had been deteriorating for years (Archegos, Greensill, money laundering, leadership churn). And the immediate trigger context is SVB failing on March 10.

**Ground truth:** UBS forced acquisition at CHF 0.76/share. CHF 16B AT1 bonds written to zero (unprecedented — equity survived, bonds didn't). FINMA invoked emergency ordinance.

### STRUCTURAL EVIDENCE

These are the documents that define what's structurally possible. They exist independently of the crisis. A system that reads them BEFORE the crisis can simulate outcomes that a system without them cannot.

**1. AT1 Bond Prospectus — PONV Clause**
- What: The actual contractual terms of CS's Additional Tier 1 bonds. Specifically the "Point of Non-Viability" clause that allows full write-down if FINMA determines non-viability.
- Why it matters: This is the single most important structural observation. Most analysts assumed bondholders would be senior to equity (normal hierarchy). The PONV clause inverts this. A system that reads this document can predict the AT1 wipeout; a system without it cannot.
- Where to find: CS investor relations archive, SEC EDGAR (CS filed under Credit Suisse Group AG), or the specific prospectus supplements for the AT1 issuances.
- What to extract: The PONV trigger language, the write-down mechanics, any reference to FINMA's role in determining non-viability. Don't need the full prospectus — the relevant sections on loss absorption and write-down.

**2. FINMA Emergency Powers**
- What: The legal authority FINMA has under Swiss law to intervene in a failing bank. Specifically the emergency ordinance power that allows them to bypass normal insolvency proceedings.
- Where to find: FINMA website (finma.ch), Swiss Federal Act on Banks and Savings Banks (Banking Act), or the "too big to fail" provisions. Also: FINMA's own published resolution framework documents.
- What to extract: What powers does FINMA have? Can they write down AT1s? Can they force a merger? Can they override shareholder approval? The answers to these questions define the space of possible outcomes.

**3. Swiss "Too Big To Fail" Legislation**
- What: The regulatory framework specifically designed for systemically important Swiss banks (CS and UBS).
- Where to find: fedlex.admin.ch (Swiss federal law database), or FINMA publications summarizing the framework.
- What to extract: Resolution paths for a G-SIB under Swiss law. What happens if a systemically important bank fails? What tools are available?
- Note: May be in German/French. English summaries from FINMA or academic papers are fine.

**4. Saudi Banking Regulations — Ownership Cap**
- What: Saudi Arabian Monetary Authority (SAMA) regulations that cap single-entity ownership of a bank. The Saudi National Bank was already at 9.9% of CS.
- Why it matters: This is a structural constraint that makes "Saudi rescue via increased stake" impossible. It eliminates a hypothesis.
- Where to find: News articles explaining the regulatory constraint are sufficient — we don't need the actual SAMA rulebook. Multiple articles from March 15 explain this.

**5. CS Capital Structure**
- What: How CS's balance sheet was structured — total capital, CET1 ratio, AT1 bonds as percentage of total capital, leverage ratio.
- Where to find: CS 2022 Annual Report (investor relations), Q4 2022 earnings press release.
- What to extract: The capital stack. How much of CS's regulatory capital was AT1 bonds? What were the minimum requirements? How close were they to breaching?

**6. SNB Emergency Liquidity Facility Terms**
- What: The terms under which the Swiss National Bank provided CHF 54B in emergency lending on March 16.
- Where to find: SNB press release from March 15-16, 2023.
- Why structural: The terms and conditions of central bank support define what liquidity support can and cannot solve. If the facility is collateralized, it doesn't fix a solvency hole.

**7. G-SIB Designation and Systemic Importance**
- What: CS's designation as a Global Systemically Important Bank, what that means for resolution, additional capital buffers required.
- Where to find: Financial Stability Board (FSB) G-SIB list, BIS publications on G-SIB framework.

### EMPIRICAL EVIDENCE — THE FULL PICTURE (signal + noise + counter-signal)

**Pre-crisis context (2021-Feb 2023):**
- [ ] Archegos collapse losses (~$5.5B, March 2021) — news articles
- [ ] Greensill Capital scandal — news articles
- [ ] CS leadership churn — multiple CEO/chairman changes
- [ ] Q4 2022 earnings (Feb 9, 2023) — CHF 110B deposit outflow disclosed
- [ ] CS share price decline through 2022 — from ~CHF 8 to ~CHF 3
- [ ] CS restructuring plan announcements
- [ ] ANY positive CS coverage from this period — analyst upgrades, restructuring optimism, "turnaround story" narratives. These exist and they matter.

**SVB trigger week (March 8-12):**
- [ ] SVB failure news (March 8-10)
- [ ] European bank sector selloff — ALL European bank stocks down, not just CS
- [ ] Analyst notes saying "European banks are different from US regionals" — COUNTER-EVIDENCE, and many analysts said exactly this
- [ ] CS stock price movements (daily or intraday if available)
- [ ] CDS spread levels — quoted in news articles from this period
- [ ] General market commentary about banking contagion fears
- [ ] Signature Bank failure (March 12)
- [ ] Regulatory statements from ECB, Fed, BoE about banking system stability — COUNTER-EVIDENCE

**Acute CS crisis (March 13-17):**
- [ ] Saudi National Bank chairman Bloomberg TV interview (March 15) — VIDEO CLIP FROM YOUTUBE. This is the most important single piece of multimodal evidence. His words are factually true and reasonable. The market reaction is catastrophic. You need both the video and the stock price to see why.
- [ ] CS stock price on March 15 — 30% intraday drop
- [ ] SNB/FINMA joint statement saying CS "meets capital and liquidity requirements imposed on systemically important banks" (March 15) — COUNTER-EVIDENCE. The regulators are explicitly saying it's fine. The system needs to process this and understand that the statement itself is a stress signal.
- [ ] CS draws CHF 54B from SNB facility (March 16) — this looks reassuring on the surface (system is working, central bank stepping in). The elimination engine should recognize the SIZE of the draw as evidence of severity.
- [ ] News articles with analyst quotes defending CS — "CS is not SVB", "European banks have better regulation", etc. COUNTER-EVIDENCE.
- [ ] News articles with analyst quotes attacking CS — "CS has been a walking dead bank for years"
- [ ] CDS spread movements through the week
- [ ] AT1 bond prices through the week (if available from news/blogs)
- [ ] General European market performance (to separate CS-specific from sector)

**Resolution (March 18-19):**
- [ ] Weekend negotiations reporting (Saturday-Sunday March 18-19)
- [ ] UBS merger announcement at CHF 0.76/share
- [ ] AT1 write-down announcement — CHF 16B to zero
- [ ] FINMA emergency ordinance text
- [ ] Bondholder reactions — outrage at hierarchy inversion
- [ ] Swiss Finance Minister Keller-Sutter press conference — VIDEO if available on YouTube
- [ ] UBS CEO statements
- [ ] Market reaction on Monday March 20

**Post-resolution (useful for validation):**
- [ ] Legal challenges from AT1 bondholders
- [ ] Other regulators (ECB, BoE) immediately clarifying that THEIR AT1 bonds follow normal hierarchy — showing how unusual the Swiss decision was
- [ ] Analysis articles explaining what happened and why

### MULTIMODAL EVIDENCE (CS)

- [ ] Saudi chairman Bloomberg TV clip — YouTube URL + transcript
- [ ] Keller-Sutter press conference — YouTube URL + transcript  
- [ ] CS CEO statements (video if available)
- [ ] CS stock price chart (TradingView screenshot or generate)
- [ ] European banks index overlay for comparison
- [ ] CDS spread chart (reconstruct from data points in articles)

---

## EVENT 2: FTX COLLAPSE (November 2-11, 2022)

**Timeline:** CoinDesk article leaks Alameda balance sheet Nov 2. CZ tweets about selling FTT Nov 6. Bank run begins Nov 7. FTX halts withdrawals Nov 8. Binance acquisition announced then withdrawn Nov 8-9. Chapter 11 filed Nov 11.

**Ground truth:** SBF convicted on 7 counts of fraud. ~$8B customer funds misappropriated via Alameda Research. FTX was insolvent.

### STRUCTURAL EVIDENCE

**1. FTT Token Mechanics**
- What: How the FTT token worked — burn mechanics, utility, supply distribution. Critically: what percentage of FTT supply was held by FTX/Alameda.
- Why it matters: FTT as collateral is circular — the token's value depends on FTX's health, so using it as collateral to back FTX creates a reflexive death spiral. This is a structural property, not an empirical observation.
- Where to find: FTX documentation (web archive), crypto analysis blogs (Messari, The Block research), Nansen or similar on-chain analysis reports.

**2. Alameda Balance Sheet (as leaked)**
- What: The CoinDesk-reported Alameda balance sheet showing $14.6B in assets, of which $5.8B was FTT and $3.37B was "unlocked SOL." Also significant: $8B in a mysterious "loans" line item.
- Why structural: The composition of the balance sheet is a permanent property. Once you know it, you can simulate: "if FTT drops 50%, what happens to Alameda's solvency?" The answer is mathematical.
- Where to find: CoinDesk article from November 2, 2022 (public). Also widely reproduced in other outlets.

**3. FTX Terms of Service — Customer Fund Handling**
- What: What FTX's ToS actually said about customer deposits. Were they segregated? Could FTX lend them?
- Why it matters: If the ToS doesn't guarantee segregation, the structural possibility of commingling exists from day one.
- Where to find: Web archive (Wayback Machine) of FTX.com terms of service.

**4. Bahamas Regulatory Framework**
- What: The Securities Commission of The Bahamas' regulatory powers and framework for crypto exchanges.
- Why structural: Defines what resolution/intervention tools exist. Very different from what SEC or CFTC could do.
- Where to find: News articles about Bahamas regulation of FTX, SCB statements during the crisis.

**5. Binance-FTX Relationship History**
- What: Binance was an early FTX investor, received FTT tokens as part of their exit. This is a structural fact — Binance held a large FTT position.
- Where to find: News articles, CZ's own tweets/blogs explaining the history.

### EMPIRICAL EVIDENCE — FULL PICTURE

**Pre-crisis context:**
- [ ] SBF's public image — congressional testimony, magazine covers, political donations, "effective altruism" branding
- [ ] Positive coverage of FTX — "the adult in the room", regulatory engagement, Bahamas HQ as legitimacy signal
- [ ] SBF interviews where he's confident, articulate, trustworthy — VIDEO from YouTube. These are COUNTER-EVIDENCE and they matter. The pre-crisis SBF persona is part of why nobody saw it coming.
- [ ] FTX stadium deal, celebrity endorsements, Super Bowl ads — signals of institutional legitimacy
- [ ] Any skeptical pre-crisis coverage (some existed but was minority)

**The leak and CZ's move (Nov 2-6):**
- [ ] CoinDesk article (Nov 2) — the actual article, not a summary of it
- [ ] Initial reactions — some dismissive ("Alameda's balance sheet doesn't mean FTX is insolvent"), some alarmed. Include BOTH.
- [ ] CZ tweet announcing Binance will sell its FTT holdings (Nov 6) — archived tweet
- [ ] FTT price reaction
- [ ] Alameda CEO Caroline Ellison offering to buy CZ's FTT at $22 — this is COUNTER-EVIDENCE (suggests they have liquidity to buy)
- [ ] SBF's public responses — calm, measured, "assets are fine"
- [ ] Crypto Twitter debate — was CZ being predatory? Was FTX actually fine?
- [ ] General crypto market movements (separate FTT from BTC/ETH)

**The bank run (Nov 7-8):**
- [ ] FTX withdrawal volumes — reported in real-time by on-chain watchers
- [ ] FTT price collapse
- [ ] SBF tweets "FTX is fine. Assets are fine." — CRITICAL CROSS-MODAL MOMENT. Get the actual tweet.
- [ ] On-chain data showing massive outflows from FTX wallets — this directly contradicts SBF's statement
- [ ] SBF Twitter Spaces appearance (Nov 8) — AUDIO/TRANSCRIPT from YouTube recordings. His tone is composed while the blockchain shows insolvency in real time.
- [ ] Binance announces acquisition/LOI (Nov 8) — initially looks like rescue. COUNTER-EVIDENCE.
- [ ] Crypto market relief rally on Binance acquisition news — COUNTER-EVIDENCE
- [ ] Other exchange CEOs' statements (Coinbase, Kraken providing proof-of-reserves)

**The collapse (Nov 9-11):**
- [ ] Binance withdraws from acquisition after "due diligence" (Nov 9) — this is a massive signal. Binance looked at the books and walked.
- [ ] SBF's continued public statements vs reality
- [ ] On-chain: mysterious movement of FTX funds ($600M+ "unauthorized transactions")
- [ ] Chapter 11 filing (Nov 11)
- [ ] John Ray III's statement about worst corporate governance he's ever seen (he also oversaw Enron liquidation)
- [ ] Customer reactions, crypto market crash

**Post-collapse (for validation):**
- [ ] Criminal charges against SBF
- [ ] Trial testimony revealing commingling details
- [ ] FTX bankruptcy recovery proceedings
- [ ] Regulatory responses (SEC, CFTC actions)

### MULTIMODAL EVIDENCE (FTX)

- [ ] SBF Twitter Spaces audio (Nov 8) — YouTube URL + transcript
- [ ] Pre-crisis SBF interviews (confident, trustworthy persona) — YouTube URLs
- [ ] CZ tweets (screenshots or archived text)
- [ ] SBF "assets are fine" tweet
- [ ] FTT price chart (CoinGecko/TradingView)
- [ ] BTC/ETH overlay to separate FTT-specific from market
- [ ] On-chain flow visualizations if available from crypto analytics

---

## How to Find This Stuff

**For news articles:** Search Reuters, BBC, FT (some free), Bloomberg (some free), CoinDesk (free), The Block (some free), Ars Technica, Swiss outlets (SWI swissinfo.ch in English). For each article, grab the full text.

**For structural docs:** SEC EDGAR for prospectuses, FINMA.ch for Swiss regulatory docs, Web Archive for FTX terms, crypto project documentation sites.

**For video/audio:** YouTube search for the specific moments. Bloomberg TV clips, CNBC clips, SBF interviews are all on YouTube.

**For price data:** Yahoo Finance (CSV download) for stocks. CoinGecko (CSV download) for crypto. CDS spreads won't have downloadable data — compile from levels quoted in articles.

**For tweets:** Check web archive, tweet archive sites, or news articles that embed/screenshot the tweets.

**For on-chain data:** Etherscan for Ethereum transactions, blockchain.com for Bitcoin. Crypto analytics blogs often have the visualizations already made.

---

## Priority Order (it's late, hackathon is tomorrow)

**Do first — structural docs (irreplaceable, unique to our system):**
1. AT1 prospectus PONV clause
2. FINMA emergency powers
3. CoinDesk Alameda balance sheet article
4. FTT token mechanics explainer

**Do second — the cross-modal money shots:**
1. Saudi chairman Bloomberg TV clip + stock price data for that day
2. SBF "assets are fine" tweet + on-chain outflow data for same timestamp
3. SBF Twitter Spaces recording

**Do third — timeline news articles:**
1. 15-20 articles per event, including counter-evidence
2. Don't just grab the "collapse" articles — grab the "it's fine" articles too

**Do fourth — price data and charts:**
1. CS stock CSV from Yahoo Finance
2. FTT price CSV from CoinGecko
3. Comparison indices (European banks, BTC)

**Do last — nice to have:**
1. Full earnings transcripts
2. Post-crisis analysis pieces
3. Legal challenge documents

---

## When Collecting Each Piece, Note:

- **STRUCTURAL or EMPIRICAL?**
- **Pro-collapse or counter-evidence?** (We need both. Roughly 60/40 split — more crisis signal than counter, but enough counter to make the demo honest.)
- **What hypothesis does it speak to?** (Even a rough tag: "supports H2", "contradicts H3", "ambiguous")
- **Source URL** (so we can re-fetch if needed)

Let's go.
