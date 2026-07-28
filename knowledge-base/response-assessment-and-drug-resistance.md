# Judging "Response" and "Resistance" — what the criteria actually cover, and where a drug gets written off too early

> Generated 2026-07-27 · PubMed search + verbatim verification · Not diagnostic, not a prescription
> **Purpose**: "this drug isn't working" is one of the highest-stakes judgements in a chemotherapy course — it removes an agent from the arsenal, often permanently, and drives the switch to a new one. This file asks what that judgement actually rests on. It was prompted by an owner's question: their cat's *ocular* lesion grew slightly a week after a first vincristine dose, and vincristine was written off. Their instinct that this might be premature turns out to be supportable — though for a **different and stronger reason than they proposed**.
> **Division of labour**: protocols and survival live in [`feline-oncology-literature-survey.md`](feline-oncology-literature-survey.md) §3; per-drug toxicity in [`antineoplastic-drug-toxicity.md`](antineoplastic-drug-toxicity.md); 2025 options in [`feline-lymphoma-treatment-currency.md`](feline-lymphoma-treatment-currency.md). This file is about **the measurement and the inference**, not about what to give.

---

## 0. The finding that matters most

### 0.1 The standard response criteria are for **dogs**, for **nodal** disease, and say so

Every "CR / PR / SD / PD" judgement in veterinary lymphoma traces back to a single consensus document — VCOG's response evaluation criteria (Vail 2010, PMID 20230579). Its own scope statement is unusually explicit:

> *"These guidelines are intended only for use in dogs, where peripheral lymphadenopathy represents the principal component of their disease and as such do not critically assess extranodal disease (e.g., primary cutaneous, central nervous system, gastrointestinal)."*

> **⭐ Read the three restrictions in that one sentence.** It is **(a) for dogs**, not cats; **(b) for peripheral lymphadenopathy**, i.e. measurable peripheral nodes; and **(c) explicitly not validated for extranodal disease.** An **intraocular** lesion is extranodal. So calling a drug "non-responsive" on the behaviour of an eye lesion is a judgement made **outside the stated scope of the only standardised criteria that exist** — and the document itself is the source for that limitation. This is a **methodological** point, not a speculation about tumour biology.

⚠️ **What this does *not* mean.** It does not mean such a judgement is wrong, and it does not mean a clinician who makes it is careless — no better instrument exists, and an extranodal lesion is often the only thing that can be measured at all. It means the confidence attached to it should be lower than the confidence attached to a nodal measurement in a dog, and that **a single small change at a single early timepoint is thin evidence** either way.

### 0.2 In an eye, what you are measuring may not be tumour at all

Feline intraocular lymphoma comes with inflammation far more often than not: in 172 biopsy-confirmed cases, *"The majority of cases exhibited concurrent uveitis (75%) and secondary glaucoma (58%)"* (Musciano 2019, PMID 31328872). And in newly diagnosed, treatment-naïve cats, ocular change is common — *"In 12 cats (48%), ocular changes were documented"*, with *"Uveitis anterior and posterior… present in 58% of affected individuals"* (Nerschbach 2013, PMID 24102737).

> **The consequence for response assessment.** A modest *increase* in an intraocular lesion is compatible with at least three different underlying states: tumour growth, **inflammatory uveitis**, or tumour shrinkage masked by inflammation. **The eye is an unusually noisy readout**, and the noise happens to move in the same direction as the signal you are trying to exclude.

**But ocular disease does respond to systemic chemotherapy.** In the two chemotherapy-treated cats with ocular involvement in that prospective series: *"a complete remission of an anterior and a partial remission of a posterior uveitis were documented"* (Nerschbach 2013). ⚠️ n=2 — a demonstration that response is possible, not a response rate. **So an eye lesion is not a compartment that systemic drugs simply cannot reach.**

⚠️ Also relevant to staging rather than response: ocular involvement moved four cats from stage IV to stage V, and intraocular lymphoma with suspected systemic involvement carried a shorter median survival (69 days) than presumed solitary ocular lymphoma (154 days; P = 0.003) (Nerschbach 2013; Musciano 2019).

---

## 1. Cross-resistance: what actually shares a mechanism

The practical question behind "was this drug written off too early" is usually: **after months on one drug, which agents are still likely to work?** There is a mechanism-level answer, and it is more specific than "try something different."

In a canine lymphoid cell line made resistant by prolonged **doxorubicin** exposure, the resistant sub-line was *"more resistant to doxorubicin and vincristine, but not to prednisolone"*, carried *"a highly increased P-glycoprotein (P-gp/abcb1) expression"*, and — the causal part — *"Both resistance to doxorubicin and vincristine… were fully reversed by the P-gp inhibitor PSC833"* (Zandvliet 2014, PMID 24975508).

> **⭐ What this establishes, and what it does not.**
> **Establishes:** doxorubicin and vincristine are **exported by the same pump**. Selection pressure from one is expected to reduce sensitivity to the other. Prednisolone is **not** affected by that pump — a genuinely non-cross-resistant partner by mechanism.
> **Does not establish:** anything about alkylating agents (cyclophosphamide, lomustine, chlorambucil), which were not tested here and are not classical P-gp substrates. **"Selected by cyclophosphamide" and "resistant to vincristine" are therefore not the same claim**, and should not be treated as one.
> ⚠️ **And it is a cell line, not a patient.** In vitro selection is a model of resistance, not a measurement of it in a living cat.

**The counterweight, which matters just as much.** In 31 **untreated** canine lymphomas, *"24 (80%)… were positive for Pgp"* — i.e. the pump is already expressed in most tumours *before* any chemotherapy — and *"The Pgp protein expression and DOR and survival was not statistically significant"* (Dhaliwal 2013, PMID 23535752).

> **So P-gp is not a clean predictor and must not be used as one.** It is present at baseline in most cases and did not predict remission duration or survival. **The mechanism is real; its prognostic value in an individual patient is not established.** Any reasoning of the form "drug A selected for resistance, therefore drug B will fail" is a hypothesis to raise with an oncologist, not a conclusion to act on.

---

## 2. What is actually established about early response

- **Achieving complete remission is the strongest positive prognostic factor across studies** — see [`feline-oncology-literature-survey.md`](feline-oncology-literature-survey.md) §3. This supports treating early, deep response as important. ⚠️ It does **not** establish the stronger folk claim that *"the first remission is necessarily the best one"*; this file located no feline evidence comparing first-versus-subsequent remission durations, and that claim is therefore **recorded as unverified**.
- **A previously used drug is not automatically finished.** In 56 cats with small-cell disease treated with chlorambucil, **re-induction remained effective at relapse after discontinuation** (Pope 2015 — sourced in [`feline-oncology-literature-survey.md`](feline-oncology-literature-survey.md) §3). ⚠️ That is a different drug, subtype and situation from re-challenging a drug judged non-responsive at induction — it establishes that re-use *is a recognised strategy*, not that any specific re-challenge is indicated.
- **Net size change is arithmetic, not a direct read-out of cell kill.** A lesion's measured change reflects proliferation *minus* cell death. A small net increase is therefore consistent with substantial cell kill outpaced by growth, and also with no cell kill at all. ⚠️ **Recorded as reasoning, not as a sourced feline finding** — this file located no feline study measuring proliferation and apoptosis against clinical size change. It cuts both ways: it undermines "it grew, therefore no response," and equally it provides no evidence that response *was* occurring.

---

## 2b. When serial imaging is off the table — reading one scan, and what replaces it

Repeat imaging is frequently unavailable in practice: it needs anaesthesia, and for a patient with airway compromise, cardiac disease or a previous anaesthetic event, that is a real risk rather than an inconvenience. Cost removes it for others. **The diagnostic scan then has to do a different job than it was ordered for**, and something has to take over the monitoring.

> ⚠️ **This section is reasoning and clinical practice, not a sourced feline finding.** No study was located validating palpation or awake radiography as response measures in feline lymphoma. It is recorded as *how to structure the question for the oncologist*, not as evidence that these substitutes work.

### 2b.1 Bulk and prognosis are different axes

The number an owner fixes on is the largest diameter. **It is usually not the feature carrying the risk.** More decision-relevant, read off the same report:

| Feature | Why it matters more than the diameter |
|---|---|
| **Bone lysis at a skull-base foramen** | A foramen transmits a nerve; enlargement suggests perineural extension toward the cranial vault — a route, not just erosion |
| **Airway or oesophageal compromise** | The thing that kills first, and on a timescale of hours |
| **Adherence to a named vessel** | Converts any future sampling or surgery into a bleeding question |
| **A node with an indistinct border against the mass** | May be contiguous rather than a separate station — changes what a sample from "the node" even means |
| **"No obvious intracranial extension"** | ⚠️ Is *not seen*, not *excluded* — a monitoring instruction, not a reassurance |

**⭐ And bulk means different things for different tumours.** A large chemo-sensitive lymphoma can collapse within days to weeks; a carcinoma of the same size in the same location often cannot be reduced at all. Reading "large" as "hopeless" imports a prognosis from the wrong tumour type. ⚠️ The converse also holds — chemo-sensitivity is an expectation, not an entitlement, and only observed response confirms it in a given animal.

### 2b.2 A layered read, because the layers move at different speeds

Bundling everything into one worry loses the distinction between what needs an emergency call tonight and what needs a question at the next appointment.

| Layer | Question | Timescale |
|---|---|---|
| **1** | Is the airway (or other immediately life-limiting structure) failing? | hours–days — **the only emergency axis** |
| **2** | Is the lesion responding? | weeks — the surrogates below |
| **3** | Is it extending along the route the imaging identified? | weeks–months — **new neurological signs**, not size |
| **4** | Was complete remission achieved? | months — the variable carrying the prognosis (§2) |

**Layer 3 is not theoretical when the imaging shows a skull-base route.** Two feline middle-ear lymphoma reports illustrate the endpoint: one cat died on day 228 after generalised seizures (Takahashi 2023, PMID 37756106); another *"lost ventilatory drive after induction for anesthesia"* with suspected brain herniation (Kerns 2018, PMID 29487747). Both are single cases — cited to show the pathway exists, not to assign probability.

### 2b.3 What can replace serial imaging, and its limits

Whatever is used, the point is that **layer 2 needs something, and the oncologist should be the one to specify it**:

- **A palpable mass**, measured the same way each time, by the same person. ⚠️ Unblinded and subjective; an owner wants it smaller.
- **Awake radiography** where the relevant structure is visible — no anaesthesia required.
- **An accessible ultrasound window**, where anatomy allows.
- **A site-specific external sign** (visible protrusion, discharge from an involved ear canal) — ⚠️ interpret only as an asymmetric indicator: improvement is meaningful, absence of improvement often is not.

**⚠️ The confounder that spoils all of them: concurrent corticosteroids.** Steroids reduce peritumoural oedema without reducing tumour, so a lesion can palpate smaller and an airway can open while tumour burden is unchanged. **Record the steroid dose on the same axis as the measurement**, or the two effects cannot be separated later.

**⭐ Why this matters beyond monitoring:** individualising a dosing interval requires being able to detect regrowth (see [`feline-lymphoma-treatment-currency.md`](feline-lymphoma-treatment-currency.md) §2b.3). An animal with a usable surrogate can have that conversation; one without it cannot, and the fixed schedule is doing the monitoring's job.

---

## 3. At the decision moment

- **Ask what the response judgement was measured on.** Nodal, imaged, or an extranodal lesion? At what interval? A judgement resting on one extranodal lesion at one early timepoint is the weakest configuration, per §0.1 — and it is worth saying so out loud to the oncologist, as a question rather than a challenge.
- **In an eye specifically, ask whether inflammation was distinguished from tumour** (§0.2). Uveitis accompanies most feline intraocular lymphoma and moves in the same direction as progression.
- **"Non-cross-resistant" has a mechanism, and it is worth naming it.** Vincristine and doxorubicin share P-gp efflux; prednisolone does not; alkylators were not tested (§1). ⚠️ But P-gp is present in most untreated tumours and did not predict outcome — so this informs the conversation, it does not settle it.
- **⛔ Nothing in this file supports an owner overriding, delaying or re-ordering a protocol.** The judgement of response, and the choice to re-challenge or switch, belong to the attending oncologist, who has the systemic picture, the imaging and the examination that none of this material substitutes for. **What this file supports is a better question**, not a different decision.
- **Two treatment philosophies exist and this file cannot adjudicate them.** Concentrating on the single most effective agent with minimal total exposure, versus adding agents and supporting counts with growth factors, are both practised. ⚠️ **No head-to-head study comparing these strategies in cats was located.** Note only that growth-factor support has its own documented cost — see [`gcsf-and-chemotherapy-neutropenia.md`](gcsf-and-chemotherapy-neutropenia.md).

---

## References

- Vail DM, et al. Response evaluation criteria for peripheral nodal lymphoma in dogs (v1.0) — a Veterinary Cooperative Oncology Group (VCOG) consensus document. *Vet Comp Oncol* 2010;8(1):28-37. PMID 20230579. [DOI](https://doi.org/10.1111/j.1476-5829.2009.00200.x)
- Nerschbach V, et al. Ocular manifestation of lymphoma in newly diagnosed cats. *Vet Comp Oncol* 2016;14(1):58-66. PMID 24102737. [DOI](https://doi.org/10.1111/vco.12061)
- Musciano AR, et al. Clinical and histopathological classification of feline intraocular lymphoma. *Vet Ophthalmol* 2020;23(1):77-89. PMID 31328872. [DOI](https://doi.org/10.1111/vop.12692)
- Zandvliet M, et al. Multi-drug resistance in a canine lymphoid cell line due to increased P-glycoprotein expression. *Toxicol In Vitro* 2014;28(8):1498-506. PMID 24975508. [DOI](https://doi.org/10.1016/j.tiv.2014.06.004)
- Dhaliwal RS, et al. Clinicopathologic significance of histologic grade, pgp, and p53 expression in canine lymphoma. *J Am Anim Hosp Assoc* 2013;49(3):175-84. PMID 23535752. [DOI](https://doi.org/10.5326/JAAHA-MS-5843)

---

---

## 原文摘录（source excerpts）

> The sentences below are **verbatim excerpts from the source literature**, untranslated.
> The prose in the body above is my interpretation; **if you need to cite, cite the original sentences here**, and go back to the source to check the context.
> Only sentences carrying specific load-bearing conclusions are excerpted; this is not a full abstract. For the complete context, retrieve the source by PMID/DOI.

**PMID 20230579** · Vail DM 2010
> These guidelines are intended only for use in dogs, where peripheral lymphadenopathy represents the principal component of their disease and as such do not critically assess extranodal disease (e.g., primary cutaneous, central nervous system, gastrointestinal).
> Standardized assessment of response to therapy for lymphoma in dogs is lacking, making critical comparisons of treatment protocols difficult.

**PMID 24102737** · Nerschbach V 2013
> In 12 cats (48%), ocular changes were documented.
> Uveitis anterior and posterior were predominant findings, being present in 58% of affected individuals.
> In these two cats, a complete remission of an anterior and a partial remission of a posterior uveitis were documented.
> Due to the detection of ocular involvement, a stage migration from stage IV to V occurred in four patients.

**PMID 31328872** · Musciano AR 2019
> The majority of cases exhibited concurrent uveitis (75%) and secondary glaucoma (58%).
> When covarying for age at diagnosis, the median survival time was significantly higher (P = 0.003) for cases of PSOL (154 days) versus those with SSI (69 days); hazards ratio of 0.47 for PSOL (95% CI: 0.241-0.937).
> The subtype of lymphoma did not affect survival time.

**PMID 24975508** · Zandvliet M 2014
> This sub-cell line was more resistant to doxorubicin and vincristine, but not to prednisolone, and had a highly increased P-glycoprotein (P-gp/abcb1) expression and transport capacity for the P-gp model-substrate rhodamine123.
> Both resistance to doxorubicin and vincristine, and rhodamine123 transport capacity were fully reversed by the P-gp inhibitor PSC833.
> No changes were observed in the expression and function of the ABC-transporters MRP-1 and BCRP.

**PMID 23535752** · Dhaliwal RS 2013
> Of the 31 cases, 24 (80%) and 7 (22%) were positive for Pgp and p53, respectively.
> The Pgp protein expression and DOR and survival was not statistically significant.
> Expression of p53 was statistically correlated with survival.

**PMID 37756106** · Takahashi T 2023 (feline middle-ear lymphoma, n=1)
> She was diagnosed with B-cell lymphoma of the right middle ear after otoscopic sampling, which showed evidence of the filling of bilateral tympanic bullae on computed tomography.
> On day 176, magnetic resonance imaging and computed tomography were performed at checkup, revealing tumor invasion into the nasopharyngeal region and the recurrence of hepatic lesions without any brain abnormality.
> Nasal congestion then worsened, and the patient died on day 228 after presenting with generalized seizures.
> Clinicians should be mindful of middle ear lymphoma as a differential diagnosis in cats who present with a sign of otitis media, especially whose condition does respond to corticosteroid treatment.
> ⚠️ Single case report. Cited in §2b.2 only to show that the skull-base/intracranial route is a real endpoint, not to assign probability. Note also the corticosteroid-responsiveness observation, which bears on the steroid confounder in §2b.3.

**PMID 29487747** · Kerns AT 2018 (feline middle-ear lymphoma, n=1)
> A 9-year-old spayed female domestic shorthair cat with clinical signs suggestive of chronic recurrent otitis media and recent seizures was presented with multifocal nervous system disease, including bilateral central and/or peripheral vestibular, cerebellar and forebrain deficits.
> The following morning the cat's mentation worsened, and the cat lost ventilatory drive after induction for anesthesia in preparation for MRI.
> A brain herniation event was suspected, and the cat was euthanized prior to further diagnostics.
> Neoplasia should be considered in cases of middle-ear effusion that do not improve adequately with appropriate antimicrobial therapy.
> ⚠️ Single case report; the tumour was non-B, non-T and PARR failed to amplify. Cited in §2b.2 for the anaesthetic endpoint that motivates §2b entirely — imaging under anaesthesia is not a neutral act in these patients.
