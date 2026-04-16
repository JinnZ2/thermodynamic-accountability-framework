"""
skill_measurement.py
====================
Extension addressing the skill/certification mismatch.

COLLAPSE THE CONFLATION
-----------------------
The previous sim used a single variable `competence ∈ [0, 1]`.
Reality has at least four orthogonal dimensions, plus a
measurement apparatus that sees only one of them.

DIMENSIONS OF CAPACITY
----------------------
  embodied_skill     — hours of direct contact with the physical system
                       ranges from 0 (never touched it) to 1 (decades)
                       grows slowly (years), decays only with extended absence
                       carries tacit knowledge that cannot be verbalized

  cognitive_fluency  — pattern-matching, systems thinking, improvisation
                       innate + developed through varied experience
                       weakly correlated with reading/writing speed

  literacy_score     — reading speed, test-taking, form completion
                       what certification exams actually measure
                       correlates with schooling access, not with
                       capacity to do physical or mechanical work

  domain_specificity — how much of the skill is tied to THIS machine,
                       THIS material, THIS failure mode vs transferable

MEASUREMENT APPARATUS (what orgs actually use)
----------------------------------------------
  certification_signal = 0.7 * literacy_score + 0.3 * embodied_skill
  (approximately — the test format biases toward literacy heavily)

  → a dyslexic veteran with 27 years embodied = LOW cert signal
  → a fresh graduate with 6 months embodied = HIGH cert signal
  → org hires by cert signal, then wonders why
    the veteran's replacement can't do the job

THE HIDDEN REQUIREMENT
----------------------
  actual_productive_capacity = f(embodied_skill, cognitive_fluency,
                                  domain_specificity)

  for certified-but-not-embodied workers:
    productive_capacity = low until mentored for 2-5 years
    mentorship REQUIRES embodied veterans on site
    if veterans were pushed out (unskilled label + attribution capture),
    mentorship pipeline is BROKEN
    new certs never reach actual productive capacity
    → org concludes "the certificates are worthless now"
    → but it was the org that broke the pipeline

FIELD TEST
----------
  real case: Diamond Match closure
    veteran: 27 yrs WP handling + machinery maintenance
    literacy: dyslexia → low certification signal
    after closure: labor market sees "unskilled"
    new hire with shiny cert + 0 yrs embodied: "skilled"
    capacity gap: veteran ~0.9, new hire ~0.15
    measurement gap: veteran 0.25, new hire 0.85
    measurement INVERTS reality

CC0. Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import random
import statistics
import math


# =================================================================
# MULTI-DIMENSIONAL WORKER CAPACITY
# =================================================================
@dataclass
class SkillProfile:
    """Four orthogonal capacity dimensions."""
    embodied_skill: float       # [0, 1] — direct-contact hours with system
    cognitive_fluency: float    # [0, 1] — pattern-match, systems thinking
    literacy_score: float       # [0, 1] — reading/test performance
    domain_specificity: float   # [0, 1] — how plant-specific the skill is

    # Derived
    def actual_capacity(self) -> float:
        """
        What the worker can ACTUALLY do on the job.
        Embodied + cognitive dominate; literacy doesn't much matter
        for physical/mechanical work.
        """
        return (0.55 * self.embodied_skill
                + 0.35 * self.cognitive_fluency
                + 0.10 * self.literacy_score)

    def certification_signal(self) -> float:
        """
        What a credentialing exam or HR screen measures.
        Heavily weighted toward literacy.
        """
        return (0.15 * self.embodied_skill
                + 0.15 * self.cognitive_fluency
                + 0.70 * self.literacy_score)

    def teaching_capacity(self) -> float:
        """
        Ability to transfer knowledge to new hires.
        Requires embodied + cognitive; literacy optional.
        """
        return (0.60 * self.embodied_skill
                + 0.35 * self.cognitive_fluency
                + 0.05 * self.literacy_score)


# =================================================================
# ARCHETYPES (based on real patterns)
# =================================================================
def make_veteran(years_on_plant: int, dyslexic: bool = False,
                 rng: Optional[random.Random] = None) -> SkillProfile:
    """
    Long-tenured worker who learned on the job.
    Embodied skill high, literacy variable (often lower because
    they entered the workforce before credential inflation).
    """
    if rng is None:
        rng = random.Random()
    embodied = min(1.0, 0.3 + 0.7 * math.tanh(years_on_plant / 10))
    cognitive = min(1.0, 0.5 + 0.4 * math.tanh(years_on_plant / 15)
                    + rng.uniform(-0.1, 0.1))
    if dyslexic:
        literacy = rng.uniform(0.15, 0.35)
    else:
        literacy = rng.uniform(0.40, 0.70)
    specificity = min(1.0, 0.4 + 0.5 * math.tanh(years_on_plant / 12))
    return SkillProfile(embodied, cognitive, literacy, specificity)


def make_fresh_graduate(rng: Optional[random.Random] = None) -> SkillProfile:
    """
    Recent cert/degree holder, no on-plant hours.
    High literacy (they passed the tests), low embodied.
    """
    if rng is None:
        rng = random.Random()
    return SkillProfile(
        embodied_skill=rng.uniform(0.05, 0.15),
        cognitive_fluency=rng.uniform(0.30, 0.70),
        literacy_score=rng.uniform(0.65, 0.90),
        domain_specificity=rng.uniform(0.10, 0.25),
    )


def make_mid_career_credentialed(rng: Optional[random.Random] = None) -> SkillProfile:
    """
    Someone with a cert AND some years, but in an adjacent role."""
    if rng is None:
        rng = random.Random()
    return SkillProfile(
        embodied_skill=rng.uniform(0.30, 0.55),
        cognitive_fluency=rng.uniform(0.40, 0.75),
        literacy_score=rng.uniform(0.55, 0.85),
        domain_specificity=rng.uniform(0.20, 0.45),
    )


def make_salvage_engineer(years: int, dyslexic: bool = False,
                           rng: Optional[random.Random] = None) -> SkillProfile:
    """
    The 'Mighty Atom' type.
    Very high embodied + cognitive from having to work with
    broken/incomplete systems. Domain transferability high
    because the skill is 'make it work from what's there'
    rather than 'follow the manual for this unit.'
    """
    if rng is None:
        rng = random.Random()
    embodied = min(1.0, 0.5 + 0.5 * math.tanh(years / 8))
    cognitive = min(1.0, 0.7 + 0.25 * math.tanh(years / 10)
                    + rng.uniform(-0.05, 0.05))
    if dyslexic:
        literacy = rng.uniform(0.15, 0.35)
    else:
        literacy = rng.uniform(0.40, 0.70)
    # LOW specificity — the whole point of salvage is transferable
    specificity = rng.uniform(0.15, 0.30)
    return SkillProfile(embodied, cognitive, literacy, specificity)


# =================================================================
# MENTORSHIP DYNAMICS
# =================================================================
@dataclass
class PipelineWorker:
    id: int
    profile: SkillProfile
    years_at_plant: float = 0.0
    was_mentored: bool = False
    mentored_hours: float = 0.0      # accumulated mentoring received
    is_teaching: bool = False
    dyslexic: bool = False


def mentor_step(mentor: PipelineWorker, mentee: PipelineWorker,
                hours: float) -> None:
    """
    Mentorship transfers embodied skill from mentor to mentee.
    Rate scales with:
      - mentor's teaching capacity
      - mentee's cognitive fluency (how fast they absorb)
      - hours spent together
    """
    transfer_rate = (mentor.profile.teaching_capacity()
                     * mentee.profile.cognitive_fluency
                     * 0.0001)  # per hour
    gain = transfer_rate * hours
    # Embodied skill grows asymptotically toward mentor's level
    ceiling = mentor.profile.embodied_skill
    current = mentee.profile.embodied_skill
    gain = min(gain, (ceiling - current) * 0.5)
    mentee.profile.embodied_skill = min(1.0, current + gain)

    # Cognitive fluency also grows slightly (learning HOW to see)
    mentee.profile.cognitive_fluency = min(
        1.0, mentee.profile.cognitive_fluency + gain * 0.3
    )

    # Domain specificity grows
    mentee.profile.domain_specificity = min(
        1.0, mentee.profile.domain_specificity + gain * 0.5
    )

    mentee.mentored_hours += hours


# =================================================================
# SIMULATION: what happens when vets are culled
# =================================================================
def simulate_plant_lifecycle(
    quarters: int = 40,
    initial_vets: int = 20,
    initial_mids: int = 15,
    initial_fresh: int = 15,
    cull_vets_at: Optional[int] = None,     # quarter when vets are "unskilled-labeled" and pushed out
    cull_fraction: float = 0.7,
    hires_per_quarter: int = 2,
    vet_dyslexia_rate: float = 0.15,
    seed: int = 42,
):
    """
    Model a plant over 10 years.

    Optionally: at quarter `cull_vets_at`, remove `cull_fraction` of
    veterans (labeled 'unskilled' due to low certification signal,
    laid off in a restructuring, etc.)

    Measure:
      - average actual_capacity over time
      - average certification_signal over time
      - mentorship coverage (new hires receiving embodied transfer)
      - time-to-competence for new hires
    """
    rng = random.Random(seed)

    workers = []
    wid = 0

    for _ in range(initial_vets):
        dyslexic = rng.random() < vet_dyslexia_rate
        p = make_veteran(years_on_plant=rng.randint(15, 30),
                         dyslexic=dyslexic, rng=rng)
        workers.append(PipelineWorker(id=wid, profile=p,
                                        years_at_plant=rng.uniform(15, 30),
                                        is_teaching=True,
                                        dyslexic=dyslexic))
        wid += 1

    for _ in range(initial_mids):
        p = make_mid_career_credentialed(rng)
        workers.append(PipelineWorker(id=wid, profile=p,
                                        years_at_plant=rng.uniform(3, 10)))
        wid += 1

    for _ in range(initial_fresh):
        p = make_fresh_graduate(rng)
        workers.append(PipelineWorker(id=wid, profile=p,
                                        years_at_plant=rng.uniform(0, 2)))
        wid += 1



    history = []

    for q in range(quarters):
        # Cull event
        if cull_vets_at is not None and q == cull_vets_at:
            vets = [w for w in workers if w.is_teaching]
            n_cull = int(len(vets) * cull_fraction)
            # Cull by lowest certification_signal first (dyslexic vets go first)
            vets.sort(key=lambda w: w.profile.certification_signal())
            to_remove = set(v.id for v in vets[:n_cull])
            workers = [w for w in workers if w.id not in to_remove]

        # Mentorship: each veteran can effectively mentor 2-3 newer workers
        teachers = [w for w in workers if w.is_teaching]
        learners = [w for w in workers
                    if not w.is_teaching
                    and w.profile.embodied_skill < 0.6]

        if teachers and learners:
            # Pair each learner to a teacher (round-robin), each gets some hours
            hours_per_quarter_per_pair = 80  # rough
            for i, learner in enumerate(learners):
                mentor = teachers[i % len(teachers)]
                mentor_step(mentor, learner, hours_per_quarter_per_pair)
                learner.was_mentored = True

        # Time passes
        for w in workers:
            w.years_at_plant += 0.25

            # If embodied_skill crosses 0.7 and years >= 5,
            # they become a teacher themselves
            if (w.profile.embodied_skill >= 0.7
                and w.years_at_plant >= 5
                and not w.is_teaching):
                w.is_teaching = True

        # Hiring: mostly fresh grads (this is who certifies)
        for _ in range(hires_per_quarter):
            p = make_fresh_graduate(rng)
            workers.append(PipelineWorker(id=wid, profile=p,
                                            years_at_plant=0.0))
            wid += 1

        # Metrics
        if workers:
            avg_actual = statistics.mean(w.profile.actual_capacity()
                                          for w in workers)
            avg_cert = statistics.mean(w.profile.certification_signal()
                                        for w in workers)
            n_teachers = sum(1 for w in workers if w.is_teaching)
            n_learners = sum(1 for w in workers if not w.is_teaching
                              and w.profile.embodied_skill < 0.6)
            # Mentorship coverage ratio
            coverage = n_teachers / max(n_learners, 1)
            # New hire progression
            recent = [w for w in workers if w.years_at_plant < 3]
            mentored_recent = [w for w in recent if w.was_mentored]
            pct_mentored = (len(mentored_recent) / len(recent) * 100
                             if recent else 0)
        else:
            avg_actual = avg_cert = coverage = pct_mentored = 0
            n_teachers = n_learners = 0

        history.append({
            "q": q,
            "n_workers": len(workers),
            "n_teachers": n_teachers,
            "n_learners": n_learners,
            "avg_actual": avg_actual,
            "avg_cert": avg_cert,
            "coverage": coverage,
            "pct_mentored": pct_mentored,
        })

    return workers, history


def print_trajectory(label, history):
    print(f"\n  {label}")
    print(f"  {'Q':>3}{'workers':>9}{'teachers':>10}{'learners':>10}"
          f"{'actual_cap':>13}{'cert_sig':>11}{'coverage':>11}"
          f"{'%mentored':>12}")
    for m in history:
        print(f"  {m['q']:>3}{m['n_workers']:>9}{m['n_teachers']:>10}"
              f"{m['n_learners']:>10}"
              f"{m['avg_actual']:>13.3f}{m['avg_cert']:>11.3f}"
              f"{m['coverage']:>11.2f}{m['pct_mentored']:>11.1f}%")


# =================================================================
# CASE: Diamond Match-style closure + relabeling
# =================================================================
def diamond_match_case():
    """
    Scenario: veteran pool includes ~15% dyslexic old-timers.
    Plant closes. Veterans enter labor market.
    Receiving facility HR screens by certification_signal.
    We compare:
      - what HR sees (cert signal)
      - what the worker can actually do (actual capacity)
      - what happens if HR hires by cert vs actual
    """
    rng = random.Random(777)
    print(f"\n{'='*82}")
    print(f"  DIAMOND MATCH CASE: Veterans entering labor market")
    print(f"  Comparing HR certification signal vs. actual capacity")
    print(f"{'='*82}")

    # Generate a realistic veteran pool
    vets = []
    for i in range(30):
        dyslexic = rng.random() < 0.15
        years = rng.randint(12, 30)
        # Some are salvage-engineers, some are standard vets
        if rng.random() < 0.2:
            p = make_salvage_engineer(years, dyslexic=dyslexic, rng=rng)
            archetype = "salvage_eng"
        else:
            p = make_veteran(years, dyslexic=dyslexic, rng=rng)
            archetype = "veteran"
        vets.append((i, archetype, years, dyslexic, p))

    # Also generate fresh grads for comparison
    grads = []
    for i in range(30):
        p = make_fresh_graduate(rng)
        grads.append((i + 100, "fresh_grad", 0, False, p))

    all_applicants = vets + grads
    # Sort by certification signal (HR's view)
    all_applicants.sort(key=lambda a: a[4].certification_signal(),
                         reverse=True)

    print(f"\n  RANKED BY CERTIFICATION SIGNAL (what HR sees)")
    print(f"  {'rank':>5}{'id':>4}{'archetype':>14}{'years':>7}{'dysl':>6}"
          f"{'cert_sig':>10}{'actual_cap':>12}{'hired?':>9}")
    print(f"  {'-'*70}")
    # Pretend HR hires top 15
    for rank, (aid, arch, yrs, dys, p) in enumerate(all_applicants[:25]):
        hired = "YES" if rank < 15 else "—"
        dys_mark = "Y" if dys else "n"
        print(f"  {rank+1:>5}{aid:>4}{arch:>14}{yrs:>7}{dys_mark:>6}"
              f"{p.certification_signal():>10.3f}"
              f"{p.actual_capacity():>12.3f}{hired:>9}")

    hired_cert = all_applicants[:15]
    rejected = all_applicants[15:]

    print(f"\n  RESULT UNDER CERTIFICATION-BASED HIRING:")
    hired_actual = statistics.mean(a[4].actual_capacity() for a in hired_cert)
    hired_teaching = statistics.mean(a[4].teaching_capacity() for a in hired_cert)
    rejected_actual = statistics.mean(a[4].actual_capacity() for a in rejected)
    rejected_teaching = statistics.mean(a[4].teaching_capacity() for a in rejected)

    print(f"    hired:    avg actual_capacity = {hired_actual:.3f}")
    print(f"              avg teaching_capacity = {hired_teaching:.3f}")
    print(f"    rejected: avg actual_capacity = {rejected_actual:.3f}")
    print(f"              avg teaching_capacity = {rejected_teaching:.3f}")

    # Now sort by actual capacity, hire top 15
    all_applicants.sort(key=lambda a: a[4].actual_capacity(), reverse=True)
    hired_actual_rank = all_applicants[:15]
    hired_actual_cap = statistics.mean(a[4].actual_capacity()
                                         for a in hired_actual_rank)
    hired_actual_teach = statistics.mean(a[4].teaching_capacity()
                                           for a in hired_actual_rank)

    print(f"\n  COUNTERFACTUAL: HIRING BY ACTUAL CAPACITY:")
    print(f"    hired:    avg actual_capacity = {hired_actual_cap:.3f}")
    print(f"              avg teaching_capacity = {hired_actual_teach:.3f}")

    print(f"\n  DELTA:")
    print(f"    capacity foregone by cert-hiring: "
          f"{hired_actual_cap - hired_actual:+.3f}")
    print(f"    teaching capacity foregone:       "
          f"{hired_actual_teach - hired_teaching:+.3f}")

    # Who specifically gets missed?
    print(f"\n  WHO GOT MISSED (in top-15 by actual capacity "
          f"but NOT top-15 by cert):")
    actual_top_ids = set(a[0] for a in hired_actual_rank)
    cert_top_ids = set(a[0] for a in hired_cert)
    missed = [a for a in hired_actual_rank
              if a[0] not in cert_top_ids]
    print(f"  {'id':>4}{'archetype':>14}{'years':>7}{'dysl':>6}"
          f"{'cert_sig':>10}{'actual_cap':>12}")
    for (aid, arch, yrs, dys, p) in missed:
        dys_mark = "Y" if dys else "n"
        print(f"  {aid:>4}{arch:>14}{yrs:>7}{dys_mark:>6}"
              f"{p.certification_signal():>10.3f}"
              f"{p.actual_capacity():>12.3f}")


# =================================================================
# CASE: mentorship pipeline collapse
# =================================================================
def mentorship_collapse_case():
    print(f"\n{'='*82}")
    print(f"  MENTORSHIP PIPELINE COLLAPSE")
    print(f"  Comparing plant trajectories: with and without veteran cull")
    print(f"{'='*82}")

    # Baseline: no cull
    _, history_ok = simulate_plant_lifecycle(
        quarters=40, cull_vets_at=None, seed=42)

    # Cull at Q8 (2 years in): 70% of veterans removed
    _, history_culled = simulate_plant_lifecycle(
        quarters=40, cull_vets_at=8, cull_fraction=0.7, seed=42)

    print(f"\n  SCENARIO A: veterans retained throughout")
    print_trajectory("RETAINED", history_ok[::4])  # every 4th quarter

    print(f"\n  SCENARIO B: 70% of veterans culled at Q8")
    print_trajectory("CULLED", history_culled[::4])

    print(f"\n  COMPARISON AT Q40 (10 years out):")
    a = history_ok[-1]
    b = history_culled[-1]
    print(f"                      retained    culled    delta")
    print(f"    actual capacity    {a['avg_actual']:.3f}      "
          f"{b['avg_actual']:.3f}     "
          f"{b['avg_actual']-a['avg_actual']:+.3f}")
    print(f"    teaching coverage  {a['coverage']:.2f}        "
          f"{b['coverage']:.2f}       "
          f"{b['coverage']-a['coverage']:+.2f}")
    print(f"    new hires mentored {a['pct_mentored']:.1f}%     "
          f"{b['pct_mentored']:.1f}%    "
          f"{b['pct_mentored']-a['pct_mentored']:+.1f}%")


if __name__ == "__main__":
    diamond_match_case()
    mentorship_collapse_case()

    print(f"\n{'='*82}")
    print(f"  STRUCTURAL FINDING")
    print(f"{'='*82}")
    print(f"""
  Two separate measurement failures compound:

  FAILURE 1: Literacy-biased certification
    The test measures reading speed and form completion
    much more than it measures embodied capacity.
    Dyslexic veterans fail the test; fresh graduates pass.
    This INVERTS the true competence ordering for 15-20%
    of experienced workers.

  FAILURE 2: Mentorship pipeline invisibility
    Certification implies "ready to work."
    Actual productive capacity requires 2-5 years of
    on-plant mentorship AFTER certification.
    Mentorship requires embodied veterans on site.
    When vets are culled (via F1 mislabeling them as
    unskilled, or via attribution capture pushing them
    out), the pipeline breaks.
    New certs keep arriving but never reach capacity.

  ORG OBSERVES:              ACTUAL CAUSE:
  "certificates worthless"    F1 + F2 compound
  "younger generation lazy"   no one to teach them
  "lost institutional know"   mislabeled people who had it
  "need more training $$"     training without mentorship
                              produces more of the same

  The wage-market-only response (pay more for certs)
  cannot fix this. Money buys cert holders.
  Cert holders without embodied mentorship = low capacity.
  The people who could TEACH them to have capacity are
  classified as unskilled and are driving a truck.
""")
