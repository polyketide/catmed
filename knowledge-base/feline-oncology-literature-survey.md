# Feline Oncology: A Panoramic Survey of Recent Literature (veterinary knowledge base)

> Generated 2026-07-17 · Multi-agent parallel search (PubMed/Consensus) + consolidation by the controller · 8 domains covered
> **Discipline**: every entry carries a real PMID/DOI; 【established/solid】 is distinguished from 【emerging/unproven】; cross-species citations are labelled (canine/human, extrapolated). Recent 5 years prioritised.
> Purpose: a systematic overview of feline oncology as a whole. Operational decisions for a specific case should combine the topic-specific knowledge bases with the attending veterinarian's judgement.

---

## ⭐ Distilled points most relevant to a head-and-neck (nasopharynx to larynx) mass

- **Primary laryngeal/tracheal lymphoma** is mostly B-cell and low-to-intermediate grade; with surgery ± chemotherapy, **median PFS and OS were both 909 days** (Rodriguez-Piza 2023, PMID 36655881) — the most closely applicable optimistic figure for this site, if the lesion is lymphoma.
- **SBRT for nasal/nasopharyngeal lymphoma**: median OS 365 days, with **single-fraction equivalent to multi-fraction**; **cribriform plate lysis (MST 121 vs 876 days) and intracalvarial involvement (100 vs 438 days) are strong negative prognostic factors** (Reczynska 2022, PMID 35188694) — a case with skull-base osteolysis belongs to the group requiring caution.
- **Definitive-intent radiotherapy for nasal carcinoma gave median OS 721 vs 284 days for palliative intent; a second course at recurrence gave 824 vs 434 days** (Yoshikawa 2021, PMID 33660305) — so if the lesion is a carcinoma, radiotherapy still operates on a scale of months to two years, not "weeks".
- **Diagnosis**: for ICC, **cell blocks outperform stained cytology slides** (immunophenotyping was inconclusive in 19% of cell blocks vs 54% of stained slides, Sampaio 2023); PARR must be **multi-target** (a single target misses nearly half of B-cell cases, Rout 2019); **clonality-positive ≠ neoplasia** (70% of LPE cases also showed monoclonality, Freiche 2021).
- **Serum TK1** is the strongest blood-based lymphoma marker in cats (AUC 0.98) and can serve as a **non-invasive diagnostic adjunct and treatment-monitoring tool** (Wang 2021, PMID 34579716).
- **Prognosis**: **BCS <5 gives median survival 3.3 vs 16.7 months for BCS ≥5** (Baez 2007); **anaemia lowers the L-asparaginase response rate (57% vs 15%)** (Inazumi 2024); **achieving CR is the strongest positive factor**.
- **Palliative / end-of-life**: the first **cat-specific AAFP/IAAHPC hospice and palliative care guidelines** appeared in 2023 (PMID 37768060), establishing the "budgets of care / care unit" framework; **93% of cat owners were willing to trade survival time for quality of life** (Reynolds 2010); the FGS pain scale is reliably usable by owners.

---

## 1. Early detection and screening

**Where things stand**: cats have **no** clinically validated blood-based early-detection tool suitable for population screening; diagnosis is still "find a mass → cytology/histopathology + imaging".

- **Serum TK1/TK** is the blood tumour marker with the strongest evidence, but it is essentially **specific to lymphoma**: AUC 0.98, sensitivity 0.83, specificity 0.95; it distinguishes lymphoma from IBD/inflammation and falls with treatment response (Wang 2021, PMID 34579716; Taylor 2013, PMID 23076596). Its role is diagnostic adjunct + response monitoring, not screening.
- **α1-acid glycoprotein (AGP)** is a non-specific tumour/response marker (median 832.60 µg/mL at lymphoma diagnosis vs 269.85 in healthy cats, *P* < 0.001, returning to control-comparable values by 12 weeks of treatment; Winkel 2015, PMID 26512544); SAA has low sensitivity.
  ⚠️ **Verified from the full text 2026-07-20, and the full text undercuts the screening reading of it.** The two distributions overlap almost entirely — lymphoma 50.00–2,825.40 µg/mL against control undetectable–536.20 — so **a single AGP value cannot classify an individual cat**, and a low result excludes nothing. What the data support is the *within-patient* use: a fall from that cat's own diagnostic value tracking treatment response. 16 lymphoma cats vs 25 controls, and the controls were much younger (median 3.0 vs 9.0 years), so age is not separated from disease here.
- **Structured screening of older cats** is the most realistic form of "early detection" currently available: a 2-year cohort of 259 apparently healthy cats found **21% were already diseased at baseline**, with a **2-year cumulative incidence of new neoplasia of roughly 7%** (Mortier 2024, PMID 38967102); the **2021 AAFP Senior Care Guidelines** include neoplasia in the minimum database (PMID 34167339).
- **Mammary tumours** have a high malignancy rate and progress quickly; early palpation and early excision (<3 cm) markedly improve prognosis.
- **【emerging/unproven】**: feline cfDNA-NGS liquid biopsy is proof-of-concept only (2 lymphomas + 9 controls, Ruiz-Perez 2024, PMID 39346958); **circulating nucleosome Nu.Q has canine data only** (canine, extrapolated); there is no multi-cancer early-detection (MCED) product validated in cats.
  ⚠️ **The Nu.Q clause carries no citation, found 2026-07-20.** The sentence cites Ruiz-Perez 2024 (PMID 39346958) for the cfDNA half; the Nu.Q half names no source, and Ruiz-Perez's abstract does not discuss Nu.Q. **This is an unsourced claim, and it is the awkward kind — a negative one.** "Canine data only" asserts an absence in the feline literature, which is exactly the class of statement this repository requires a documented search for rather than an assumption (see `emergency-triage-red-flags.md`, where open-mouth breathing is recorded as searched-for-and-not-found rather than simply absent). Until that search is run and recorded, treat the clause as **unverified**, not as an established gap.

## 2. Advances in diagnostic technique

**Where things stand**: the most active area of the past 5 years is distinguishing **low-grade intestinal T-cell lymphoma (LGITL) from lymphoplasmacytic enteritis (LPE)**; **histopathology remains the gold standard**.

- **2023 ACVIM consensus** (Marsilio, PMID 37130034): **no single clonality assay or marker reliably distinguishes neoplasia from inflammation**; clinical, imaging, histological, IHC and PARR findings must be integrated.
- **PARR upgraded to multi-target multiplex PCR**: using four immunoglobulin primer sets in combination, clonal rearrangements were detected in 87% (33/38) of presumed B-cell neoplasms, whereas the IGH-VDJ reaction alone detected clonality in only 50% (19/38) (Rout 2019, PMID 31478220); the assay is **highly specific but only moderately sensitive — a negative result does not exclude lymphoma**. Primer standardisation work recommends dropping Kde (Weyrich 2024, PMID 38774911).
- **⚠️ The trap: clonality-positive ≠ neoplasia** — 70% of LPE cases also featured monoclonality (40%) or monoclonality on a polyclonal background (30%) (Freiche 2021, PMID 34374109). **Ki-67 (20% threshold in the epithelium, 30% in the lamina propria; specificity >95% for each) and pSTAT5** serve as LGITL markers.
- **⭐ Cell size does not predict survival here; the cytotoxic phenotype's *location* does.** In 50 endoscopically sampled feline intestinal T-cell lymphomas, **"No significant differences in survival time were found based on cell size or epitheliotropism"** — but cases with TIA1+ and/or granzyme B+ neoplastic lymphocytes **predominantly in the mucosal epithelium had significantly shorter survival (P < .05)** (Ii 2022, PMID 36052863). Granzyme B positivity itself split sharply by cell size (LCL 6/14 = 43%, SCL 2/36 = 6%), yet it was *where* those cells sat that carried the prognosis. ⚠️ Context for how much is at stake: the same paper cites previous work putting median survival at roughly 1.5 months for LCL versus 28 months for SCL — so a marker that re-sorts prognosis independently of cell size is not a refinement, it is a different answer. Endoscopic samples only; transmural spread could not be assessed.
- **New IHC markers**: intestinal T-cell lymphoma should add **granzyme B/TIA1**. Without immunohistochemical labelling of granzyme B, cytotoxic status would have been missed in **85% (11/13) of histopathological slides and 46% (6/13) of cytological slides** (Wolfesberger 2024, PMID 38943798); intraepithelial cytotoxic lymphocytes carry a poor prognosis (Ii 2022, PMID 36052863).
- **Cell blocks > stained slides for ICC**: immunophenotyping was inconclusive in 54% of stained cytology slides versus 19% of cell blocks (Sampaio 2023, PMID 36851461); **a pleural-effusion cell pellet can substitute for a biopsy when running PARR**.
- **【emerging】**: TRBC1/2 RNA in situ hybridisation (canine/feline proof-of-concept), AI-based lymphocyte quantification, standardisation of feline flow cytometry — all proof-of-concept; **validation of feline-specific NGS/liquid-biopsy diagnostics is a conspicuous gap**.

## 3. Feline lymphoma: treatment and prognosis

**Where things stand**: grade and subtype determine strategy; **achieving complete remission (CR) is the strongest positive prognostic factor in almost every study**; prospective RCTs are lacking.

> **⭐ The single largest prognostic divide in feline lymphoma, from three independent series — none of which states the comparison.**
>
> | Form | Median overall survival | Source |
> |---|---|---|
> | **Small-cell** alimentary | **1317 days** (~3.6 years) | Pope 2015, PMID 29067174 (56 cats) |
> | **Large-cell** gastrointestinal | **150 days** | Inazumi 2024, PMID 38825481 (43 cats) |
> | **Intermediate-to-large-cell**, CMOP/CHOP | **103 / 80 days** | Lai 2025, PMID 40443182 (123 cats) |
>
> **Roughly an order of magnitude, turning on cell size.** Inazumi's own literature review puts previously reported survival for large-cell gastrointestinal lymphoma at **65–157 days**, which brackets all three large-cell figures above and makes the convergence unlikely to be chance.
>
> ⚠️ Different populations, protocols, countries and eras; these are not head-to-head comparisons and the medians should not be subtracted from one another. What survives every one of those caveats is the **magnitude** of the gap — which is why cell size determines what an owner is actually deciding about, and why `feline-oncology-literature-survey.md` treats the small-cell/large-cell split as the first question rather than a refinement. ⚠️ Note also that Ii 2022 (§ above) found cell size *not* predictive within intestinal T-cell lymphoma once epithelial cytotoxic phenotype was accounted for — the divide is robust across broad forms, not a law within every subtype.

- **Low-grade / small-cell alimentary form** (mostly T-cell, indolent): oral **chlorambucil + prednisolone** carries the best prognosis — CR 76%, median remission 18.9 months (Lingard 2009); in a series of 56 cats, ORR 85.7%, median PFS 1078 days and median OS 1317 days, with re-induction still effective at relapse after discontinuation (Pope 2015, PMID 29067174).
- **High-grade / intermediate-to-large-cell form**: multi-agent COP/CHOP, but overall median survival is usually only **3–7 months**. **⭐ The most recent direct comparison puts it lower**: in 123 cats across three referral hospitals, response rate was **66% in both arms**, median progression-free interval **69 days (CMOP) vs 59 days (CHOP)**, and **median survival 103 vs 80 days** (Lai 2025, PMID 40443182). ⚠️ Referral caseload and retrospective, so this is not a population estimate — but it is the number an owner is deciding against, and roughly three months is a very different proposition from "3–7 months" read optimistically. **Alternatives to CHOP**: CMOP (mitoxantrone replacing doxorubicin, giving bolus administration without extravasation risk; 123 cats, the two arms equivalent — response rates 66% in both, median PFI 69 vs 59 days, median ST 103 vs 80 days; Lai 2025, PMID 40443182) and COVP (adding vinblastine; CR 59%, median OS 412 days, with lower GI toxicity; Lee 2025, PMID 40119555).
- **Primary laryngeal/tracheal (PLTL)**: mostly B-cell, low-to-intermediate grade, **median PFS and OS both 909 days** (Rodriguez-Piza 2023, PMID 36655881) ★ relevant to head-and-neck cases.
- **Nasal / nasopharyngeal form**: radiotherapy-led; **adding chemotherapy early after radiotherapy in localised disease** outperformed radiotherapy alone (PFS 677 vs 104, OS 983 vs 263; Goto 2022); SBRT gave median OS 365 days (Reczynska 2022).
- **Immunophenotype and prognosis**: in high-grade alimentary disease, **B-cell outperforms T-cell (PFS 220 vs 42 days)** (Moore 2023, VAPC, PMID 38152842).
- **Salvage**: no standard protocol; single-agent lomustine or a multi-agent backbone (LOMAC ORR 46%, Smallwood 2020; LOPH in FeLV+ cats, OS 214 days, Horta 2020).
- **【emerging】**: novel immunotherapies, targeted agents and monoclonals in feline lymphoma are all at an early or developmental stage; BTK inhibitor data are human (extrapolated).

## 4. Other common solid tumours

- **Mammary carcinoma**: **radical mastectomy plus histological staging** is the core of treatment; prognosis rests on **tumour >2 cm, histological grade (MMEE), lymphovascular invasion (LVI), and pathological nodal stage** (Mills 2019; Dagher 2019, PMID 31113336); **adjuvant chemotherapy (doxorubicin or metronomic cyclophosphamide) has not shown a survival benefit** (Petrucci 2020, PMID 33140523) — do not promise one. Stage IV prognosis is weeks to months. Progesterone-receptor positivity is favourable.
  - **⭐ Surviving the first year does not buy a cat what it buys a dog.** In one cohort of 344 dogs and 342 cats with surgically removed stage I–III invasive mammary carcinoma, the 1-year conditional specific survival was **59% (dogs) vs 48% (cats) at diagnosis** — but among those that had already survived a year, it rose to **80% in dogs and only 52% in cats** (Chocteau 2021, PMID 32954630). The authors' reading: 1-year surviving dogs "were relatively protected from cancer-related death, whereas feline MCs remained life-threatening cancers for longer periods of time."
    **Why this belongs in a feline file rather than a comparative one.** Conditional survival is what an owner is actually asking when they say "she's made it a year, is she through the worst of it?" In dogs the honest answer shifts substantially; **in cats it barely moves — 48% to 52%.** Reassurance built on the canine pattern, or on general oncology intuition that surviving early means surviving, does not transfer. ⚠️ Mixed-species cohort; the 59%/80% figures are the dog comparison, quoted here only to show the size of the divergence. Surgically resected stage I–III only — not applicable to stage IV.
- **Oral squamous cell carcinoma (FOSCC)**: **the worst prognosis of these (1-year survival <10%)**; where resectable, surgery, with margins the decisive factor (Iwata 2025); where unresectable, radiotherapy prolongs survival but **accelerated protocols carry ~30% grade 3 acute toxicity** (Marconato 2019); bone invasion can be treated with radiotherapy plus zoledronate; toceranib gives limited benefit only in the lingual subgroup.
- **Feline injection-site sarcoma (FISS)**: **achieving clean margins with a wide/radical excision at the first surgery** is the single most important controllable factor; where margins are dirty, add radiotherapy (finely fractionated outperformed coarsely fractionated, PFI 1430 vs 540 days, Rossi 2019) or electrochemotherapy; roughly 10–25% develop pulmonary metastasis.
- **Nasal planum / cutaneous SCC**: early-stage (T1/T2) disease is curable by surgery, electrochemotherapy or brachytherapy; ECT also achieves a high response rate in locally advanced disease (21 cats with T3/T4, ORR 100%, Ferrer-Jorda 2024); sun protection for white cats is primary prevention.
- **Mast cell tumour**: the cutaneous form is mostly benign and usually cured by surgery; **the first grading scheme** appeared recently (Sabattini 2019); **the splenic (visceral) form has a good prognosis after splenectomy ± chemotherapy (median 856 days)** (Evans 2018); toceranib gave clinical benefit in 80% across anatomical forms (Berger 2018).

## 5. Advances in radiotherapy

- **Nasal tumours (lymphoma and carcinoma alike) are the setting where feline radiotherapy has the strongest evidence and the best results**: definitive-intent irradiation (fractionated 10 × 4.2–4.8 Gy, or stereotactic) commonly gives median survival >1 year, clearly outperforming palliative intent.
- **SBRT/SRT**: completed in 3–5 fractions, fewer anaesthetic episodes, mild acute toxicity; **the price is late osteonecrosis/fistula**. The starkest warning comes from the FLASH trial, which was **prematurely interrupted because maxillary bone necrosis occurred 9 to 15 months after radiotherapy in 3 of 7 cats treated with FLASH (43%), versus 0 of 9 treated with standard of care** (Rohrer Bley 2022, PMID 35421221; note this trial was in **nasal planum SCC**, arm 1 SoC 10 × 4.8 Gy vs arm 2 1 × 30 Gy FLASH).
- **Reirradiation** can serve as salvage at recurrence, with longer overall survival (562 vs 258 days, Ueno 2026); but a short interval combined with osteolysis predisposes to grade 3 fistula/osteonecrosis. ★ Risk is higher where osteolysis is already present.
- **Acute toxicity**: in-field mucositis/dermatitis, alopecia, conjunctivitis (mostly VRTOG grade 1–2 and self-limiting). **Late**: leukotrichia and pigment change (mild); osteonecrosis/fistula (severe).
- **Nasal lymphoma achieves good local control with radiotherapy, but roughly one third progress systemically before long** — full systemic staging and a chemotherapy decision are needed; prophylactic regional nodal irradiation is effective.
- **【emerging】**: BNCT, low-dose whole-abdominal irradiation, tracheal and pancreatic SBRT case reports — exploratory.

## 6. Targeted therapy and immunotherapy (see the dedicated file, *Feline Lymphoma: Targeted and Immunotherapy Evidence*)

- **Toceranib is the only targeted agent with real clinical efficacy data in cats** (off-label): clinical benefit ~80% in mast cell tumour > ~55–65% in oral SCC and mammary carcinoma > ~45% in pancreatic carcinoma; dosing ~2.5–2.8 mg/kg three times weekly or every other day; low nephrotoxicity (Williams 2024), and it can be combined safely with low-dose meloxicam.
- **Immunotherapy in cats remains almost entirely at the 【target expression / in vitro construction】 stage**: anti-feline PD-1 (Nishibori 2023/2025), anti-feline PD-L1, feline CAR-T (Cockey 2024, first constructed but in vitro only), anti-HER2 monoclonals — **as of 2025 there has been no checkpoint or CAR-T clinical trial in any feline tumour**.
- The only modality actually administered to cats is an **autologous whole-cell tumour vaccine** (Torigen) — safety data only (117 cats, 5.1% adverse events); efficacy unproven.
- **The reason**: the high cost of developing species-specific antibodies plus a small market; cats trail dogs by one step. It is not that "the science cannot be done" (see §4 of the dedicated file).

## 7. Prognostic factors and survival (across tumour types)

- **Treatment response (CR > PR > SD > PD)** is the strongest and the one modifiable factor (in lymphoma, CR 341 days vs PR 78 vs no response 45; Moore 2023).
- **Body condition BCS <5**: median survival 3.3 vs 16.7 months (Baez 2007, PMID 17451991). In the general cat population, BCS is associated with lifespan at both extremes — against a reference of BCS 6, hazard of death rose at BCS 3 (HR 4.67), 4 (HR 2.61) and 9 (HR 1.80), with median lifespan 15.8 years across 2609 cats in Sydney primary practice (Teng 2018, PMID 29393723). ✅ `2609` verified 2026-07-20 against the archived record.
- **⚠️ These two papers were chained in one sentence for months, and they do not share a scale.** The disagreement is on the number the sentence leaned hardest on:
  | | Baez 2007 | Teng 2018 |
  |---|---|---|
  | Population | 57 referral **cancer** cats | 2609 **primary-practice** cats |
  | Outcome | survival from cancer diagnosis | all-cause survival and lifespan |
  | Exposure | BCS at evaluation | **maximum** BCS across all visits |
  | Where 5 sits | **favourable group** (≥5, MST 16.7 mo) | **elevated hazard** (HR 1.43 vs reference 6) |

  **So "BCS 5" is the good group in one and a worse-than-reference group in the other.** Neither is wrong — they are different populations answering different questions — but the figures must not be read along one axis, and a recommendation cannot be assembled by taking the threshold from one and the hazard from the other.
  ⚠️ **Teng's use of *maximum* BCS is a deliberate defence, and it changes who the thin cats are.** Taking each cat's highest recorded score prevents terminal weight loss from being counted as a cause of the death it accompanied. The consequence is that Teng's low-BCS cats **were never in good condition at any visit** — a constitutionally thin group, not Baez's cats who lost condition to disease. The two "thin" categories are not the same animals.
  ⚠️ The published CI for BCS 5 reads "95% CI 11.5-1.76" in both PubMed and PMC — **malformed as printed**; context makes it 1.15-1.76. Quoted verbatim in the excerpt block and flagged rather than silently corrected.
- **⭐ But BCS is prognostic and blind at the same time, and the same paper shows both.** Baez's full text reports that among cats with **BCS ≥5 — the better-prognosis group — 72% (23/32) already had moderate to severe muscle wasting** at one or more site, and 91% of the whole cohort had muscle loss at all three sites assessed. A cat can score "optimal or overweight" and be substantially catabolic underneath.
  **What this changes in practice**: BCS predicts survival, so it is worth recording — but a normal BCS is **not** evidence that wasting has been excluded, and the two must not be collapsed into one reassurance. The muscle-mass score is a separate, cheap, palpation-based assessment (temporal region, scapulae, hind limbs) and it is the one that detects what BCS misses. **Whether to score it, and how to act on it, is the attending veterinarian's call** — the useful owner-side move is to ask whether muscle mass was assessed separately from body condition, not to attempt scoring at home.
  ⚠️ **Limits.** 57 cats, single referral oncology service, 1999–2001, scores assigned subjectively by one investigator and never tested for inter-observer reproducibility. The species contrast the authors draw (93% of cats vs 35% of dogs with muscle wasting) is across two different studies, not a matched comparison. Treat the direction as established and the proportions as approximate.
- **Anaemia**: a consistently adverse prognostic factor across tumour types, which also **lowers the chemotherapy response rate** (L-asparaginase 57% vs 15%, Inazumi 2024).
- **FeLV**: **progressive infection (median survival 30 days; 4–5× increase in hazard of death) must be distinguished from regressive infection (no direct effect)** (Biezus 2025, PMID 40591622).
- **Clinical substage b** (systemic signs present) predicts a worse outcome.
- **【emerging/weak】**: feline-specific evidence for sarcopenia/MCS as an independent prognostic factor in feline cancer remains weak (mostly human/canine extrapolation); a validated cross-tumour prognostic nomogram **does not yet exist**.

## 8. Hospice · palliative care · euthanasia decision-making

- **The first cat-specific AAFP/IAAHPC hospice and palliative care guidelines, 2023** (Eigner 2023, PMID 37768060): **"budgets of care" and "care unit"** plus structured ethical decision-making; emphasises that emotional health matters as much as physical health.
- **QoL takes priority over lifespan**: **93% of owners of cats with heart disease were willing to trade survival time for good QoL, and 57% of those were willing to trade up to 6 months** (Reynolds 2010, PMID 20738770); the key QoL parameters are **appetite, interaction with the owner, sleep, and toileting**.
- **Tiered pain assessment**: for acute pain use the **FGS** (cut-off >0.39, reliably usable by owners; Evangelista 2019 / Monteiro 2023); for chronic OA use the owner-completed FMPI or MI-CAT scales; **frunevetmab (Solensia, an anti-NGF monoclonal)** is an approved monthly injectable analgesic for feline OA.
- **QoL instruments**: CatQoL and VetMetrica-feline are validated; but a systematic review found only 8 of 32 instruments validated (Doit 2021); **HHHHHMM (Villalobos) is widely used but lacks cat-specific validation** (mixed canine/feline — extrapolate with caution).
- **Euthanasia decision-making**: driven both by animal-centred factors (pain, behaviour, decline) and by human-centred ones (needing a veterinarian to validate that the decision was right, normalising death, forecasting the course) (Littlewood 2021); during any period of delay, palliative care maintains welfare; **declining appetite plus non-specific decline is the most common trigger sign**; cost is a real constraint in a sizeable proportion of cases.
- **Grief support**: pet loss can produce grief equivalent to human bereavement and is often socially "disenfranchised"; support and after-care planning should be offered proactively (Cleary 2022; Cooney 2020).

---

## Master list of core literature (by domain, PMID/DOI)

**Screening/diagnosis**: Wang 2021 (34579716, feline TK1); Mortier 2024 (38967102, senior cat screening); Marsilio 2023 (37130034, ACVIM consensus); Rout 2019 (31478220, multi-target PARR); Freiche 2021 (34374109, LGITL/LPE); Sampaio 2023 (36851461, cell block > slide); Ruiz-Perez 2024 (39346958, cfDNA proof-of-concept).
**Lymphoma**: Lingard 2009 (19576832); Pope 2015 (29067174); Rodriguez-Piza 2023 (36655881, laryngeal/tracheal); Lai 2025 (40443182, CMOP); Lee 2025 (40119555, COVP); Moore 2023 (38152842, VAPC / B vs T); Reczynska 2022 (35188694, nasal SBRT); Goto 2022 (36049238); Inazumi 2024 (38825481, L-Asp); Horta 2020 (32684120, LOPH); Smallwood 2020 (33176543, LOMAC salvage).
**Solid tumours/radiotherapy**: Mills 2019 (31788484, mammary staging); Dagher 2019 (31113336, MMEE); Petrucci 2020 (33140523, no benefit from adjuvant mammary chemotherapy); Yoshikawa 2021 (33660305, definitive RT for nasal carcinoma); Marconato 2019 (31756259, oral SCC radiotherapy toxicity); Rossi 2019 (29473768, FISS fractionation); Sabattini 2019 (30244666, mast cell grading); Evans 2018 (28168776, splenic MCT); Rohrer Bley 2022 (35421221, FLASH osteonecrosis); Ueno 2026 (42375287, reirradiation); Ferrer-Jorda 2024 (39073984, ECT).
**Targeted/immunotherapy**: Wiles 2017 (26755491, toceranib FOSCC); Berger 2018 (29172873, toceranib MCT); Del Portillo 2024 (39212426, toceranib mammary); Williams 2024 (39287178, toceranib renal safety); Maekawa 2023 (36701405, PD-L1); Nishibori 2023 (37095139) / 2025 (40974651, anti-feline PD-1); Cockey 2024 (39631169, feline CAR-T in vitro); Lucroy 2021 (34328359, autologous vaccine); Žagar 2023 (37835664, TKI review).
**Prognosis**: Baez 2007 (17451991, BCS); Teng 2018 (29393723, nine-point BCS); Biezus 2025 (40591622, FeLV progressive/regressive); Finotello 2017 (28556532, LGL); Chocteau 2021 (32954630, conditional survival).
**Hospice/palliative**: Eigner 2023 (37768060, AAFP/IAAHPC hospice guidelines); Ray 2021 (34167339, AAFP senior); Evangelista 2019 (31836868, FGS); Monteiro 2023 (36649089, FGS by owners); Gruen 2021 (34724255, frunevetmab); Reynolds 2010 (20738770, QoL > lifespan); Doit 2021 (33941335, review of QoL instruments); Littlewood 2021 (33924569, euthanasia decision-making); Cleary 2022 (33881389, grief).

> The complete per-entry data (key advances / solid data / emerging, in full, for each domain) are archived in the workflow journal; this page is the curated version. All citations come from tool-based searches, with species extrapolation and "unproven" status labelled. For the few entries marked "found via Consensus search", DOIs were not individually verified, as noted.

---

---

---

---

---

## 参考文献（原文记录）

> 本节标题、期刊、卷期页**一律为 PubMed 原文**，不翻译、不缩写。
> 正文中的表述仅为解读；**如需引用，请引用下方原文条目**。
> 非英文文献保留其原始语言标题并标注语种。

- Baez JL, et al. A prospective investigation of the prevalence and prognostic significance of weight loss and changes in body condition in feline cancer patients. *J Feline Med Surg* 2007;9(5):411-7. PMID 17451991. [DOI](https://doi.org/10.1016/j.jfms.2007.02.005)
- Reynolds CA, et al. Perceptions of quality of life and priorities of owners of cats with heart disease. *J Vet Intern Med* 2010;24(6):1421-6. PMID 20738770. [DOI](https://doi.org/10.1111/j.1939-1676.2010.0583.x)
- Taylor SS, et al. Serum thymidine kinase activity in clinically healthy and diseased cats: a potential biomarker for lymphoma. *J Feline Med Surg* 2012;15(2):142-7. PMID 23076596. [DOI](https://doi.org/10.1177/1098612X12463928)
- Winkel VM, et al. Serum α-1 acid glycoprotein and serum amyloid A concentrations in cats receiving antineoplastic treatment for lymphoma. *Am J Vet Res* 2015;76(11):983-8. PMID 26512544. [DOI](https://doi.org/10.2460/ajvr.76.11.983)
- Pope KV, et al. Outcome and toxicity assessment of feline small cell lymphoma: 56 cases (2000-2010). *Vet Med Sci* 2015;1(2):51-62. PMID 29067174. [DOI](https://doi.org/10.1002/vms3.9)
- Dagher E, et al. Feline Invasive Mammary Carcinomas: Prognostic Value of Histological Grading. *Vet Pathol* 2019;56(5):660-670. PMID 31113336. [DOI](https://doi.org/10.1177/0300985819846870)
- Rout ED, et al. Assessment of immunoglobulin heavy chain, immunoglobulin light chain, and T-cell receptor clonality testing in the diagnosis of feline lymphoid neoplasia. *Vet Clin Pathol* 2019;48 Suppl 1:45-58. PMID 31478220. [DOI](https://doi.org/10.1111/vcp.12767)
- Petrucci GN, et al. Adjuvant doxorubicin vs metronomic cyclophosphamide and meloxicam vs surgery alone for cats with mammary carcinomas: A retrospective study of 137 cases. *Vet Comp Oncol* 2020;19(4):714-723. PMID 33140523. [DOI](https://doi.org/10.1111/vco.12660)
- Yoshikawa H, et al. Retrospective evaluation of intranasal carcinomas in cats treated with external-beam radiotherapy: 42 cases. *J Vet Intern Med* 2021;35(2):1018-1030. PMID 33660305. [DOI](https://doi.org/10.1111/jvim.16098)
- Ray M, et al. 2021 AAFP Feline Senior Care Guidelines. *J Feline Med Surg* 2021;23(7):613-638. PMID 34167339. [DOI](https://doi.org/10.1177/1098612X211021538)
- Freiche V, et al. Histopathologic, phenotypic, and molecular criteria to discriminate low-grade intestinal T-cell lymphoma in cats from lymphoplasmacytic enteritis. *J Vet Intern Med* 2021;35(6):2673-2684. PMID 34374109. [DOI](https://doi.org/10.1111/jvim.16231)
- Wang L, et al. Feline thymidine kinase 1: molecular characterization and evaluation of its serum form as a diagnostic biomarker. *BMC Vet Res* 2021;17(1):316. PMID 34579716. [DOI](https://doi.org/10.1186/s12917-021-03030-5)
- Reczynska AI, et al. Outcome of stereotactic body radiation for treatment of nasal and nasopharyngeal lymphoma in 32 cats. *J Vet Intern Med* 2022;36(2):733-742. PMID 35188694. [DOI](https://doi.org/10.1111/jvim.16388)
- Rohrer Bley C, et al. Dose- and Volume-Limiting Late Toxicity of FLASH Radiotherapy in Cats with Squamous Cell Carcinoma of the Nasal Planum and in Mini Pigs. *Clin Cancer Res* 2022;28(17):3814-3823. PMID 35421221. [DOI](https://doi.org/10.1158/1078-0432.CCR-22-0262)
- Ii T, et al. Intraepithelial cytotoxic lymphocytes are associated with a poor prognosis in feline intestinal T-cell lymphoma. *Vet Pathol* 2022;59(6):931-939. PMID 36052863. [DOI](https://doi.org/10.1177/03009858221120010)
- Rodriguez-Piza I, et al. Clinical presentation, treatment and outcome in 23 cats with laryngeal or tracheal lymphoma. *J Feline Med Surg* 2023;25(1):1098612X221143769. PMID 36655881. [DOI](https://doi.org/10.1177/1098612X221143769)
- Sampaio F, et al. Detection of Lymphoid Markers (CD3 and PAX5) for Immunophenotyping in Dogs and Cats: Comparison of Stained Cytology Slides and Matched Cell Blocks. *Vet Sci* 2023;10(2). PMID 36851461. [DOI](https://doi.org/10.3390/vetsci10020157)
- Marsilio S, et al. ACVIM consensus statement guidelines on diagnosing and distinguishing low-grade neoplastic from inflammatory lymphocytic chronic enteropathies in cats. *J Vet Intern Med* 2023;37(3):794-816. PMID 37130034. [DOI](https://doi.org/10.1111/jvim.16690)
- Eigner DR, et al. 2023 AAFP/IAAHPC feline hospice and palliative care guidelines. *J Feline Med Surg* 2023;25(9):1098612X231201683. PMID 37768060. [DOI](https://doi.org/10.1177/1098612X231201683)
- Moore AS, Frimberger AE. Treatment of feline intermediate to high-grade alimentary lymphoma: A retrospective evaluation of 55 cats treated with the VAPC combination chemotherapy protocol (2017-2021). *Vet Comp Oncol* 2023;22(1):106-114. PMID 38152842. [DOI](https://doi.org/10.1111/vco.12958)
- Weyrich A, et al. Comparative analysis of primer sets for the assessment of clonality in feline lymphomas. *Front Vet Sci* 2024;11:1356330. PMID 38774911. [DOI](https://doi.org/10.3389/fvets.2024.1356330)
- Wolfesberger B, et al. Immunophenotype investigation in feline intestinal non-B-cell lymphoma. *J Comp Pathol* 2024;212:20-26. PMID 38943798. [DOI](https://doi.org/10.1016/j.jcpa.2024.05.004)
- Mortier F, et al. Value of repeated health screening in 259 apparently healthy mature adult and senior cats followed for 2 years. *J Vet Intern Med* 2024;38(4):2089-2098. PMID 38967102. [DOI](https://doi.org/10.1111/jvim.17138)
- Ruiz-Perez CA, et al. Proof-of-concept evaluation of next-generation sequencing-based liquid biopsy for non-invasive cancer detection in cats. *Front Vet Sci* 2024;11:1394686. PMID 39346958. [DOI](https://doi.org/10.3389/fvets.2024.1394686)
- Pui Yung Anna L, et al. Use of Cyclophosphamide, Vincristine, Prednisolone and Vinblastine for the Treatment of Large Cell Lymphoma in Cats. *J Vet Intern Med* 2025;39(2):e70066. PMID 40119555. [DOI](https://doi.org/10.1111/jvim.70066)
- Lai NA, et al. Comparison of outcomes in feline intermediate- to large-cell lymphoma treated with CMOP (cyclophosphamide, mitoxantrone, vincristine and prednisolone) instead of CHOP (cyclophosphamide, doxorubicin, vincristine and prednisolone). *J Feline Med Surg* 2025;27(5):1098612X251335635. PMID 40443182. [DOI](https://doi.org/10.1177/1098612X251335635)
- Biezus G, et al. Survival analysis and clinical abnormalities in cats with progressive or regressive feline leukemia virus (FeLV) infection in Brazil. *PLoS One* 2025;20(7):e0322691. PMID 40591622. [DOI](https://doi.org/10.1371/journal.pone.0322691)

---

---

## 原文摘录（source excerpts）

> The sentences below are **verbatim excerpts from the source literature**, untranslated.
> The prose in the body above is my interpretation; **if you need to cite, cite the original sentences here**, and go back to the source to check the context.
> Only sentences carrying specific load-bearing conclusions are excerpted; this is not a full abstract. For the complete context, retrieve the source by PMID/DOI.

**PMID 17451991** · Baez JL 2007
> Feline cancer patients having a BCS <5 had a median survival time (MST) of 3.3 months compared to that of 16.7 months for cats with a BCS of > or = 5 (P=0.008).
> **【Publisher full text retrieved and checked 2026-07-20 — source: publisher PDF】**
> Fifty-seven cats with neoplasia were evaluated.
> Muscle mass was reduced at all three sites assessed in 91% of the cancer patients.
> When cats with BCS of ≥5 were evaluated with respect to muscle mass scores, 72% of cases (23/32) had evidence of moderate to severe muscle wasting at one or more anatomical location (score <2).
> Even the majority cats with a normal or overweight BCS (72%) had evidence of significant muscle wasting at one or more anatomical location.
> Ninety-three percent had some evidence of muscle wasting in the temporal region (score <3).
> Likewise, only 35% of the dogs were found to have evidence of muscle wasting, as opposed to 93% of cases in this investigation.
> Remission status was closely associated with BCS with a mean BCS of cats that were in remission of 5.2 ± 1.7 vs a mean BCS of 3.5 ± 2.2 for cats that were not in remission (P = 0.0014).
> In addition to BCS, only having the diagnosis of SCC was independently associated with survival (hazards ratio = 0.8, P = 0.004 and 6.7, P = 0.001 for BCS and SCC, respectively).
> ⚠️ **ATTRIBUTION CORRECTED, gap moved not closed, 2026-07-20.** The figure `2609` was flagged against this paper and was placed on a full-text retrieval list on that basis. **It is not in this paper and never could have been — Baez enrolled 57 cats.** The body sentence reads "…(Baez 2007, PMID 17451991); on the nine-point scale … (Teng 2018, n=2609)": 2609 is **Teng 2018's** sample size. Teng 2018 (PMID 29393723) had **no excerpt block anywhere in this repository and had never been archived**, which is why `2609` sat unverified — **now fetched, and verified verbatim: "In total, 2609 cats met the selection criteria from 4020 cats screened."** See that paper's own block. `2018` is a citation year. **This was the second instance of the Amini-Sereshki pattern** — see `upper-airway-response-marker-validity.md` under PMID 16675613, and the SOP section on the two halves of a misattribution verdict.
> ⚠️ Body-weight MST is reported but **collapses within lymphoma**: "<3.3 kg was 3.9 months, 6.5 months for cats weighing ≥3.3 kg and ≤5 kg and 19.9 months for cats weighing >5 kg (P = 0.025)", yet "when only the patients with lymphoma were subgrouped … the difference in MST was not significant (P = 0.3)". Body weight is not cited in this file as a prognostic factor for that reason.
> ⚠️ Design limits the authors state: BCS and the fat/muscle scores are **subjective**, scored by a single investigator (consistent, but never tested for inter-observer reproducibility), and the study "was not designed to evaluate whether or not cats were losing weight in the face of adequate nutritional intake" — so cachexia as a syndrome is inferred, not demonstrated.

**PMID 20738770** · Reynolds CA 2010
> Ninety-three percent of owners were willing to trade survival time for good QoL; 57% of these were willing to trade up to 6 months.
> **【PMC full text retrieved and checked】**
> Ninety-three percent of owners were willing to trade survival time for good QoL; 57% of these were willing to trade up to 6 months.
> ⚠️ Check passed. Note: the source spells the figure out as the words "Ninety-three percent", so a purely numeric match would miss it — this is a known source of false positives in my flagging algorithm.

**PMID 23076596** · Taylor SS 2012
> Mean sTK activity for cats with lymphoma was 17.5 U/l (range 1.0-100.0 SD ± 27.4).
> Mean sTK activity for healthy cats was 2.2 U/l (range 0.8-8.4, ± SD 1.7).
> Mean sTK activity for cats with NHPN was 4.2 U/l (range 1.0-45.0, SD ± 8.6).
> Mean sTK activity for the inflammatory group was 3.4 U/l (range 1.0-19.6, SD 3.9).
> ⚠️ Excerpts added 2026-07-20; this block previously held only a flag and no source text. **The ranges overlap heavily** — lymphoma 1.0-100.0 against healthy 0.8-8.4 and non-haematopoietic neoplasia 1.0-45.0 — so like AGP (PMID 26512544), the group separation is real and the individual discrimination is not. The body's framing of TK as "diagnostic adjunct + response monitoring, not screening" is what these numbers support.
> ⚠️ **FALSE POSITIVE, resolved 2026-07-20.** The figures `0.83, 0.95, 0.98` were flagged here. They are the TK1 ROC results of **Wang 2021 (PMID 34579716)**, quoted verbatim and marked "Check passed" in that paper's own excerpt block; the two papers are cited in one body sentence. `2013, 2021` are citation years, not data. Nothing was ever unverified.

**PMID 26512544** · Winkel VM 2015
> **【Publisher full text retrieved and checked 2026-07-20 — source: publisher PDF】**
> Median serum AGP and SAA concentrations were 269.85 µg/mL (range, very low or undetectable to 536.20 µg/mL) and 0.10 µg/mL (range, very low or undetectable to 0.96 µg/mL), respectively.
> Median serum AGP and SAA concentrations were 832.60 µg/mL (range, 50.00 to 2,825.40 µg/mL) and 1.03 µg/mL (range, undetectable to 18.80 µg/mL), respectively.
> Median serum AGP and SAA concentrations were significantly (P < 0.001 and P = 0.003, respectively) higher in cats with lymphoma at the time of diagnosis than in the control group.
> Serum AGP concentration returned to a value comparable with that of the control group by 12 weeks of treatment.
> The first consisted of 25 healthy adult (≥ 1 years old) privately owned cats and was used as a control group.
> The second group consisted of 16 cats with lymphoma undergoing antineoplastic treatment.
> ⚠️ Gap closed 2026-07-20. `270, 832` were flagged unverified and **were a real gap** — the values are 269.85 and 832.60, rounded in the body. Verified verbatim above.
> ⚠️ **The ranges overlap almost completely, and the median comparison conceals it.** Lymphoma AGP spans 50.00–2,825.40 µg/mL; control spans undetectable–536.20. A cat with lymphoma can sit at 50 µg/mL, below the control median. **The group difference is real; the individual test is not discriminating.** Cited in the body accordingly.
> ⚠️ 16 lymphoma cats vs 25 controls, and controls had a median age of 3.0 years against 9.0 for the lymphoma group — the groups differ in age as well as in disease.

**PMID 26755491** · Wiles V 2017
> The overall biological response rate in group 1 was 56.5%.
> Median survival time of toceranib-treated cats was significantly longer at 123 days compared with 45 days in cats not treated with toceranib ( P = 0.01).
> Administration of NSAIDs was also associated with significantly improved survival time ( P = 0.0038) among all cats.

**PMID 28168776** · Evans BJ 2018
> This retrospective study evaluated treatment outcomes in 64 cats with splenic MCT.
> Median tumor specific survival (MTSS) was: 856, 853, 244, 365 days for groups A, B, C, and D, respectively.
> However, comparing cats that had splenectomy (A and B) versus those that did not (C and D), the MTSS was 856 and 342 days, respectively (p=0.008).
> Splenectomy (+/- chemotherapy) significantly prolongs survival in cats with mast cell tumors.

**PMID 28556532** · Finotello R 2018
> One-hundred and 9 cats with newly diagnosed LGL lymphoma that underwent initial staging (including hematology, serum biochemistry, thoracic radiographs and abdominal ultrasound), and followed-up were retrospectively evaluated.
> Median time to progression (MTTP) was 5 days, and median survival time (MST) 21 days.
> MST was significantly shorter in the case of substage b, circulating neoplastic cells, lack of chemotherapy administration, and lack of treatment response.

**PMID 29067174** · Pope KV 2015
> Median overall survival was 1317 days.
> Medical records from 56 cats were evaluated.
> Median progression-free survival was 1078 days.
> ⚠️ **FALSE POSITIVE resolved 2026-07-20.** `76` and `18.9` belong to **Lingard 2009 (PMID 19576832)** — "CR 76%, median remission 18.9 months" — attributed correctly in the body and cited in the same sentence as this paper. Sentence-level attribution filed them here.

**PMID 29172873** · Berger EP 2018
> Results Case data from 50 cats with cutaneous (n = 22), splenic/hepatic (visceral) (n = 10), gastrointestinal (n = 17) or other (n = 1) mast cell neoplasia were received.
> Clinical benefit was seen in 80% (40/50), including 86% (19/22) with cutaneous, 80% (8/10) with visceral and 76% (13/17) with gastrointestinal involvement.
> Conclusions and relevance Toceranib appears to be well tolerated in feline patients with mast cell neoplasia.

**PMID 29393723** · Teng KT 2018
> In total, 2609 cats met the selection criteria from 4020 cats screened.
> The maximum BCS of each cat during the visits was used as the primary exposure variable.
> The median of the maximum BCS was 6 (interquartile range [IQR] 5-7).
> Compared with cats with a maximum BCS of 6, increased hazards of death were observed in cats with a maximum BCS of 3 (hazard ratio [HR] 4.67, 95% confidence interval [CI] 3.00-7.27), 4 (HR 2.61, 95% CI 1.95-3.49), 5 (HR 1.43, 95% CI 11.5-1.76) and 9 (HR 1.80, 95% CI 1.11-2.93).
> Median lifespan was 15.8 (IQR 13.5-17.6) years.
> There are significant associations of nine-point body condition scoring with survival and lifespan, and BCSs <5 and of 9 were found to be negatively associated with both.
> Electronic patient records from a cat-dominant primary practice in metropolitan Sydney, Australia, where the body condition of cats was regularly recorded using a nine-point BCS scale were obtained.
> ⚠️ **Gap closed 2026-07-20 — `2609` verified verbatim.** This paper was cited in the body and in the index line but **had no excerpt block and had never been archived**, so `2609` sat unverified while the flag for it was filed against Baez 2007. See the note under PMID 17451991, and §7c on how the rebuild input let this happen.
> ⚠️ **Typo in the source, reproduced here verbatim as required**: the CI for BCS 5 is printed "95% CI 11.5-1.76" in both the PubMed record and the PMC deposit. Read in context it can only be 1.15-1.76 — an interval whose lower bound exceeds its upper bound and its own point estimate is not an interval. **Do not silently correct it when quoting; state that the published value is malformed.**
> ⚠️ Full text is not retrievable: PMC (PMC11104206) holds the abstract only, and the publisher blocks automated requests. Everything above is abstract-sourced and Leg 1 checks it.

**PMID 29473768** · Rossi F 2019
> Fifty-nine cats were included; 38 underwent a finely fractionated protocol and 21 a coarsely fractionated protocol.
> When only first-occurrence cases were included, median PFI was significantly longer in the finely fractionated group compared with the coarsely fractionated group (1430 vs 540 days; P = 0.007).
> Cats with first-occurrence ISSs appear to benefit from postoperative finely fractionated radiotherapy.

**PMID 30244666** · Sabattini S 2019
> Cutaneous mast cell tumors (cMCTs) account for approximately 20% of skin neoplasms in cats.
> Tumors were classified as high grade if there were >5 mitotic figures in 10 fields (400×) and at least 2 of the following criteria: tumor diameter >1.5 cm, irregular nuclear shape, and nucleolar prominence/chromatin clusters.
> According to this scheme, the 15 (24%) high-grade cMCTs had significantly reduced survival time (median, 349 days; 95% CI, 0-739 days) as compared with the 48 low-grade tumors (median not reached; P < .001).

**PMID 31113336** · Dagher E 2019
> Survey data and histologic features of 342 feline invasive mammary carcinomas were analyzed with respect to overall and cancer-specific survival.
> This retrospective study validates Mills et al's proposal to adapt the thresholds for mitotic counts to better assess the histological grade of the highly proliferative mammary carcinomas encountered in the cat.
> The Elston and Ellis (EE) histologic grading system, originally developed for human breast cancer, is commonly used to grade feline mammary carcinomas, although it is not really adapted for this species, hence the need of a more relevant grading system.
> ⚠️ Excerpts added 2026-07-20; this block previously held only a flag and no source text.
> ⚠️ **A worked example of why this repository exists.** A grading system built for human breast cancer was carried into cats and used routinely — the authors say plainly it "is not really adapted for this species". What fixed it was not new biology but **re-thresholding the mitotic count for a more proliferative tumour**. The hazard ratios of the corrected system are modest (grade III HR 1.46, grade II HR 1.39 against grade I), and remain significant independently of tumour size and nodal stage.
> ⚠️ The figure `2020` cited in the body **does not appear in the abstract text** — it may come from the full text (which the abstract does not contain), or may be erroneous; **retrieve the full text and verify before citing**. (Note: this check misses figures that the source spells out as English words.)

**PMID 31478220** · Rout ED 2019
> The IGH-VDJ reaction alone only detected clonality in 50% (19/38) of these cases.
> Using four immunoglobulin primer sets (IGH-VDJ, IGH-DJ, Kde, and IGL), clonal immunoglobulin rearrangements were detected in 87% (33/38) of the presumed B-cell neoplasms.
> ⚠️ The figure `2024` cited in the body **does not appear in the abstract text** — it may come from the full text (which the abstract does not contain), or may be erroneous; **retrieve the full text and verify before citing**. (Note: this check misses figures that the source spells out as English words.)

**PMID 31756259** · Marconato L 2020
> Overall median progression-free interval (PFI) was poor with 70 days (95% CI: 48;93).
> In 8 of the 27 (29.6%) cats in group B, however, severe toxicity (grade 3) occurred.
> With the overall poor outcome and high occurrence of acute toxicity, we cannot recommend the use of this accelerated radiation protocol combined with anti-angiogenic therapy for oral SCC in cats.

**PMID 31788484** · Chocteau F 2019
> This retrospective study included 395 female cats with a surgically removed mammary carcinoma, with a 2-year follow-up.
> Invasiveness (distinction between in situ and invasive FMCs), the pathologic tumor size (pT), lymphovascular invasion (LVI), and the pathologic nodal stage (pN) defined a 5-stage system: Stage 0 (FMCs in situ), Stage I (pT1, LVI-, pN0-pNX), Stage II (pT2, LVI-, pN0-pNX), Stage IIIA (pT1, LVI+ and/or pN+), and Stage IIIB (pT2, LVI+ and/or pN+), where pT1 was ≤20 mm, pT2 was >20 mm, and pNX corresponded to unsampled draining lymph node.
> Higher histological stages were associated with reduced disease-free interval, overall survival, and specific survival.

**PMID 32684120** · Horta RS 2021
> This prospective study included owned cats, diagnosed (cytologically) with multicentric or mediastinal lymphoma and treated with the LOPH (lomustine, vincristine [Oncovin; Antibióticos do Brasil], prednisolone and hydroxydaunorubicin [doxorubicin]) protocol.
> Complete response was reported in 81% (n = 17/21), while three had partial remission and one had no response.
> The MST (lymphoma-related survival) for the 21 cats was 214 days.
> The LOPH protocol was well tolerated by cats with lymphoma and persistent FeLV viremia, and resulted in a better MST than similar studies with other protocols.

**PMID 32954630** · Chocteau F 2021
> In this cohort of 344 dogs and 342 cats with surgically removed stage I to III invasive MCs, with a minimal follow-up of 2 years, we calculated the 1-year CS, that is, the probability for patients that have survived 1 year, to survive or to die from cancer during the subsequent year.
> The 1-year conditional specific survival probabilities were 59% and 48% at diagnosis of invasive MC respectively in dogs and cats, and 80% and 52% in 1-year surviving dogs and cats respectively, suggesting that 1-year surviving dogs were relatively protected from cancer-related death, whereas feline MCs remained life-threatening cancers for longer periods of time.
> ⚠️ Mixed canine-feline cohort (344 dogs, 342 cats). The feline-specific conditional-survival figures are 48% (at diagnosis) and 52% (in 1-year survivors); the dog figures (59%, 80%) are given alongside for comparison, not as feline data.

**PMID 33140523** · Petrucci GN 2020
> The median DFI was 270, 226 and 372 days in groups 1, 2 and 3, respectively.
> The median OS was 338 (group 1), 421 (group 2) and 430 (group 3) days.
> The differences between groups were not significant (DFI P = .280 and OS P = .186).
> In conclusion, adjuvant chemotherapy treatment did not improve survival and the overall benefit remains unproven.
> ⚠️ Excerpts added 2026-07-20. The master-literature index asserts "no benefit from adjuvant mammary chemotherapy" for this PMID — **a finding, not a topic label, and it had no source text behind it until now.** The abstract does support it. Note what the numbers show: the point estimates favour metronomic cyclophosphamide + meloxicam (DFI 372, OS 430) over surgery alone, but n = 23 versus 80 and the differences are not significant. **"Not shown to help" is the claim; "shown not to help" is not.**
> ⚠️ The figure `2019` cited in the body **does not appear in the abstract text** — it may come from the full text (which the abstract does not contain), or may be erroneous; **retrieve the full text and verify before citing**. (Note: this check misses figures that the source spells out as English words.)

**PMID 33176543** · Smallwood K 2021
> The medical records of 13 cats treated with lomustine, methotrexate and cytarabine for relapsed high-grade feline lymphoma, at a single institution between 2013 and 2018, were examined.
> In cats that received (or in which there was intention to treat with) all three drugs, 6/13 (46%) demonstrated a complete or partial response to chemotherapy.
> The median progression-free survival was 61 days (range 16-721 days).

**PMID 33660305** · Yoshikawa H 2021
> Cats that underwent second DRT course at time of recurrence lived significantly longer than cats that received 1 RT course (either DRT or PRT [median OST 824 days (95% CI: 237-1410 days) vs 434 days (95% CI: 277-591 days); p = .028]).
> In multivariate modeling, cats received definitive-intent treatment (DRT; FRT/SRT) had significantly longer median PFS (504 days, [95% confidence interval (CI): 428-580 days] vs PRT 198 days [95% CI: 62-334 days]; p = 0.006) and median OST [721 days (95% CI: 527-915 days) vs 284 days (95% CI: 0-570 days); p = 0.001]).

**PMID 33881389** · Cleary M 2022
> Animal owners who experience the death of a beloved family pet or companion animal may experience feelings of grief and loss that are synonymous with the death of a human.
> This systematic review synthesized 19 qualitative papers from 17 studies that explored the psychosocial impact of bereavement and grieving the loss of a pet.
> The analysis revealed five themes: Their Relationship; Their Grief; Their Guilt; Their Supports; and Their Future.
> ⚠️ HUMAN data: a qualitative systematic review of human bereavement/grief psychology after the death of a companion animal (pets generally, not feline-specific). Cited in the body as human-grief context, not as feline clinical evidence.

**PMID 33924569** · Littlewood K 2021
> Our study explored the ways in which end-of-life decisions were being made by owners of older and chronically ill cats in New Zealand and the role of their veterinarian in the process.
> Qualitative data were gathered via retrospective semi-structured interviews with 14 cat owners using open-ended questions.
> Four were animal-centered themes: cat behavior change, pain was a bad sign, signs of ageing are not good, and the benefits of having other people see what owners often could not.

**PMID 33941335** · Doit H 2021
> This systematic review aimed to explore the published literature to identify the number and range of QoL assessment tools available to researchers and veterinary professionals, by discovering tools which have already been used in published studies.
> A total of 1138 manuscripts were identified, of which 96 met all criteria.
> Forty of 96 manuscripts contained an assessment of QoL, using one of 32 unique tools identified.
> Only eight of the structured tools were validated, and of these, three could be applied to healthy cats; the remainder being specific to a disease or being hospitalised.

**PMID 34167339** · Ray M 2021
> The '2021 AAFP Feline Senior Care Guidelines' are authored by a Task Force of experts in feline clinical medicine and serve as an update and extension of those published in 2009.
> ⚠️ **FALSE POSITIVE, resolved 2026-07-20.** The figures `21, 259` were flagged here. Both belong to **Mortier 2024 (PMID 38967102)** — "259 apparently healthy" cats, "21% ... were not considered healthy" — quoted verbatim in that paper's own excerpt block, from the PMC full text. The AAFP guidelines and Mortier are cited in one body sentence. `2024` is a citation year. Nothing was ever unverified.

**PMID 34328359** · Lucroy MD 2022
> In total, 117 cats met the inclusion criteria and received 422 doses of autologous cancer vaccine.
> Six (5.1%) cats had seven reported AEs, with the majority of these (85.7%) being characterized as grade 1 or 2 (mild) and resolving without medical intervention.
> AEs were infrequent in cats treated with an adjuvanted whole-cell autologous cancer vaccine under typical field use conditions.

**PMID 34374109** · Freiche V 2021
> The Ki-67 20%- and 30%-thresholds discriminated between LGITL and LPE within both the epithelium (specificity >95%) and lamina propria (specificity >95%), respectively.
> Surprisingly, 70% of LPE cases featured monoclonality (40%) or monoclonality on a polyclonal background (30%).

**PMID 34579716** · Wang L 2021
> ROC analysis revealed an area under the curve (AUC) of 0.98 with a sensitivity of 0.83 and a specificity of 0.95 for felines with lymphoma.
> **【PMC full text retrieved and checked】**
> ROC (receiver operating characteristic) analysis showed an AUC (area under the curve) value of 0.98 (< 0.0001) for the lymphoma group and 0.86 (< 0.001) for the solid tumor group, at 95% confidence interval.
> At the chosen cutoff value the sensitivity was 0.83 and the specificity was 0.95 for lymphoma.
> ⚠️ Check passed: AUC 0.98, sensitivity 0.83 and specificity 0.95 all match the body text.

**PMID 34724255** · Gruen ME 2021
> Frunevetmab, a felinized antinerve growth factor monoclonal antibody, effectively decreases osteoarthritis (OA) pain in cats.
> Significant improvement with frunevetmab over placebo occurred at days 28 and 56 for the client specific outcome measures (CSOM) questionnaire (success rates and total scores [NNT of 9 and ES of 0.3 at day 56]); at days 28 and 56 for owner-assessed global treatment response; and at days 56 and 84 for veterinarian-assessed joint pain (ES of 0.18 at day 56).
> Adverse events did not differ between groups, except skin disorders which collectively occurred significantly more frequently in frunevetmab treated (32/182 cats) vs placebo (8/93 cats).

**PMID 35188694** · Reczynska AI 2022
> Negative prognostic factors included cribriform lysis (MST 121 vs. 876 days, P = 0.0009) and intracalvarial involvement (MST 100 vs. 438 days, P = 0.0007).
> Disease progression was noted in 38% (12/32), locally in 22% (7/32), and systemically in 16% (5/32).
> Progression free survival was 225 days (95% CI 98-514) and median survival time (MST) was 365 days (95% CI 123-531).

**PMID 35421221** · Rohrer Bley C 2022
> The trial was prematurely interrupted due to maxillary bone necrosis, which occurred 9 to 15 months after radiotherapy in 3 of 7 cats treated with FLASH-radiotherapy (43%), as compared with 0 of 9 cats treated with SoC.
> Cats with T1-T2, N0 carcinomas of the nasal planum were randomly assigned to two arms of electron irradiation: arm 1 was the standard of care (SoC) and used 10 × 4.8 Gy (90% isodose); arm 2 used 1 × 30 Gy (90% isodose) FLASH.

**PMID 36052863** · Ii T 2022
> Cases included 14 large-cell lymphomas (LCLs) and 36 small-cell lymphomas (SCLs).
> LCLs were positive for CD8 in 13/14 cases (93%), T-cell intracellular antigen 1 (TIA1) in 14/14 cases (100%), and granzyme B in 6/14 cases (43%).
> SCLs were positive for CD8 in 28/36 cases (78%), TIA1 in 33/36 cases (92%), and granzyme B in 2/36 cases (6%).
> TIA1- and granzyme B-positive neoplastic lymphocytes were predominantly observed in the mucosal epithelium of 10/50 cases (20%) and 6/50 cases (12%), respectively.
> No significant differences in survival time were found based on cell size or epitheliotropism.
> However, cases with TIA1+ and/or granzyme B+ neoplastic lymphocytes predominantly in the mucosal epithelium had significantly shorter survival times (P < .05), suggesting that mucosal epithelium infiltration of neoplastic cells with a cytotoxic immunophenotype is a negative prognostic factor.
> Clonal T-cell receptor (TCR) gene rearrangement was detected in 10/14 (71%) LCL cases and 33/36 (92%) SCL cases. No clonal immunoglobulin heavy chain (IgH) gene rearrangement was detected.
> **【Publisher full text retrieved and checked 2026-07-20 — source: publisher PDF】**
> In a previous study, the median survival time of LCL cases was approximately 1.5 months and that of SCL cases was 28 months.
> Intestinal tissue specimens endoscopically collected from 50 cats at Japan Small Animal Medical Center (JSAMC) between 2018 and 2020 were examined.
> ⚠️ **A previous ⚠️ marker here was a FALSE POSITIVE and has been removed.** It flagged the figures `85, 2024` as unverified against this abstract. Those figures belong to Wolfesberger 2024 (PMID 38943798) and are correctly attributed in the body; they were mis-assigned to this PMID because both citations appear in the same sentence. `extract_source_excerpts.py` attributes figures by sentence, so a sentence carrying two citations can hang one paper's numbers on the other. Check attribution before treating such a flag as a real gap.

**PMID 36649089** · Monteiro BP 2023
> A total of 3039 responses were received with 1262 completed answers from 66 countries (86%, 11.1% and 2.9% identified as female, male or other, respectively).
> The ICC single (caregivers) was 0.65, 0.69, 0.58, 0.37, 0.38 and 0.65, respectively, for AU ears, eyes, muzzle, whiskers, head and sum of scores.
> Total FGS scores had good reliability when used by cat caregivers, regardless of demographic variables, showing the potential applicability of the instrument to improve feline pain management and welfare worldwide.

**PMID 36655881** · Rodriguez-Piza I 2023
> Median PFS and OS were 909 days (range 23-1484) and 909 days (range 23-2423), respectively.
> **【PMC full text retrieved and checked】**
> The mean duration of clinical signs before presentation was recorded in 21/23 cases and was 57.5 days (range 2-515).
> Immunohistochemistry was available in 11 cases (48%); all were consistent with B-cell lymphoma.
> Lymphoma grade was reviewed in 11 cases, of which nine were classified as low grade and two as intermediate grade.
> No cases had lymphoma documented in a location other than the primary site.
> ⚠️ ⚠️ The abstract and the body of this paper contradict each other: the abstract states "Pretreatment with steroids was associated with longer OS (p = 0.003)", whereas the Results section states "Age, breed, sex, retroviral status, anatomical location, anaemia at presentation, debulking surgery and pretreatment with corticosteroids did not affect PFS or OS." Any citation of this point must state the contradiction.

**PMID 36701405** · Maekawa N 2023
> We first determined the complete coding sequence of feline PD-L1 and PD-L2, and found that the deduced amino acid sequences of feline PD-L1/PD-L2 share high sequence identities (66-83%) with orthologs in other mammalian species.
> Finally, immunohistochemistry using CL1Mab-7 also showed PD-L1 expression in feline squamous cell carcinoma (5/5, 100%), mammary adenocarcinoma (4/5, 80%), fibrosarcoma (5/5, 100%), and renal cell carcinoma (2/2, 100%) tissues.
> ⚠️ Molecular/in-vitro and IHC characterization study (cell lines and banked tissue), not a clinical trial in live cats with disease.

**PMID 36851461** · Sampaio F 2023
> Immunophenotyping was inconclusive in 54% RSC and 19% CB.

**PMID 37130034** · Marsilio S 2023
> Lymphoplasmacytic enteritis (LPE) and low-grade intestinal T cell lymphoma (LGITL) are common diseases in older cats, but their diagnosis and differentiation remain challenging.
> To date, no single diagnostic criterion or known biomarker reliably differentiates inflammatory lesions from neoplastic lymphoproliferations in the intestinal tract of cats and a diagnosis currently is established by integrating all available clinical and diagnostic data.
> Histopathology remains the mainstay to better differentiate LPE from LGITL in cats with chronic enteropathy.

**PMID 37768060** · Eigner DR 2023
> The '2023 AAFP/IAAHPC Feline Hospice and Palliative Care Guidelines' are authored by a Task Force of experts in feline hospice and palliative care convened by the American Association of Feline Practitioners and the International Association for Animal Hospice and Palliative Care.
> ⚠️ **FALSE POSITIVE, resolved 2026-07-20.** The figure `93` was flagged here. It is the willingness-to-trade proportion of **Reynolds 2010 (PMID 20738770)**, already marked "Check passed" in that paper's own excerpt block — where the source spells it "Ninety-three percent", so a numeric match misses it twice over. The two are cited in one body sentence. `2010` is a citation year. Nothing was ever unverified.

**PMID 37835664** · Žagar Ž 2023
> A comprehensive search of three electronic databases and relevant paper reference lists identified 139 studies meeting the inclusion criteria.
> Based on the current literature, toceranib phosphate appears to be the most efficacious TKI in cats, especially against MCTs.
> Exploring the clinical use of TKIs in mammary carcinomas holds promise.

**PMID 38152842** · Moore AS 2023
> On multivariate analysis, 40 cats that achieved CR had a median survival time of 341 days (78 days for PR, 45 days for NR); PFS times were also significantly affected by lymphocyte:monocyte L:M ratio (>3.4 = 700 days vs. ≤3.4 = 126 days) and B-cell versus T-cell phenotype (220 days vs. 42 days, respectively).
> For all 55 cats (including those receiving chemotherapy and surgery), median PFS was 184 days with 1, 2 and 3-year survival rates of 35.4%, 26.5% and 26.5%, respectively.
> Medical records were reviewed for 55 cats with alimentary lymphoma treated with a novel multiagent protocol using prednisolone, L-asparaginase, doxorubicin, vinblastine instead of vincristine, a higher dosage of cyclophosphamide and oral procarbazine (VAPC protocol).

**PMID 38774911** · Weyrich A 2024
> Formalin-fixed and paraffin-embedded samples from 31 feline T-cell lymphomas, 29 B-cell lymphomas, and 11 non-neoplastic controls were analyzed by PCR combined with capillary electrophoresis.
> ⚠️ **FALSE POSITIVE, resolved 2026-07-20.** The figures `50, 87` were flagged here. Both are PARR detection rates from **Rout 2019 (PMID 31478220)** — "50% (19/38)" for IGH-VDJ alone, "87% (33/38)" for the four-primer combination — quoted verbatim in that paper's own excerpt block. Rout and Weyrich are cited in one body sentence. `2019` is a citation year. Nothing was ever unverified.

**PMID 38943798** · Wolfesberger B 2024
> Neoplastic lymphoid cells were immunopositive for CD3 in 93% (14/15), granzyme B in 87% (13/15), CD5 in 20% (3/15), CD8 in 13% (2/15), CD4 in 7% (1/15) and CD56 in 7% (1/15) of cases.
> Feline small intestinal lymphoma predominantly demonstrates a T-cell immunophenotype identified by standard immunopositivity for T cells with CD3 or immunopositivity for B cells with CD20.
> Without immunohistochemical labelling of the cytotoxic protein granzyme B, the cytotoxic status would have been missed in 46% (6/13) of the cytological and in 85% (11/13) of the histopathological slides.
> ⚠️ The figure `2022` cited in the body **does not appear in the abstract text** — it may come from the full text (which the abstract does not contain), or may be erroneous; **retrieve the full text and verify before citing**. (Note: this check misses figures that the source spells out as English words.)

**PMID 38967102** · Mortier F 2024
> Thorough history, physical examination, blood tests, and urinalysis were performed in 259 apparently healthy mature adult (7-10 years) and senior (>10 years) cats.
> At baseline, 21% of apparently healthy cats were not considered healthy but were diagnosed with International Renal Interest Society (IRIS) ≥ stage 2 chronic kidney disease (CKD; 7.7%) or hyperthyroidism (4.6%), among other disorders.
> **【PMC full text retrieved and checked】**
> Median age of the 259 apparently healthy cats was 10 years (range, 7-18 years).
> ⚠️ Check passed: 259 apparently healthy cats, median age 10 years.

**PMID 39073984** · Ferrer-Jorda E 2024
> In total, 21 cats were enrolled over a 4-year period.
> Nineteen cats achieved a complete response (CR) and two cats a partial response (PR) for an overall response rate of 100%.
> The overall survival was 453 days for a median follow-up of 341 days (range 191-989).
> Of the cats, 62% had grade 3 or 4 toxicities, but no deaths due to the treatment were documented.

**PMID 39212426** · Del Portillo Miguel I 2024
> A total of 17 cats with cytologically or histopathologically confirmed mammary adenocarcinoma (gross disease) were prospectively enrolled.
> Clinical benefit was seen in 12 (64.7%) cats and an objective response was seen in six (35.2%) cats.
> The median progression-free survival and median overall survival time were 91 days (range 30-158) and 145 days (range 31-234), respectively.

**PMID 39287178** · Williams K 2024
> In total, 32 cats treated with toceranib for malignancies were analyzed.
> None of the 32 cats developed progressive proteinuria or azotemia during the follow-up period (median 56 days; range 56-336).
> The incidence of proteinuria, renal azotemia and hypertension in cats treated with toceranib for neoplasia appears to be low.

**PMID 39346958** · Ruiz-Perez CA 2024
> Two cats with cytologically confirmed lymphoma and nine presumably cancer-free cats were included in this analysis.
> Both cancer-diagnosed subjects had somatic copy number variants (a "cancer signal") identified in cell-free DNA, suggesting the current presence of cancer in these subjects.
> This study lays the foundation for future studies to fully validate this type of testing for use in clinical practice.
> ⚠️ Body claim's "Nu.Q canine-only" figure concerns a different assay/paper, not this PMID; not addressed in this abstract.

**PMID 39631169** · Cockey JR 2025
> 6 healthy cats were used in this study.
> Chimeric antigen receptor T cells were engineered by transduction with an FIV-based lentiviral system to express a human CD19 CAR.
> Feline CD19 CAR T cells demonstrated specific cytotoxicity against human CD19+ target cells.
> ⚠️ In vitro proof-of-concept using feline T cells engineered against a human CD19 target; not a feline tumor model or in-vivo study.

**PMID 40119555** · Pui Yung Anna L 2025
> Progression-free survival was 264 days (range, 6-1486 days), the disease-free interval was 812 days (range, 39-1486 days) and the median survival time for all cats was 412 days (range, 7-1772 days).
> Complete response was achieved in 59% of the cases, and partial response was observed in 17%.
> ⚠️ **FALSE POSITIVE, resolved 2026-07-20.** The figure `123` was flagged here as unverified. It is the enrolment count of **Lai 2025 (PMID 40443182)**, verified in that paper's own excerpt block, and the two are cited in one sentence in the body — sentence-level attribution filed one paper's number under the other. Nothing was ever unverified.

**PMID 40443182** · Lai NA 2025
> A total of 123 cats were enrolled, with 41 cats in the CMOP group and 82 cats in the CHOP group.
> No significant differences were identified between the response rates (66% in both groups), median PFI (CMOP 69 days, CHOP 59 days) and median ST (CMOP 103 days, CHOP 80 days) of cats treated with CMOP instead of CHOP.
> CMOP is a well-tolerated and suitable substitute for CHOP for feline intermediate- to large-cell lymphoma. It is logistically easier to administer as it can be given as an intravenous bolus and carries less risk of catastrophic extravasation injuries.
> **【Publisher full text retrieved and checked 2026-07-20 — source: publisher PDF】**
> Medical records of cats treated for intermediate- to large-cell lymphoma between 2015 and 2023 from three referral institutions within the larger Sydney metropolitan area were retrospectively reviewed.
> ⚠️ **FALSE POSITIVE resolved 2026-07-20**: the figure `412` was flagged here. It is the median survival time from **Lee/Pui Yung 2025 (PMID 40119555)**, verified in that paper's excerpt block. Same sentence-level mis-attribution as above, in the opposite direction — the two papers swapped flags.

**PMID 40591622** · Biezus G 2025
> The median survival time following FeLV diagnosis was 30 days for the FeLV+P group.
> In total, 176 cats were selected: 116 with progressive infection (FeLV+P), 30 with regressive infection (FeLV+ R), and 30 FeLV-negative cats (Control).

**PMID 40974651** · Nishibori S 2025
> Immune checkpoint inhibitors (ICIs) have revolutionized cancer treatment in humans; however, research on ICIs in cats remains limited, and no clinical trials have been conducted for feline neoplastic diseases.
> We engineered two 1A1-2-fIgG1 mutants with amino acid substitutions in the constant region to reduce the interactions between the Fc fragment and C1q or FcγRs and mitigate these effector functions.
> These mutations successfully abolished the binding to CD64, CD32, and CD16 while preserving the affinity for FcRn, which is essential in maintaining the half-life of antibodies in the blood.
> ⚠️ In vitro/molecular antibody-engineering study; no cats with disease were treated. Abstract explicitly states no clinical trials of ICIs in cats have been conducted.

**PMID 42375287** · Ueno H 2026
> Twenty-six cats were treated, 11 of which underwent reirradiation after clinical progression.
> The median overall survival was significantly longer in the reirradiation group than in the nonreirradiation group (562 vs. 58 days, p < 0.001).
> Two cats developed grade 3 late toxicities (cutaneous or oral-cutaneous-nasal fistulas) associated with bone lysis and short inter-treatment intervals.
