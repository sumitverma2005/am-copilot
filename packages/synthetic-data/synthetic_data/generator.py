"""
Synthetic admissions intake call generator — batch 1 (syn_001–syn_015).

Seed strategy: MASTER_SEED + SCENARIO_OFFSETS[scenario] + call_index
NOTE: Python's built-in hash() is NOT deterministic across runs (randomised
since Python 3.3). We use a fixed integer offset per scenario type instead.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Optional

from faker import Faker

# ── Constants ──────────────────────────────────────────────────────────────────

MASTER_SEED = 42

SCENARIO_OFFSETS: dict[str, int] = {
    "excellent": 100,
    "weak": 200,
    "family_caller": 300,
    "urgency": 400,
    "objection_heavy": 500,
}

FAKE_CARRIERS = [
    "BluePeak Health",
    "Meridian Care",
    "Summit Select",
    "CoreFirst Insurance",
    "NovaCare Health",
]

TREATMENT_CENTER = "Sunrise Recovery Center"

GENERATED_AT = "2026-04-01T00:00:00Z"


# ── Seed helpers ───────────────────────────────────────────────────────────────

def _get_seed(scenario: str, call_index: int) -> int:
    return MASTER_SEED + SCENARIO_OFFSETS[scenario] + call_index


def _make_faker(seed: int) -> Faker:
    fake = Faker()
    fake.seed_instance(seed)
    return fake


def _make_rng(seed: int) -> random.Random:
    return random.Random(seed)


# ── Context builder ────────────────────────────────────────────────────────────

def _make_ctx(scenario: str, call_index: int) -> dict:
    seed = _get_seed(scenario, call_index)
    fake = _make_faker(seed)
    rng = _make_rng(seed)
    return {
        "seed": seed,
        "caller_first": fake.first_name(),
        "caller_last": fake.last_name(),
        "agent_first": fake.first_name(),
        "agent_last": fake.last_name(),
        "agent_id": f"AGT-{rng.randint(100, 999)}",
        "carrier": rng.choice(FAKE_CARRIERS),
        "member_id": f"BP{rng.randint(10000000, 99999999)}",
        "group_number": f"GRP-{rng.randint(100000, 999999)}",
        "tracking_number": f"+1{rng.randint(2000000000, 9999999999)}",
    }


# ── Overall score calculator ───────────────────────────────────────────────────

WEIGHTS = {
    "empathy_rapport": 1.5,
    "insurance_verification": 1.0,
    "clinical_screening": 1.0,
    "urgency_triage": 1.0,
    "family_caller_handling": 1.0,
    "objection_handling": 1.0,
    "next_step_clarity": 1.0,
    "compliance_language": 1.5,
}


def _calc_overall(scores: dict[str, Optional[int]]) -> int:
    total_weighted = 0.0
    total_weight = 0.0
    for dim, score in scores.items():
        if score is not None:
            total_weighted += score * WEIGHTS[dim]
            total_weight += WEIGHTS[dim]
    if total_weight == 0:
        return 0
    return round((total_weighted / total_weight) * 20)


# ── Turn builder helper ────────────────────────────────────────────────────────

def _turns(raw: list[tuple[str, int, str]]) -> list[dict]:
    return [
        {"turn": i + 1, "speaker": spk, "timestamp_seconds": ts, "text": txt}
        for i, (spk, ts, txt) in enumerate(raw)
    ]


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: EXCELLENT (syn_001–003)
# All dims 4–5. No violations. Patient callers.
# ══════════════════════════════════════════════════════════════════════════════

def _syn_001(ctx: dict) -> dict:
    """Excellent: cooperative patient, insurance confirmed, all dims 4-5."""
    a, c = f"{ctx['agent_first']}", f"{ctx['caller_first']}"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How can I help you today?"),
        ("caller", 4, f"Hi... my name is {c}. I've been struggling with alcohol for a couple of years now and I think — I think I finally need to get some real help."),
        ("agent", 14, f"Thank you so much for reaching out, {c}. I can hear that took a lot of courage. You don't have to figure this out alone — that's exactly why we're here. Can you tell me a little about what's been going on?"),
        ("caller", 28, "It's been getting worse. I'm drinking every day, sometimes starting in the morning. My wife is scared and honestly so am I."),
        ("agent", 42, f"I really appreciate you sharing that with me. What you're describing — recognising the pattern and being scared — that actually tells me a lot about how serious you are about getting better. That's a strength, {c}. Let me ask — are you having any physical symptoms right now? Shaking, sweating, anything like that?"),
        ("caller", 62, "Not right now. I had my last drink a few hours ago."),
        ("agent", 70, "Okay, good to know. So no immediate withdrawal symptoms at this moment. And is this something you're looking to address soon, or are you in a place where today or this week feels more urgent?"),
        ("caller", 82, "I'd like to start as soon as possible. My wife and I talked last night and we agreed I need to do this now."),
        ("agent", 92, f"I'm glad you have that support at home — that makes a real difference. Let me get a few more details so we can figure out the right level of care for you. How long has the daily drinking been going on?"),
        ("caller", 104, "About two years, maybe a bit more. It got a lot worse after I lost my job eighteen months ago."),
        ("agent", 114, "I understand. And have you ever been through any treatment before — detox, rehab, outpatient, anything like that?"),
        ("caller", 122, "I did an IOP program about four years ago. It helped for a while but I eventually went back."),
        ("agent", 132, "That's really useful context. Prior treatment history helps our clinical team put together the right plan. Now let me ask about insurance — do you have coverage right now?"),
        ("caller", 142, f"Yes, through my wife's employer. It's {carrier}."),
        ("agent", 148, f"Great. Do you happen to have the insurance card handy? I'll need the member ID and group number."),
        ("caller", 154, f"Sure, hold on. Member ID is {mid} and the group number is {grp}."),
        ("agent", 168, f"Perfect, thank you. So {carrier}, member ID {mid}, group {grp}. Let me note that down. Our admissions coordinator will verify your benefits — typically we can get that back to you within a couple of hours. Have you or your wife had any questions about cost or what coverage looks like?"),
        ("caller", 188, "A little. We weren't sure what insurance would cover."),
        ("agent", 196, "Totally understandable. Once we verify, we'll walk you through exactly what your plan covers and what, if anything, would be your responsibility. We never want cost to be the thing that gets in the way. There are also financing options if needed, but let's see what the verification shows first."),
        ("caller", 214, "That's reassuring. Thank you."),
        ("agent", 218, f"Of course. {c}, based on what you've shared — two-year history, daily use, prior IOP — our clinical team will likely want to do a full assessment to determine whether detox is the right starting point or whether an IOP or PHP level of care fits best. Does that make sense?"),
        ("caller", 238, "Yes, that makes sense. I just want to do this right this time."),
        ("agent", 244, "And you will. Here's what happens next: I'm going to send you a confirmation email right now with our address, what to expect, and a short intake form. Our benefits coordinator will call you within two hours with your insurance verification results. Can you take a call this afternoon?"),
        ("caller", 262, "Yes, absolutely."),
        ("agent", 266, f"Perfect. You'll hear from us by three o'clock today. And {c} — reaching out today was the right call. We'll take it from here."),
        ("caller", 276, "Thank you. I really appreciate it."),
        ("agent", 280, "Of course. Take care, and we'll talk soon."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 4,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_001",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 290,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_001",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "cooperative", "insurance-confirmed", "prior-iop"],
            "coaching_notes": "Exemplary across all scored dimensions. Agent used caller's name consistently, completed full clinical screen, and gave a precise next-step with timing. Minor: could have explicitly named the IOP/PHP distinction when describing level-of-care options.",
        },
    }


def _syn_002(ctx: dict) -> dict:
    """Excellent: nervous patient, needs reassurance, no objections, urgency triage N/A."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}. This is {a}, how can I help you?"),
        ("caller", 4, f"Um, hi. I'm {c}. I... I almost didn't call. I've been trying to get the nerve up for weeks."),
        ("agent", 14, f"I'm really glad you did, {c}. It takes a lot to make this call and I want you to know there's no pressure here. Take your time. What's going on?"),
        ("caller", 26, "I've been using meth on and off for about three years. It's been more on than off lately. I'm not sleeping. I'm losing weight. My friends have noticed."),
        ("agent", 40, f"Thank you for trusting me with that. Three years is a long time to carry this, and the fact that you reached out today — that matters. {c}, I want to make sure I understand what you're going through. Are you using every day at this point?"),
        ("caller", 58, "Most days. Sometimes I go two or three days without and then I crash hard."),
        ("agent", 66, "Okay. And when you crash — are you getting any sleep during those periods, or is it pretty rough?"),
        ("caller", 74, "Pretty rough. I sleep a lot but it's not good sleep."),
        ("agent", 82, "That's a really common pattern with stimulant use. Our clinical team will want to do a proper assessment, but what you're describing — the daily use, the crash cycles, the weight loss — those are things they'll be looking at carefully. Have you ever tried to stop or get treatment before?"),
        ("caller", 100, "No. This is the first time I've told anyone outside of my close friends."),
        ("agent", 108, f"Then this is a really significant step. I want to honour that. {c}, are you in a safe place right now? Any immediate concerns — medical, housing, safety?"),
        ("caller", 118, "I'm okay. I have an apartment. It's just — it's getting bad enough that I know I need to do something."),
        ("agent", 128, "That self-awareness is important. Let me ask — are you thinking about this as something you want to address in the next few days, or is this more of an exploratory call right now?"),
        ("caller", 140, "I want to actually do it. I've been thinking about it for too long already."),
        ("agent", 148, "Good. Let's make that happen. Do you have insurance coverage right now?"),
        ("caller", 154, f"Yes, through work. I have {carrier}."),
        ("agent", 160, "Great. Do you have your card available with the member ID and group number?"),
        ("caller", 166, f"Yeah. Member ID is {mid}, group number {grp}."),
        ("agent", 178, f"Thank you. {carrier}, {mid}, group {grp}. Our team will verify your benefits today. Based on your coverage and what you've shared, they'll be able to tell you what residential or outpatient options look like. Is there anything you're worried about in terms of taking this step?"),
        ("caller", 196, "I'm scared of what people will think. My job, my family."),
        ("agent", 204, f"That fear is completely valid. A lot of people share it. What I can tell you is that confidentiality is something we take very seriously — what happens here stays here. And the people who love you, {c}? Most of them will be relieved, not judgmental. Our counsellors can also help you think through how to have those conversations when you're ready."),
        ("caller", 226, "That helps. Thank you."),
        ("agent", 230, "Of course. Here's what we'll do next: I'm going to send you a short intake form and a confirmation email right now. Our benefits team will call you within ninety minutes with the verification results. You'll have a clear picture of your options by end of business today. Does that work?"),
        ("caller", 248, "Yes, that's good."),
        ("agent", 252, f"Perfect. I'll get that email out to you in the next five minutes. And {c} — you made the right call today. We'll take it from here."),
        ("caller", 262, "Thank you so much."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 5,
        "clinical_screening": 5,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_002",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 272,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_002",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "nervous", "first-time-seeking-help", "stimulant-use"],
            "coaching_notes": "Perfect empathy and rapport. Agent never pushed, gave space, and addressed confidentiality concern organically. Urgency triage scored 3 (acceptable) — caller is motivated but no same-day urgency, correctly handled.",
        },
    }


def _syn_003(ctx: dict) -> dict:
    """Excellent: self-pay patient, agent pivots smoothly to financing. Insurance dim N/A."""
    a, c = ctx["agent_first"], ctx["caller_first"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I'm calling about getting into a program. I've been dealing with opioid use — mostly prescription pills, but it's gotten out of hand."),
        ("agent", 14, f"Thank you for reaching out, {c}. That takes courage and I'm glad you called. Tell me — how long has this been going on?"),
        ("caller", 22, "About eighteen months. It started after a back surgery. I was taking the pills for the pain and then I couldn't stop."),
        ("agent", 32, f"That's a very common path and it doesn't make it your fault. You got trapped by something that started as medical treatment. {c}, are you still taking them daily?"),
        ("caller", 44, "Yes. Every day. I've tried to cut down but I get sick when I do."),
        ("agent", 52, "When you say sick — are you talking about withdrawal symptoms? Sweating, muscle aches, nausea?"),
        ("caller", 58, "All of that, yes. It's pretty bad."),
        ("agent", 66, "Okay. That's really important information. Opioid withdrawal can be medically serious and our clinical team will want to assess whether medically-supervised detox is the right first step before any IOP or residential program. Have you had any prior treatment for this?"),
        ("caller", 82, "No. I've been trying to handle it on my own."),
        ("agent", 88, "I understand. And coming in now, before it gets worse, is the right move. Do you have health insurance coverage we could check?"),
        ("caller", 96, "That's actually why I'm calling now — I lost my insurance when I left my job last month. I'm self-pay."),
        ("agent", 104, f"Got it, thank you for telling me. Self-pay is something we work with regularly and I don't want cost to be what stands between you and getting help. Let me walk you through what that looks like. We have a sliding-scale fee structure based on income, and we also work with a financing partner — CareCredit — that offers low-interest payment plans. Some people are also surprised to find they qualify for state-funded programs. Can I ask roughly what your situation looks like financially, so I can point you to the right option?"),
        ("caller", 134, "I have some savings. I can probably cover some of it. But I'm worried about the full cost."),
        ("agent", 144, "That's completely fair. Here's what I'd suggest: let me connect you with our financial counsellor who can walk through the actual numbers with you — the sliding scale, the financing, and the state program eligibility. You'll have a clear picture of what you'd actually owe before you commit to anything. Does that work?"),
        ("caller", 162, "Yes, that would be helpful."),
        ("agent", 166, f"Good. In the meantime, let me ask a few more questions so we have the clinical picture ready when you talk to the financial team. {c}, you mentioned withdrawal symptoms when you try to cut down — how recently did you last try to stop?"),
        ("caller", 180, "About two weeks ago. I made it about a day and a half before I had to take something."),
        ("agent", 190, "That tells me the physical dependence is significant. Our clinical team will likely recommend starting with MAT — medication-assisted treatment — which uses medications like buprenorphine to manage withdrawal safely. That's something the assessment will determine. Are there any other health concerns, mental health or otherwise, that we should know about?"),
        ("caller", 210, "I've been pretty depressed. I don't know if that's the opioids or just my situation."),
        ("agent", 222, "It's likely both, and we treat them together — that's what dual diagnosis care looks like. Our team is experienced with co-occurring depression and substance use. Here's the plan: I'm going to flag you for a call from our financial counsellor within the hour, and I'll also get our clinical intake team ready with the information you've shared today. Can you take a call in the next sixty minutes?"),
        ("caller", 246, "Yes, I'm free."),
        ("agent", 250, f"Perfect. You'll hear from us within the hour. {c}, opioid withdrawal with the symptoms you're describing really does need professional support — you don't have to white-knuckle this. We'll get you the right help."),
        ("caller", 264, "Thank you. That means a lot."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": None,
        "clinical_screening": 4,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_003",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 274,
            "caller_type": "patient",
            "campaign_source": "referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_003",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "self-pay", "opioid-use-disorder", "withdrawal-symptoms", "dual-diagnosis-noted"],
            "coaching_notes": "Insurance verification correctly scored N/A — caller is self-pay and agent immediately pivoted to financing and sliding scale. Objection handling exemplary. Clinical screen strong. Urgency triage 3: withdrawal symptoms present but not acute crisis level.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: WEAK (syn_004–006)
# syn_004, 005: compliance violations (dim 8 = 0)
# syn_006: coaching gaps only, borderline call
# ══════════════════════════════════════════════════════════════════════════════

def _syn_004(ctx: dict) -> dict:
    """Weak: DIAG_CLAIM violation. Agent makes diagnostic statement. Dim 8 = 0."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, yeah, I'm calling because... I think I have a problem with drinking. My name is {c}."),
        ("agent", 10, "Okay. How long has this been going on?"),
        ("caller", 14, "Probably four or five years. But it's gotten worse in the last year."),
        ("agent", 20, "How much are you drinking a day?"),
        ("caller", 24, "Maybe a bottle of wine at night, sometimes more."),
        ("agent", 30, "And are you drinking in the morning?"),
        ("caller", 34, "Not usually. Occasionally on weekends."),
        ("agent", 40, "Okay. Based on what you're telling me, it sounds like you have a dependency problem that's going to need professional treatment."),
        ("caller", 48, "Yeah, I figured as much."),
        ("agent", 52, "Do you have insurance?"),
        ("caller", 56, f"Yes. {carrier}."),
        ("agent", 60, "Member ID?"),
        ("caller", 64, f"{mid}."),
        ("agent", 68, "Group number?"),
        ("caller", 72, f"{grp}."),
        ("agent", 76, "Okay. We'll verify that. Any prior treatment?"),
        ("caller", 80, "No."),
        ("agent", 84, "Okay. Someone will call you back about availability."),
        ("caller", 88, "Do you know when?"),
        ("agent", 92, "Probably today or tomorrow."),
        ("caller", 96, "Okay. Should I do anything in the meantime?"),
        ("agent", 100, "Just wait for our call. We'll figure out the details then."),
        ("caller", 106, "Alright. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 2,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 2,
        "compliance_language": 0,
    }

    return {
        "call_id": "syn_004",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 116,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_004",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": True,
            "expected_flags": ["DIAG_CLAIM"],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "compliance-violation", "diagnostic-claim", "poor-empathy", "vague-next-step"],
            "coaching_notes": "COMPLIANCE VIOLATION: 'it sounds like you have a dependency problem' is a diagnostic claim. Agent stayed in intake role on language but crossed the line with this statement. Beyond compliance: flat tone throughout, no empathy opening, clinical screen incomplete (missed severity, withdrawal, prior treatment), next step is vague ('today or tomorrow'). Major coaching opportunity.",
        },
    }


def _syn_005(ctx: dict) -> dict:
    """Weak: OUTCOME_GUARANTEE violation. Agent promises recovery outcome. Dim 8 = 0."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. What can I help you with?"),
        ("caller", 6, f"Hi. I'm {c}. I'm calling because I've been struggling with cocaine use and my family is really worried about me. I'm worried about me too."),
        ("agent", 18, "I understand. How long has this been going on?"),
        ("caller", 24, "About two years. It's daily now."),
        ("agent", 28, "Okay. We have a really great program here and I can tell you — our 30-day program gets people better. You'll come out of here a completely different person."),
        ("caller", 40, "That sounds good. That's what I need."),
        ("agent", 44, "Absolutely. Do you have insurance?"),
        ("caller", 48, f"Yes, {carrier}."),
        ("agent", 52, "Member ID and group number?"),
        ("caller", 56, f"Member ID {mid}, group {grp}."),
        ("agent", 66, "Great. And have you had any previous treatment?"),
        ("caller", 70, "I did a 30-day residential about three years ago."),
        ("agent", 74, "And you're back to using — okay. Well this time will be different, I promise. Our program has an excellent success rate."),
        ("caller", 84, "I hope so. I'm ready to commit."),
        ("agent", 88, "That's what we need to hear. Is there anything about cost you're worried about?"),
        ("caller", 94, "A little. I don't know what insurance covers."),
        ("agent", 98, "We'll verify your benefits and let you know. Don't worry, we'll get you taken care of."),
        ("caller", 106, "Okay. What happens next?"),
        ("agent", 110, "Someone from our admissions team will call you. Probably in the next day or so."),
        ("caller", 118, "Do you have a more specific time?"),
        ("agent", 122, "I'll put you on the list. You'll hear from us."),
        ("caller", 128, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 3,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 2,
        "family_caller_handling": None,
        "objection_handling": 3,
        "next_step_clarity": 2,
        "compliance_language": 0,
    }

    return {
        "call_id": "syn_005",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 138,
            "caller_type": "patient",
            "campaign_source": "referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_005",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": True,
            "expected_flags": ["OUTCOME_GUARANTEE"],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "compliance-violation", "outcome-guarantee", "prior-treatment", "stimulant-use"],
            "coaching_notes": "COMPLIANCE VIOLATION: 'our 30-day program gets people better' and 'You'll come out of here a completely different person' are outcome guarantees. Also: 'this time will be different, I promise' and 'excellent success rate' reinforce the violation. Clinical screen shallow — did not explore severity, withdrawal risk, or co-occurring issues. Next step vague.",
        },
    }


def _syn_006(ctx: dict) -> dict:
    """Weak (borderline): coaching gaps only, no compliance violation. Dims 2-3 range. BORDERLINE."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid = ctx["carrier"], ctx["member_id"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, {a} speaking."),
        ("caller", 4, f"Hi, I'm {c}. I'm looking into treatment for alcohol. My doctor suggested I call."),
        ("agent", 10, "Okay, sure. How much are you drinking?"),
        ("caller", 14, "A lot. Pretty much every night. A six-pack or more."),
        ("agent", 20, "Every night. Okay. Do you have insurance?"),
        ("caller", 24, f"Yes, {carrier}."),
        ("agent", 28, "Do you have your member ID?"),
        ("caller", 32, f"Yes, it's {mid}."),
        ("agent", 38, "And the group number?"),
        ("caller", 42, "I don't have that with me right now."),
        ("agent", 46, "That's okay. We'll try to look it up. Anything else about your situation I should know?"),
        ("caller", 54, "I mean, it's been going on for a few years. I tried to cut back on my own but it didn't really work."),
        ("agent", 64, "Got it. Any prior treatment programs?"),
        ("caller", 68, "No, nothing formal."),
        ("agent", 72, "Okay. And are you looking to come in soon or still deciding?"),
        ("caller", 78, "I think I want to do it but I'm nervous about it. I have kids, so I'm wondering how that works."),
        ("agent", 88, "We can work around schedules. Our outpatient programs allow people to be home in the evenings."),
        ("caller", 96, "That's good to know. I'm worried about the cost too."),
        ("agent", 102, "Your insurance should cover most of it. We'll verify."),
        ("caller", 108, "Okay. So what do I do now?"),
        ("agent", 114, "We'll have someone call you to set something up."),
        ("caller", 118, "When?"),
        ("agent", 122, "Within the next day or two."),
        ("caller", 126, "Okay. Is there anything I need to have ready?"),
        ("agent", 130, "Just your insurance card."),
        ("caller", 134, "Alright. Thanks."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 2,
        "clinical_screening": 2,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 2,
        "next_step_clarity": 3,
        "compliance_language": 4,
    }

    return {
        "call_id": "syn_006",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 144,
            "caller_type": "patient",
            "campaign_source": "physician_referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_006",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "borderline", "coaching-gaps", "no-violation", "parent-concern"],
            "coaching_notes": "BORDERLINE: Urgency triage and next-step clarity are borderline 2-3 — graders may disagree. No compliance violation. Major coaching gaps: no warm empathy opening, clinical screen minimal (missed withdrawal history, severity, duration), group number not escalated as important, objection about kids handled with a single sentence and dropped, cost concern dismissed with 'should cover most of it'. Next step is vague but timing is given.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: FAMILY_CALLER (syn_007–009)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_007(ctx: dict) -> dict:
    """Family caller: excellent. Spouse calling for partner. Agent handles consent and distress well."""
    a = ctx["agent_first"]
    caller_first, caller_last = ctx["caller_first"], ctx["caller_last"]
    patient_first = "Jamie"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi. My name is {caller_first} {caller_last}. I'm calling about my husband. His name is {patient_first}. I'm... I'm not sure where to start."),
        ("agent", 14, f"Take a breath, {caller_first}. You're doing the right thing by calling. I can hear how hard this is. Can you tell me what's been going on?"),
        ("caller", 26, f"He's been drinking heavily for over a year. It's gotten to the point where he can't stop. He's tried a few times. Last week he had a seizure and the doctor at the ER told us he needs to go somewhere that can handle detox."),
        ("agent", 44, f"I'm so sorry you and {patient_first} have been through that. A seizure during withdrawal is serious and I want you to know you've called the right place. We have medically supervised detox. Before I go further — is {patient_first} aware that you're calling today?"),
        ("caller", 62, "Yes. He said he's ready. He's the one who asked me to call because he was too scared to do it himself."),
        ("agent", 70, f"That's really important to know. Because {patient_first} is an adult, anything we do in terms of treatment will require his consent — and because he's already expressed that consent to you and wants this, that makes this call something we can definitely work with. I'll need to speak with him at some point today to confirm, but let's get started with what you can share."),
        ("caller", 92, "Of course. Whatever you need."),
        ("agent", 96, f"Thank you for understanding. {caller_first}, I want to acknowledge — this has clearly been frightening for you too. Spouses and families go through a lot when a loved one is struggling. How are you holding up?"),
        ("caller", 110, "Honestly not great. I've been holding everything together for a year and I'm exhausted."),
        ("agent", 118, f"That's completely understandable and valid. We actually have resources for family members as well — our family counsellor can speak with you separately if that would help. We'll come back to that. Right now let's focus on getting {patient_first} the right help. Can you tell me about the drinking — how much, how often?"),
        ("caller", 138, "He was drinking a fifth a day at his worst. Since the ER he's cut back but he's still drinking to avoid withdrawal."),
        ("agent", 152, "Okay. So he's currently using to manage withdrawal symptoms — that's actually a sign that he needs medically supervised detox before any residential or outpatient program. Does he have any history of prior treatment?"),
        ("caller", 162, "No. This is the first time we're looking at this."),
        ("agent", 168, f"Understood. And {patient_first}'s insurance — is he covered under your plan or his own?"),
        ("caller", 174, f"His own, through his employer. It's {carrier}."),
        ("agent", 180, "Do you have his member ID and group number?"),
        ("caller", 186, f"Yes, I have his card. Member ID {mid}, group {grp}."),
        ("agent", 198, f"Perfect. I have that noted. Here's what I'd like to do: I'll verify {patient_first}'s benefits today and have someone from our admissions team call both of you — ideally with him present — within two hours. That way he can give verbal consent on the call and we can get the intake process started. Does he have a phone he can take a call on?"),
        ("caller", 220, "Yes. We'll both be here."),
        ("agent", 226, f"Wonderful. You'll hear from us by two o'clock this afternoon. And {caller_first} — what you're doing for your husband right now is an act of love. Please don't forget to take care of yourself too."),
        ("caller", 240, "Thank you. That really helps."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 3,
        "urgency_triage": 4,
        "family_caller_handling": 5,
        "objection_handling": None,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_007",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 250,
            "caller_type": "family_member",
            "campaign_source": "er_referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_007",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["family-caller", "spouse", "consent-confirmed", "withdrawal-risk", "prior-seizure"],
            "coaching_notes": "Exemplary family caller handling: consent addressed immediately, patient's autonomy respected, family member's distress acknowledged, family resources offered. Clinical screen limited by family-caller context (scored 3). Next step is precise with timing and format.",
        },
    }


def _syn_008(ctx: dict) -> dict:
    """Family caller: BORDERLINE. Parent calling for adult child. Consent awkward, distress partially acknowledged."""
    a = ctx["agent_first"]
    caller_first = ctx["caller_first"]
    patient_first = "Alex"
    carrier, mid = ctx["carrier"], ctx["member_id"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {caller_first}. I'm calling about my son. His name is {patient_first}. He's 24. He's been using heroin."),
        ("agent", 12, "Okay. Does your son know you're calling?"),
        ("caller", 18, "No. He's at work. I wanted to find out about options before I talk to him tonight."),
        ("agent", 26, "I see. Well, since he's an adult, we'd need to talk to him directly before we can move forward with anything."),
        ("caller", 36, "Of course. I just — I need to know what to tell him. What to say."),
        ("agent", 42, "Right. So what's been going on with him?"),
        ("caller", 48, "He started using about two years ago. It's been heroin. He's been doing well at his job but I can see it's getting worse. He's losing weight. He fell asleep at dinner last week."),
        ("agent", 60, "Does he have any health insurance through his job?"),
        ("caller", 66, f"Yes, through work. It's {carrier}. I have his information here — member ID is {mid}."),
        ("agent", 74, "Okay. Do you have a group number?"),
        ("caller", 80, "I don't think I have that."),
        ("agent", 84, "That's okay, we can try to pull it up. Is he using every day?"),
        ("caller", 90, "I believe so. He won't talk to me about it directly but the signs are there."),
        ("agent", 98, "Has he ever tried to stop or get treatment?"),
        ("caller", 104, "Not that I know of."),
        ("agent", 108, "Okay. So what would you like to happen?"),
        ("caller", 114, "I want to know how to get him into your program. What do I say to him? He gets defensive when I bring it up."),
        ("agent", 124, "You can let him know that you've done the research and there's a place that can help. He'll need to call himself or come in for an assessment. We can't hold a spot without him being involved."),
        ("caller", 138, "I understand that. But is there anything you can do to help me prepare for that conversation?"),
        ("agent", 144, "Not really — that's going to depend on him. But if he's willing to call, we can get things moving quickly."),
        ("caller", 152, "Okay. And what about MAT? I've heard that helps with opioids."),
        ("agent", 160, "Yes, we offer medication-assisted treatment. Our clinical team will assess whether that's right for him."),
        ("caller", 168, "That's good. I'm just really scared for him."),
        ("agent", 174, "That's understandable. Have him give us a call when he's ready."),
        ("caller", 180, "Alright. Thank you."),
    ])

    scores = {
        "empathy_rapport": 3,
        "insurance_verification": 2,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": 2,
        "objection_handling": 3,
        "next_step_clarity": 3,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_008",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 190,
            "caller_type": "family_member",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_008",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["family-caller", "parent", "patient-unaware", "opioid-use-disorder", "borderline"],
            "coaching_notes": "BORDERLINE: family_caller_handling and insurance_verification are borderline 2-3. Consent framing was technically correct (agent noted patient needs to call) but cold — no warmth around why consent matters. Family member's fear ('I'm really scared') received a single dismissive sentence. Did not offer family counsellor resources. Insurance handling: missing group number not pursued. Objection handling borderline — 'not really' to the family preparation question was unhelpful.",
        },
    }


def _syn_009(ctx: dict) -> dict:
    """Family caller: poor. Sibling calling urgently. No HIPAA framing, distress ignored."""
    a = ctx["agent_first"]
    caller_first = ctx["caller_first"]
    patient_first = "Marcus"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}."),
        ("caller", 4, f"Hi, I need help. My brother — his name is {patient_first} — he's in really bad shape. He told me last night he wants to get help and I'm calling on his behalf. My name is {caller_first}."),
        ("agent", 14, "What's wrong with him?"),
        ("caller", 18, "He's been on meth for two years. Last night he had a breakdown. He's never opened up like this before and I'm afraid if I don't act now he'll change his mind."),
        ("agent", 28, "Okay. What's his date of birth?"),
        ("caller", 32, "March 14th, 1993."),
        ("agent", 36, "And his insurance?"),
        ("caller", 40, f"It's {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 52, "Has he used anything today?"),
        ("caller", 56, "I don't know. Probably."),
        ("agent", 60, "Does he have any mental health issues?"),
        ("caller", 64, "He's been depressed for a long time. That's part of why he started using, I think."),
        ("agent", 70, "Any medical conditions?"),
        ("caller", 74, "Not that I know of."),
        ("agent", 78, "Okay. We'll need him to call us or come in."),
        ("caller", 82, "He's not going to do that on his own. Can you help me figure out how to get him there? He's willing right now — tonight."),
        ("agent", 90, "We can't admit someone without them presenting themselves. He needs to call."),
        ("caller", 96, "I understand that. But is there anything I can do? Any guidance on how to talk to him?"),
        ("agent", 102, "Just bring him in or have him call."),
        ("caller", 108, "Is there a crisis line or an interventionist you work with?"),
        ("agent", 114, "We don't have that here. He can call when he's ready."),
        ("caller", 120, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 2,
        "family_caller_handling": 1,
        "objection_handling": 2,
        "next_step_clarity": 2,
        "compliance_language": 4,
    }

    return {
        "call_id": "syn_009",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 130,
            "caller_type": "family_member",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_009",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["family-caller", "sibling", "no-consent-framing", "urgent-window", "dual-diagnosis-noted"],
            "coaching_notes": "Poor family caller handling: agent collected patient's DOB and insurance without any consent framing. Sibling's distress ('I'm afraid', urgent window) entirely ignored. No warmth or acknowledgement throughout. Did not offer crisis resources or intervention referral when directly asked — that's a missed escalation opportunity. Should have offered to speak with patient directly.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: URGENCY (syn_010–012)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_010(ctx: dict) -> dict:
    """Urgency: active withdrawal symptoms. Agent correctly escalates. Dim 4 = 5."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, my name is {c}. I need help. I've been trying to stop drinking and I've been shaking for two days and I threw up this morning and I'm scared."),
        ("agent", 14, f"{c}, I hear you and I'm glad you called. What you're describing — the shaking, the vomiting, two days in — those are withdrawal symptoms and they can be medically serious. I want to make sure you're safe. Are you alone right now?"),
        ("caller", 30, "Yes. My roommate is at work."),
        ("agent", 36, "Okay. Have you had any seizures before when you've tried to stop drinking, or any hallucinations — seeing or hearing things that aren't there?"),
        ("caller", 48, "No seizures. But last night I thought I heard someone in the apartment and there was nobody there."),
        ("agent", 58, f"{c}, that's an early sign of alcohol withdrawal that we take very seriously. I want to be direct with you: alcohol withdrawal at this stage can escalate and it needs medical supervision. I want to get you into our detox unit today. Can you get here, or do you need us to help arrange transport?"),
        ("caller", 76, "I can drive. I think."),
        ("agent", 82, "I'd actually recommend not driving given what you're describing — your coordination may be affected. Do you have someone who could bring you, or can you take a rideshare?"),
        ("caller", 92, "I can call an Uber."),
        ("agent", 96, f"Perfect. Here's what I need from you: call the Uber right after we hang up. Our address is 4800 North Lakeview Drive. When you arrive, tell the front desk your name and that you spoke with {a} this morning and that this is urgent. Do you have health insurance?"),
        ("caller", 114, f"Yes, {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 126, f"I have that. I'm putting a note in right now with your name, insurance, and that you're coming in today. Our detox team will be expecting you. {c}, I want you to keep the Uber app open and call us back if anything gets worse before you arrive — new symptoms, chest pain, confusion. Our number is on your caller ID. Can you repeat the address back to me?"),
        ("caller", 150, "4800 North Lakeview Drive."),
        ("agent", 154, "That's right. How are you feeling right now, in this moment?"),
        ("caller", 158, "Shaky. Scared. But a little relieved."),
        ("agent", 164, f"Good. Relief is the right feeling. You did the right thing calling. We'll take it from here. I'll stay on the line until you've called the Uber — are you able to do that right now?"),
        ("caller", 176, "Yes. Opening the app now."),
        ("agent", 180, "Good. I'm right here."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 5,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_010",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 190,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_010",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": True,
            "scenario_tags": ["patient-caller", "active-withdrawal", "hallucinations", "same-day-admit", "crisis-protocol-activated"],
            "coaching_notes": "Exemplary urgency triage: agent immediately identified withdrawal severity, asked the right escalation questions (seizure history, hallucinations), recommended against driving, gave a precise address with name-check-in instructions, and stayed on the line. Text-book crisis response.",
        },
    }


def _syn_011(ctx: dict) -> dict:
    """Urgency: agent misses suicidal ideation signal. Dim 4 = 0. Escalation required."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, my name is {c}. I've been struggling with alcohol and I think I need help."),
        ("agent", 10, "Of course. How long has this been going on?"),
        ("caller", 14, "Years. But it's been really bad lately. I don't know, I just... I don't really see the point in a lot of things anymore."),
        ("agent", 24, "How much are you drinking?"),
        ("caller", 28, "A lot. Almost a bottle of vodka a day."),
        ("agent", 34, "Every day?"),
        ("caller", 38, "Pretty much."),
        ("agent", 42, "Okay. And are you looking to come in soon?"),
        ("caller", 48, "I guess. I'm not really sure what I'm looking for. I just feel like nothing's going to get better anyway."),
        ("agent", 56, "I understand. Do you have insurance?"),
        ("caller", 62, f"Yes, {carrier}. ID is {mid}, group {grp}."),
        ("agent", 74, "Okay. Any prior treatment?"),
        ("caller", 80, "No."),
        ("agent", 84, "And what's your availability like? Could you come in this week?"),
        ("caller", 90, "I don't know. Maybe. I just don't have a lot of energy for anything lately."),
        ("agent", 98, "We can schedule a time that works for you. Let me get someone from admissions to call you back about next steps."),
        ("caller", 106, "Okay."),
        ("agent", 110, "We'll be in touch. Thanks for calling."),
        ("caller", 114, "Okay. Bye."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 0,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 2,
        "compliance_language": 4,
    }

    return {
        "call_id": "syn_011",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 124,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_011",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": True,
            "scenario_tags": ["patient-caller", "missed-urgency", "passive-si", "critical-coaching-opportunity"],
            "coaching_notes": "CRITICAL MISSED URGENCY: Caller stated 'I don't really see the point in a lot of things anymore' and 'nothing's going to get better anyway' and 'don't have a lot of energy for anything' — passive suicidal ideation signals that required crisis protocol. Agent moved to insurance without pause. Urgency triage = 0 (unacceptable). This call requires immediate coaching review and should not happen again. Clinical screen also inadequate.",
        },
    }


def _syn_012(ctx: dict) -> dict:
    """Urgency: correctly assessed as low. Caller researching for future. Urgency triage N/A."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How can I help you?"),
        ("caller", 4, f"Hi, I'm {c}. I'm actually calling to do some research. I have a colleague who I think is struggling with alcohol and I want to understand what options are out there before I talk to them. I'm not sure if they'd be open to treatment."),
        ("agent", 16, f"That's a thoughtful thing to do, {c}. I'm happy to walk you through what we offer. Just so I understand the situation — you're gathering information on behalf of someone else, not for yourself?"),
        ("caller", 30, "That's right. They don't know I'm calling."),
        ("agent", 36, "Understood. A few things to know: ultimately your colleague would need to reach out themselves or come in, since any treatment is voluntary. But knowing your options helps you have a better conversation with them. What do you already know about what's going on with them?"),
        ("caller", 48, "They drink every day. I've noticed them coming back from lunch with alcohol on their breath, and they've mentioned not sleeping well."),
        ("agent", 60, "That does sound like a pattern worth addressing sooner rather than later, though it sounds like there's no immediate crisis situation right now — more of a concerning escalation over time."),
        ("caller", 72, "Right, nothing acute. I just want to be prepared."),
        ("agent", 78, "That makes sense. Let me tell you what we offer: we have outpatient programs — IOP, which is three evenings a week — and PHP, which is more intensive, five days a week. For someone who is employed and functional, IOP is often the starting point. We also have a professional track that's confidential and designed for people who are concerned about workplace implications."),
        ("caller", 104, "That's really helpful. What about insurance — would theirs likely cover this?"),
        ("agent", 112, "Most major insurance plans cover substance use treatment. If your colleague reaches out, we can verify their specific benefits in about an hour. We never want cost to be a barrier."),
        ("caller", 122, "That's good to know. Is there any literature or anything I could share with them?"),
        ("agent", 128, "Absolutely. I can email you our general program overview — it's designed for exactly this kind of conversation. What's your email address?"),
        ("caller", 136, "It's the one I called from, actually."),
        ("agent", 142, "I'll pull that from the caller ID and send it within the hour. And if you'd like to talk through how to approach that conversation with your colleague, our family and support line is open — no charge, just guidance. Would that be helpful?"),
        ("caller", 154, "Yes, actually. That would be helpful."),
        ("agent", 160, "I'll include that number in the email as well. You're being a good friend, {c}. Let me know if anything changes or if they're ready to reach out directly."),
        ("caller", 170, "Thank you so much."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": None,
        "family_caller_handling": None,
        "objection_handling": 3,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_012",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 180,
            "caller_type": "third_party_inquiry",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_012",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["third-party-inquiry", "no-urgency", "urgency-triage-na", "professional-track-mentioned"],
            "coaching_notes": "Urgency triage correctly scored N/A — caller explicitly researching for future, no urgency signals present. Agent correctly identified this and responded proportionally. Strong knowledge of program levels (IOP/PHP). Objection handling scored 3 — answered the insurance question but didn't proactively address the 'will they be open to it' question the caller hinted at.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: OBJECTION_HEAVY (syn_013–015)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_013(ctx: dict) -> dict:
    """Objection heavy: excellent. Cost and readiness objections handled perfectly."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How are you doing today?"),
        ("caller", 6, f"Hi. I'm {c}. Honestly not great. I've been thinking about calling for a while but kept talking myself out of it."),
        ("agent", 16, f"I'm really glad you didn't talk yourself out of it today, {c}. What's going on?"),
        ("caller", 24, "I've been drinking pretty heavily for about three years. I know I need to stop. I just keep finding reasons not to deal with it."),
        ("agent", 34, f"I hear that. Sometimes the hardest part is making that first call, and you've already done it. What kind of reasons have been coming up for you?"),
        ("caller", 46, "Money, mostly. I don't know if I can afford this. And honestly I'm not sure I'm ready. What if I go and it doesn't work?"),
        ("agent", 58, f"Those are really honest things to say and I want to take them seriously. Let's start with the readiness piece, because I think it matters most. The fact that you've been thinking about this for a while and you still picked up the phone — that actually tells me something. Can I ask: what made today the day you finally called?"),
        ("caller", 80, "My daughter said something to me last night. She's eight. She said she was scared of me when I drink. I didn't sleep after that."),
        ("agent", 94, f"Thank you for sharing that. That's a profound moment — and you're taking it seriously, which is what matters. {c}, 'ready' doesn't always mean feeling confident. Sometimes it means being willing to try even when you're scared. And you're clearly willing. Now let's talk about cost, because I don't want that to be the thing that stops you."),
        ("caller", 116, "I have insurance but I don't know what it covers."),
        ("agent", 122, "That's the right first step. Do you have your insurance card? I can note your information and have our benefits team give you an exact answer within two hours — before you commit to anything."),
        ("caller", 130, f"Sure. I have {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 144, f"Perfect. I've noted that. Now — most plans cover substance use treatment at a significant level, often 80 to 100 percent once your deductible is met. But if there is a gap, we also have a sliding-scale fee and financing through CareCredit. The point is: we have never turned someone away because of cost alone. That's not who we are."),
        ("caller", 168, "Okay. That helps to hear."),
        ("agent", 174, "And the 'what if it doesn't work' question — I want to answer that honestly. No one can promise you it will. What I can promise is that not trying guarantees the outcome you're trying to avoid. Treatment gives you a real chance, and we'll work with you to find the right level of care — whether that's outpatient so you can be home with your daughter, or something more intensive."),
        ("caller", 198, "The outpatient piece matters. I can't be away from her."),
        ("agent", 204, f"Then we build around that. Our IOP program is three evenings a week. You'd be home every night. Let me have our admissions coordinator call you this afternoon with your benefits information and walk you through that schedule. Can you take a call between two and four?"),
        ("caller", 220, "Yes. I can do that."),
        ("agent", 224, f"You'll hear from us by four o'clock. And {c} — what you said about your daughter? Hold onto that. That's your reason."),
        ("caller", 234, "Thank you. I needed to hear all of this."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_013",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 244,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_013",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "cost-objection", "readiness-objection", "parental-motivation", "iop-appropriate"],
            "coaching_notes": "Exemplary objection handling: acknowledged readiness objection before responding, asked a powerful open question ('what made today the day'), addressed cost concretely without dismissing it, gave an honest answer to the 'what if it doesn't work' question. Clinical screen was lighter (scored 3) — agent focused on motivational work, which was appropriate, but severity and withdrawal risk could have been explored.",
        },
    }


def _syn_014(ctx: dict) -> dict:
    """Objection heavy: BORDERLINE. Caller raises cost and fear. Agent repeats response. Dim 6 = 2."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I'm thinking about getting help for drinking. I have some questions."),
        ("agent", 12, "Sure, go ahead."),
        ("caller", 16, "First — how much does it cost? I'm worried about affording it."),
        ("agent", 22, "That depends on your insurance. Do you have coverage?"),
        ("caller", 28, f"Yes, {carrier}. But I'm not sure what it covers."),
        ("agent", 36, "We'll verify your benefits. Member ID and group number?"),
        ("caller", 42, f"Member ID {mid}, group {grp}."),
        ("agent", 52, "Okay. We'll look into that. Anything else?"),
        ("caller", 58, "I'm also just — I'm scared about what treatment is like. I've heard it's really hard."),
        ("agent", 66, "It's a process. It's not easy. But people get through it."),
        ("caller", 74, "Right, but I have a job. I can't just take time off."),
        ("agent", 80, "We have outpatient options."),
        ("caller", 86, "Okay. I'm still not sure I can afford it though even with insurance."),
        ("agent", 92, "Like I said, we'll verify your benefits and let you know what you'd owe."),
        ("caller", 98, "I know, but what if it's still too much? I'm on a tight budget."),
        ("agent", 106, "We do have some financial assistance available. But let's see what the insurance says first."),
        ("caller", 114, "Okay. I guess that makes sense. I'm just nervous about the whole thing."),
        ("agent", 120, "That's understandable. Most people are nervous."),
        ("caller", 126, "What happens if I do this and it doesn't stick?"),
        ("agent", 132, "We'd work with you on next steps. Treatment outcomes vary."),
        ("caller", 140, "Okay. So what do I do now?"),
        ("agent", 144, "Someone will call you about your benefits and scheduling."),
        ("caller", 150, "When?"),
        ("agent", 154, "Within the next business day or so."),
        ("caller", 160, "Alright. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 2,
        "next_step_clarity": 2,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_014",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 170,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_014",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "cost-objection", "fear-objection", "borderline", "repeated-response"],
            "coaching_notes": "BORDERLINE: objection_handling is borderline 2-3 — caller raised cost concern three times and got the same answer each time ('we'll verify benefits'), with no acknowledgement of the financial anxiety. Fear objection ('it's really hard') received a dismissive one-liner. Next step is borderline 2-3 — timing given as 'next business day or so' which is vague. Empathy was absent throughout. Major coaching opportunity on objection acknowledgement before responding.",
        },
    }


def _syn_015(ctx: dict) -> dict:
    """Objection heavy: mixed. Confidentiality objection handled well. Next step vague (dim 7 = 2)."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I want to ask about getting treatment but I have a concern I need to get past first."),
        ("agent", 14, f"Of course, {c}. What's on your mind?"),
        ("caller", 20, "I work for a large company and my insurance is through them. I'm worried that if I use my insurance for this, my employer will find out. I can't have that."),
        ("agent", 30, f"That's a really common concern and I want to give you an honest answer. Your insurance claim is private — your employer receives aggregate data for cost management but does not receive information about individual diagnoses or treatment types. Under HIPAA, your treatment records are protected. The only way your employer would know is if you told them or if you need to request FMLA leave, which is a separate process you control."),
        ("caller", 56, "Okay. That's more reassuring than I expected. Thank you."),
        ("agent", 62, "Of course. And if you decide FMLA is something you want to explore — which some people do to protect their job during treatment — we can connect you with guidance on that. It's separate from your clinical records."),
        ("caller", 74, "Good to know. So — I've been using cocaine on and off for about two years. Lately more on. I'm spending money I don't have. My partner is frustrated."),
        ("agent", 86, f"I appreciate you sharing that. Two years of use with escalating frequency and financial impact — those are meaningful signals. {c}, are you also drinking or using anything else alongside the cocaine?"),
        ("caller", 100, "Sometimes I drink to come down. Not heavily."),
        ("agent", 108, "Okay. And are there times you've tried to stop on your own?"),
        ("caller", 114, "I've tried. I go a few days and then something stressful happens and I'm back."),
        ("agent", 122, "That cycle — the stress trigger leading back — is something our counsellors work on specifically, especially in IOP. Do you have insurance?"),
        ("caller", 132, f"Yes. {carrier}. ID {mid}, group {grp}."),
        ("agent", 144, "Thank you. And given your confidentiality concern, I want to confirm: when we verify your benefits, that call goes through our intake team, not back to your employer's HR. You're safe."),
        ("caller", 156, "Okay. Good. So what do I do from here?"),
        ("agent", 162, "We'll follow up with you about your options."),
        ("caller", 168, "When?"),
        ("agent", 172, "We'll be in touch soon. Keep an eye on your phone."),
        ("caller", 178, "Alright. Thanks for the information."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 3,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 2,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_015",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 188,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_015",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "confidentiality-objection", "stimulant-use", "vague-close", "iop-appropriate"],
            "coaching_notes": "Confidentiality objection handled with knowledge and warmth — best moment of the call. Clinical screen adequate. Next step is the failure point: 'we'll be in touch soon' and 'keep an eye on your phone' are not acceptable close language. No timing, no ownership, caller had to ask twice. Dim 7 = 2. Strong start, weak finish.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: EXCELLENT — BATCH 2 (syn_016–018)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_016(ctx: dict) -> dict:
    """Excellent: prior residential treatment + relapse. Agent covers full clinical history."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I'm calling because I've relapsed. I did a 30-day residential about two years ago and I was clean for fourteen months. I started drinking again four months ago and it's gotten bad fast."),
        ("agent", 18, f"{c}, thank you for being so upfront about your history. Fourteen months of sobriety after residential — that's real work. And the fact that you're calling now, rather than waiting for things to get worse, tells me you haven't forgotten what it felt like to be on the other side of this. What's been going on in the last four months?"),
        ("caller", 38, "Stressful job change. And a breakup. I know those are excuses, but that's when it started."),
        ("agent", 48, "They're not excuses — they're context, and our clinical team needs that context to design the right plan for you. You've done residential before, so you know the drill. Can I ask: how much are you drinking now versus before you got into treatment the first time?"),
        ("caller", 64, "About the same. Daily, a bottle of wine to a bottle and a half."),
        ("agent", 74, "And are you having any withdrawal symptoms when you try to go a day without?"),
        ("caller", 80, "Some. Anxiety, trouble sleeping. Nothing as bad as last time, but it's there."),
        ("agent", 90, f"Good to know. That history matters — your body remembers. I want to flag that for our clinical team. {c}, given that you've been through residential, what's your thinking on level of care this time? Some people want to try IOP first, others know they need the structure of residential again."),
        ("caller", 108, "Honestly I think I need residential. I don't trust myself in an outpatient setting right now."),
        ("agent", 116, "That kind of self-awareness is valuable and I'll make sure it goes into your intake notes. Our clinical team will assess that formally, but your own read matters. Let me get your insurance information so we can check what your plan covers for a residential admission."),
        ("caller", 128, f"Sure. It's {carrier}, member ID {mid}, group {grp}."),
        ("agent", 140, f"Got it. And from your first treatment — do you remember if there were any complications with coverage, or did it go smoothly?"),
        ("caller", 150, "It went fine. Same carrier, different plan."),
        ("agent", 156, "Good. That continuity actually helps. I'm noting your prior treatment facility, your length of sobriety, and the relapse timeline. Our intake team will have all of this before they call you. Here's what happens next: benefits verification will be back to you within ninety minutes, and our admissions coordinator will call immediately after with availability for an assessment. Can you take a call this afternoon?"),
        ("caller", 178, "Yes. I'm free after noon."),
        ("agent", 184, f"Perfect — you'll hear from us between one and two o'clock. {c}, relapse is not failure. It's information. You know how to do this."),
        ("caller", 194, "Thank you. I needed to hear that."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 4,
        "clinical_screening": 5,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_016",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 204,
            "caller_type": "patient",
            "campaign_source": "referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_016",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "relapse", "prior-residential", "self-aware", "residential-indicated"],
            "coaching_notes": "Strong handling of relapse caller — empathy was warm but appropriately matter-of-fact (not over-pitying), clinical history covered thoroughly including prior treatment complications. Agent explicitly asked caller's own level-of-care preference, which is excellent practice. Minor: empathy opening was good but could have slowed down slightly before moving to clinical questions.",
        },
    }


def _syn_017(ctx: dict) -> dict:
    """Excellent: caller minimising use; agent draws out severity without confrontation."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How can I help?"),
        ("caller", 4, f"Hi, I'm {c}. I'm just... calling to find out what you guys do. I don't know if I really need treatment or whatever. My sister kind of pushed me to call."),
        ("agent", 16, f"I'm glad your sister encouraged you to reach out, and I'm glad you followed through. There's no pressure here — I'm just going to ask a few questions and we can figure out together whether what you're dealing with is something we can help with. What's been going on?"),
        ("caller", 32, "I drink, but it's not like I'm an alcoholic or anything. I just drink after work to unwind. Everyone does that."),
        ("agent", 44, f"I hear you. Can I ask — how many drinks is 'unwinding' for you on a typical evening?"),
        ("caller", 52, "I don't know. Three or four, maybe."),
        ("agent", 58, "And are there nights when it's more than that?"),
        ("caller", 64, "Sometimes. If it was a really bad day, maybe six or seven."),
        ("agent", 72, "And how often are the really bad days?"),
        ("caller", 78, "More than they used to be. Maybe three or four times a week now."),
        ("agent", 86, f"Okay. So on those nights — after six or seven drinks — how do you feel the next morning?"),
        ("caller", 94, "Rough. I've been calling in late to work a few times."),
        ("agent", 100, f"Has that happened more in the last few months than it used to?"),
        ("caller", 106, "Yeah. My sister noticed that too. She said I've changed."),
        ("agent", 114, f"I appreciate you sharing that. {c}, I want to reflect something back to you — not to label it, just so you can hear it. What you're describing — four to seven drinks most evenings, increasingly difficult mornings, calling in late, your sister noticing a change — those are patterns that tend to escalate without support. You don't have to call it anything. But the question isn't whether it's 'bad enough.' The question is whether it's getting in the way of the life you want."),
        ("caller", 144, "When you put it like that... yeah, it is."),
        ("agent", 150, "Then you called the right place. Let me ask a few more questions. Do you have insurance?"),
        ("caller", 156, f"Yes. {carrier}. Member ID is {mid}, group {grp}."),
        ("agent", 168, "Thank you. And have you ever tried to cut back on your own?"),
        ("caller", 174, "A few times. I go a week and then something comes up."),
        ("agent", 182, "That pattern — trying and returning — is really common and it's one of the things treatment specifically addresses. Here's what I'd like to do: I'll have our benefits team verify your coverage and an admissions coordinator call you back within two hours. They'll talk through your options — which based on what you've described would likely start with our outpatient track. Would that work for you?"),
        ("caller", 204, "Yeah. Okay. That sounds okay."),
        ("agent", 210, f"Good. You'll hear from us by noon. And {c} — calling was the right thing to do."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 4,
        "clinical_screening": 5,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_017",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 220,
            "caller_type": "patient",
            "campaign_source": "family_referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_017",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "minimising-use", "ambivalent", "family-referred", "motivational-interviewing"],
            "coaching_notes": "Exemplary motivational approach — agent used Socratic questioning to let the caller arrive at their own concern rather than confronting the minimisation directly. The reflection ('the question is whether it's getting in the way of the life you want') is textbook MI and avoids labelling. Clinical screen strong: drew out frequency, morning consequences, and prior quit attempts. Objection handling 5: handled 'I don't really need this' without pushback.",
        },
    }


def _syn_018(ctx: dict) -> dict:
    """Excellent: highly distressed caller; agent sustains exceptional empathy throughout."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"I... sorry. I'm {c}. I don't even know why I called. I've been sitting here for an hour trying to call and I keep hanging up."),
        ("agent", 16, f"And you called. That's what matters. {c}, I'm here and I have time. There's nothing else I need to be doing right now. What's going on?"),
        ("caller", 30, "I've been using heroin for three years. My family doesn't know. I've been hiding it. I'm scared I'm going to die."),
        ("agent", 44, f"Thank you for trusting me with that. I can hear how much fear is in what you just said — and that fear makes complete sense. Three years is a long time to carry this alone. You're not alone right now. Can you tell me — are you safe at this moment? Are you using right now?"),
        ("caller", 62, "No. I used this morning but not right now. I'm at home."),
        ("agent", 70, f"Okay. Good. {c}, I want you to know that what you just told me — that you're scared you're going to die — that tells me you want to live. That's something we can work with. How are you feeling physically right now?"),
        ("caller", 86, "Anxious. A little sweaty. I've been using every day so I'm starting to feel it."),
        ("agent", 96, "When you say feeling it — are you getting early withdrawal symptoms? Muscle aches, nausea, restlessness?"),
        ("caller", 106, "Yeah. All of that. It comes on fast with heroin."),
        ("agent", 114, f"It does. And that's important information — opioid withdrawal can escalate and it's much safer managed medically. I want to get you in today if we can. Is that something you want?"),
        ("caller", 128, "Yes. But I'm scared. What if my family finds out?"),
        ("agent", 136, f"Your treatment is confidential. We don't contact family without your permission — ever. Whatever you decide about telling them is your choice, on your timeline. Right now, the only thing that matters is getting you safe. Do you have insurance?"),
        ("caller", 150, f"Yes. {carrier}. I have my card. Member ID {mid}, group {grp}."),
        ("agent", 164, f"Thank you. I'm noting that now. {c}, here's what I want to do: I'm going to put a priority flag on your intake and connect you with our detox admissions team right now — not in two hours, right now. They'll tell you exactly what the admissions process looks like today. Are you able to stay on the line for a moment while I get them?"),
        ("caller", 184, "Yes. Please."),
        ("agent", 188, f"I'm right here. You made the hardest call already."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 5,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_018",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "excellent",
        "metadata": {
            "duration_seconds": 198,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_018",
            "scenario_type": "excellent",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": True,
            "scenario_tags": ["patient-caller", "high-distress", "opioid-use-disorder", "early-withdrawal", "hidden-use", "same-day-admit"],
            "coaching_notes": "Outstanding. Empathy was patient and unhurried despite the caller's distress — agent gave space without rushing to information. Correctly identified urgency (daily use + early withdrawal symptoms = medical risk) and escalated to real-time admissions handoff rather than a callback. Confidentiality objection handled in one sentence without derailing the momentum. Benchmark-quality call.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: WEAK — BATCH 2 (syn_019–021)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_019(ctx: dict) -> dict:
    """Weak: CLINICAL_SCOPE violation. Agent tells caller what level of care they need."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, {a} speaking."),
        ("caller", 4, f"Hi, I'm {c}. I'm looking at treatment options for alcohol. I've been drinking pretty heavily."),
        ("agent", 10, "How long?"),
        ("caller", 14, "About two years. It's every day."),
        ("agent", 18, "How much a day?"),
        ("caller", 22, "Half a bottle of vodka, sometimes more."),
        ("agent", 28, "Any withdrawal when you try to stop?"),
        ("caller", 32, "Some shaking. Nothing too bad."),
        ("agent", 36, "Have you looked into what kind of program you want?"),
        ("caller", 42, "I was thinking outpatient. I have a job and I can't just disappear."),
        ("agent", 48, "Based on what you're describing — daily drinking, half a bottle of vodka, withdrawal symptoms — I think you need residential, not outpatient. Outpatient isn't going to be enough for where you are."),
        ("caller", 62, "Oh. I didn't think it was that bad."),
        ("agent", 68, "It is. You should really consider the 30-day program. That's the right fit for your situation."),
        ("caller", 76, "I'd have to figure out my job. That's a big deal."),
        ("agent", 82, "FMLA can cover that. Do you have insurance?"),
        ("caller", 88, f"Yes. {carrier}. ID {mid}, group {grp}."),
        ("agent", 100, "Okay. We'll verify. Someone will be in touch."),
        ("caller", 106, "Do you know when?"),
        ("agent", 110, "Probably today."),
        ("caller", 114, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 3,
        "urgency_triage": 2,
        "family_caller_handling": None,
        "objection_handling": 2,
        "next_step_clarity": 2,
        "compliance_language": 0,
    }

    return {
        "call_id": "syn_019",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 124,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_019",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": True,
            "expected_flags": ["CLINICAL_SCOPE"],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "compliance-violation", "clinical-scope", "level-of-care-overreach"],
            "coaching_notes": "COMPLIANCE VIOLATION: 'I think you need residential, not outpatient' and 'Outpatient isn't going to be enough for where you are' are scope-of-practice violations — level-of-care determination requires clinical assessment, not intake staff judgment. Also: 'That's the right fit for your situation' is a clinical prescription. Agent should say 'our clinical team will assess the right level of care.' Beyond compliance: no empathy, objection to job impact dismissed with FMLA mention only, next step vague.",
        },
    }


def _syn_020(ctx: dict) -> dict:
    """Weak: DIAG_CLAIM v2 + generally poor. Agent diagnoses and dismisses. Dim 8 = 0."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid = ctx["carrier"], ctx["member_id"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}."),
        ("caller", 4, f"Yeah, hi. I'm {c}. I think I might have a problem with pills. Painkillers."),
        ("agent", 10, "How long?"),
        ("caller", 14, "Maybe a year. Started after a surgery."),
        ("agent", 18, "What you're describing sounds like addiction. You're going to need treatment."),
        ("caller", 26, "I mean... I don't know if it's that serious."),
        ("agent", 30, "It is. Daily use of opioids after a year is addiction. Are you still getting them from a prescription or buying them?"),
        ("caller", 40, "A mix. My prescription ran out so I've been getting them other ways."),
        ("agent", 48, "That's a classic pattern. You have a serious dependency. Do you have insurance?"),
        ("caller", 56, f"Yes, {carrier}. ID is {mid}."),
        ("agent", 62, "Group number?"),
        ("caller", 66, "I don't have it with me."),
        ("agent", 70, "We'll try without it. Someone will call you."),
        ("caller", 76, "When?"),
        ("agent", 80, "Soon."),
        ("caller", 84, "Okay. Is there anything I should know before then?"),
        ("agent", 88, "Just be ready to discuss your history. Bye."),
    ])

    scores = {
        "empathy_rapport": 1,
        "insurance_verification": 2,
        "clinical_screening": 2,
        "urgency_triage": 1,
        "family_caller_handling": None,
        "objection_handling": 1,
        "next_step_clarity": 1,
        "compliance_language": 0,
    }

    return {
        "call_id": "syn_020",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 98,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_020",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": True,
            "expected_flags": ["DIAG_CLAIM"],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "compliance-violation", "diagnostic-claim", "dismissive-tone", "worst-case"],
            "coaching_notes": "COMPLIANCE VIOLATION: 'What you're describing sounds like addiction' and 'You have a serious dependency' are diagnostic claims — intake staff cannot diagnose. Multiple violations in short span. Beyond compliance: zero empathy, dismissive throughout, insurance screen incomplete (group number abandoned), clinical screen stopped after confirmation of use pattern, next step ('soon', 'bye') is the worst in the dataset. This call is a comprehensive failure across all dimensions.",
        },
    }


def _syn_021(ctx: dict) -> dict:
    """Weak: borderline — multiple gaps, no violation. Insurance and clinical screen both 2-3. BORDERLINE #4."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, I'm {a}."),
        ("caller", 6, f"Hi. My name is {c}. My doctor told me I should look into treatment for my drinking. I've been cutting back but it's hard."),
        ("agent", 16, "How long have you been drinking heavily?"),
        ("caller", 22, "A few years. It got worse after COVID."),
        ("agent", 28, "Are you drinking every day?"),
        ("caller", 32, "Most days. Not always a lot, but something."),
        ("agent", 38, "Do you have insurance?"),
        ("caller", 42, f"Yes, {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 54, "Great. Do you have any idea what kind of program you're looking for?"),
        ("caller", 60, "Something that works around my schedule. I have two kids."),
        ("agent", 66, "We have outpatient options that are evenings only."),
        ("caller", 72, "That would work. How long does it usually last?"),
        ("agent", 78, "Depends on your assessment. Typically eight to twelve weeks for IOP."),
        ("caller", 86, "Okay. My doctor mentioned something about medication. Is that something you do?"),
        ("agent", 92, "Yes, we offer MAT. The clinical team would assess that."),
        ("caller", 100, "Good to know. What happens next?"),
        ("agent", 104, "Someone will call you to set up an intake appointment."),
        ("caller", 110, "Do you have a rough timeframe?"),
        ("agent", 114, "Within the next day or two."),
        ("caller", 120, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 3,
        "urgency_triage": 2,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 2,
        "compliance_language": 4,
    }

    return {
        "call_id": "syn_021",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "weak",
        "metadata": {
            "duration_seconds": 130,
            "caller_type": "patient",
            "campaign_source": "physician_referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_021",
            "scenario_type": "weak",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "borderline", "physician-referred", "parent-concern", "adequate-but-flat"],
            "coaching_notes": "BORDERLINE: clinical_screening is borderline 2-3 — agent captured frequency and history, but missed severity (withdrawal, consequences, prior attempts) and the MAT question came from the caller, not the agent. Insurance borderline 2-3 — fields captured but no framing as 'step toward help.' No empathy opening; call was transactional throughout. Next step timing of 'a day or two' is borderline acceptable vs. not.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: FAMILY_CALLER — BATCH 2 (syn_022–024)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_022(ctx: dict) -> dict:
    """Family caller: employer calling on behalf of employee. Unusual consent, handled correctly."""
    a = ctx["agent_first"]
    caller_first, caller_last = ctx["caller_first"], ctx["caller_last"]
    patient_first = "Devon"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hello, my name is {caller_first} {caller_last}. I'm an HR manager at a company and I'm calling about one of our employees — with their knowledge and support. His name is {patient_first}. He spoke to me this morning and asked me to help him find treatment. He's struggling with alcohol."),
        ("agent", 18, f"Thank you for calling, {caller_first}, and thank you for supporting {patient_first} in this way. Before we go further, I want to make sure I understand the consent situation correctly. Has {patient_first} given you explicit permission to speak on his behalf and to share his information with us today?"),
        ("caller", 36, "Yes. He was with me this morning. He's actually in the next office right now. He's willing to talk to you directly if needed."),
        ("agent", 44, f"That's actually very helpful. Given that {patient_first} is available, it would be best if we could have him join the call for a few minutes — even briefly — so he can give verbal consent and I can ask him a couple of quick questions. Would that be possible?"),
        ("caller", 58, "Yes, absolutely. One moment."),
        ("agent", 62, "Of course, take your time."),
        ("caller", 72, f"Hi, this is {patient_first}."),
        ("agent", 76, f"Hi {patient_first}, thank you for coming on the line. I just want to confirm — you're aware that your HR colleague {caller_first} reached out to us on your behalf today, and you're okay with us having this conversation and sharing information about your situation?"),
        ("caller", 92, "Yes, I am. I asked them to help me."),
        ("agent", 98, f"Thank you, {patient_first}. I appreciate you saying that. I have a few questions for you directly. How long have you been struggling with alcohol?"),
        ("caller", 108, "A couple of years. It's gotten bad in the last six months."),
        ("agent", 116, "Are you experiencing any withdrawal symptoms when you go a day without drinking?"),
        ("caller", 122, "Some anxiety and trouble sleeping. Nothing severe."),
        ("agent", 128, f"Okay. {patient_first}, do you have health insurance through your employer here?"),
        ("caller", 134, f"Yes. It's {carrier}. My HR should have all the details."),
        ("agent", 140, f"{caller_first}, do you have {patient_first}'s insurance information available?"),
        ("caller", 148, f"Yes. Member ID {mid}, group {grp}."),
        ("agent", 158, f"Perfect. {patient_first}, here's what happens next: our benefits team will verify your coverage and an admissions coordinator will call you — on your direct line, not through HR unless you prefer otherwise — within two hours. Which number would you like them to use?"),
        ("caller", 174, "My cell. I'll give it to you."),
        ("agent", 180, f"Please go ahead. And {patient_first} — you have good people around you. That matters."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": 5,
        "objection_handling": None,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_022",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 190,
            "caller_type": "employer_representative",
            "campaign_source": "eap_referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_022",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["employer-caller", "patient-adjacent", "eap-pathway", "consent-confirmed-live", "unusual-consent-edge-case"],
            "coaching_notes": "Excellent handling of an unusual consent scenario — agent immediately asked for explicit patient consent, then asked if the patient could come on the line directly (best practice), and correctly directed the callback to the patient's personal number rather than HR. Family_caller_handling scored 5 for navigating the employer/patient/consent triangle correctly. Clinical screen limited because the handoff from HR to patient was brief.",
        },
    }


def _syn_023(ctx: dict) -> dict:
    """Family caller: BORDERLINE. Adult child for parent. Consent adequate, family distress ignored. BORDERLINE #5."""
    a = ctx["agent_first"]
    caller_first = ctx["caller_first"]
    patient_first = "Robert"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"{TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi. My name is {caller_first}. I'm calling about my dad. His name is {patient_first}. He's 64 and he's been drinking heavily since my mom passed away last year."),
        ("agent", 16, "I'm sorry to hear that. Does your father know you're calling?"),
        ("caller", 22, "Yes. I talked to him this morning. He said he'd think about it but he said I could call to find out what's involved."),
        ("agent", 30, "Okay. I want to be upfront — since your father is an adult, any treatment would require his direct consent. But I'm happy to give you information you can share with him. How much is he drinking?"),
        ("caller", 44, "A lot. A bottle of wine at dinner, then usually whiskey after. Every night."),
        ("agent", 52, "Has he had any falls or health issues related to it?"),
        ("caller", 58, "He fell twice last month. The second time he needed stitches."),
        ("agent", 66, "That's concerning from a medical standpoint. Has he ever tried to stop or cut down?"),
        ("caller", 72, "He tried after the first fall but it only lasted a few days."),
        ("agent", 78, "Does he have insurance?"),
        ("caller", 84, f"Yes, through his retirement plan. It's {carrier}. I have his ID — it's {mid}, group {grp}."),
        ("agent", 96, "Thank you. Given his age and the fall history, medical assessment is particularly important for him. Has he agreed to at least speak to someone here?"),
        ("caller", 108, "Not yet. I'm hoping to convince him this week."),
        ("agent", 116, "When he's ready, he can call directly or you can bring him in. We'd be glad to do a brief phone consultation with him if that feels more approachable."),
        ("caller", 126, "That might work. I'll try that approach."),
        ("agent", 130, "Good. Is there anything else you'd like to know?"),
        ("caller", 136, "Not right now. I'm just worried about him. It's been a really hard year for our whole family."),
        ("agent", 144, "That's understandable. Have him give us a call when he's ready."),
        ("caller", 150, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 3,
        "insurance_verification": 3,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": 3,
        "objection_handling": None,
        "next_step_clarity": 3,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_023",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 160,
            "caller_type": "family_member",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_023",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["family-caller", "adult-child", "elderly-patient", "fall-history", "borderline"],
            "coaching_notes": "BORDERLINE: family_caller_handling is borderline 2-3 — consent was acknowledged but framing was procedural rather than warm; when caller said 'it's been a really hard year for our whole family' the agent gave a two-word non-response ('that's understandable') and moved on. The offer of a phone consultation with the patient was good practice. All dimensions are borderline 3 — reasonable graders may score 2 or 3 across the board. Clinical flag: fall history mentioned, agent noted it but didn't flag as urgent.",
        },
    }


def _syn_024(ctx: dict) -> dict:
    """Family caller: friend calling, not family. Agent navigates trickier consent correctly."""
    a = ctx["agent_first"]
    caller_first = ctx["caller_first"]
    patient_first = "Simone"
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How can I help?"),
        ("caller", 4, f"Hi, I'm {caller_first}. I'm calling about my friend. Her name is {patient_first}. She asked me to call for her because she was too nervous to do it herself."),
        ("agent", 14, f"I'm glad she has someone like you to help her take this step. Before I go further — just so you both understand — I can share general information with you, but because {patient_first} isn't a family member, I'd want to involve her directly before we discuss her specific situation in any detail. Is she with you right now or available to speak?"),
        ("caller", 34, "She's right here. She can hear you — I have you on speaker."),
        ("agent", 40, f"{patient_first}, can you hear me okay? I just want to make sure you're comfortable with your friend being part of this call."),
        ("caller", 50, f"Yes. I'm here. I asked {caller_first} to help me. I'm just really scared."),
        ("agent", 58, f"That's completely okay, {patient_first}. You don't have to do any of the talking if you don't want to. I'm glad you're on the line. Can you tell me, in your own words, what's been going on?"),
        ("caller", 72, f"I've been using cocaine for about eighteen months. It's gotten out of control. I spend money I don't have. I've been lying to my family."),
        ("agent", 88, f"Thank you for telling me that. Eighteen months and the pattern you're describing — the financial consequences, the hiding — those are signs that this has moved beyond something you can manage on your own, and reaching out today is exactly the right move. {patient_first}, are you also drinking or using anything else alongside the cocaine?"),
        ("caller", 108, "Sometimes I drink. To come down."),
        ("agent", 116, "Okay. And have you tried to stop on your own?"),
        ("caller", 122, "A few times. I can't get past a week."),
        ("agent", 128, f"That's a really common pattern with stimulant use and it doesn't mean you lack willpower — it means your brain has adapted and needs support to reset. Do you have health insurance, {patient_first}?"),
        ("caller", 142, f"Yes. {carrier}. I have my card. Member ID {mid}, group {grp}."),
        ("agent", 154, f"Thank you. Here's the plan: I'll verify your benefits and have our admissions team call you — {patient_first}, on your number directly, unless you'd prefer {caller_first} to be included in that call too."),
        ("caller", 170, "I'd like her on the call."),
        ("agent", 174, f"Then I'll note that. You'll hear from us within ninety minutes. {patient_first} — having a friend willing to make this call with you is not a small thing. Hold onto that."),
        ("caller", 186, "Thank you."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 3,
        "family_caller_handling": 5,
        "objection_handling": None,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_024",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "family_caller",
        "metadata": {
            "duration_seconds": 196,
            "caller_type": "friend",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_024",
            "scenario_type": "family_caller",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["friend-caller", "patient-on-call", "stimulant-use", "consent-navigated-correctly"],
            "coaching_notes": "Strong handling of the friend-caller edge case — agent immediately established consent by addressing the patient directly, confirmed she was comfortable with the arrangement, and then pivoted naturally to the patient for the clinical questions. Next step correctly offered patient the choice of including friend in follow-up call. Family_caller_handling scored 5 because the non-family consent situation was navigated without making it feel legalistic.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: URGENCY — BATCH 2 (syn_025–027)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_025(ctx: dict) -> dict:
    """Urgency: recent overdose last night. Agent activates crisis protocol immediately."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi. My name is {c}. I overdosed last night. My roommate found me and used naloxone. I'm alive and I need help."),
        ("agent", 14, f"{c}, I am so glad you called and I am so glad your roommate was there. That was a life-saving moment and you survived it. How are you feeling physically right now?"),
        ("caller", 26, "Weak. Sick. I have a headache. But I'm okay enough to talk."),
        ("agent", 34, f"Good. You're okay. First — have you been seen by a doctor since last night? Did you go to the ER?"),
        ("caller", 44, "No. My roommate wanted me to but I refused. I was scared."),
        ("agent", 52, f"I understand. I'm going to be honest with you: after an opioid overdose, medical evaluation is important — not just for the overdose itself, but because your body has been through significant stress. I want to get you both medically evaluated and into our detox program today. Not tomorrow — today. Can I ask: are you using heroin, fentanyl, or prescription opioids?"),
        ("caller", 74, "Fentanyl. I've been using for about eight months."),
        ("agent", 82, f"Eight months of fentanyl use and an overdose last night — this is a genuine medical emergency, {c}, and you're doing exactly the right thing by calling. Here is what I want to do: I'd like to arrange for you to be seen at our medical facility this morning. Our intake team can coordinate transport from where you are. Where are you located?"),
        ("caller", 96, "I'm at my apartment. Downtown."),
        ("agent", 102, "Okay. Do you have insurance with you?"),
        ("caller", 108, f"Yes. {carrier}. My card is here. Member ID {mid}, group {grp}."),
        ("agent", 120, f"I have that. {c}, I'm escalating you to our medical intake coordinator right now — they handle same-day admissions for exactly this kind of situation. I need you to stay on the line. Does your roommate know you're calling us?"),
        ("caller", 136, "Yes. They're here."),
        ("agent", 140, "Good. Tell them to stay with you until our coordinator calls back — which will be in under ten minutes. Do not drive. Do not be alone. Can you do that?"),
        ("caller", 152, "Yes."),
        ("agent", 156, f"Good. You called at exactly the right moment, {c}. I'm getting help to you right now."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 5,
        "urgency_triage": 5,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 5,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_025",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 166,
            "caller_type": "patient",
            "campaign_source": "direct",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_025",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": True,
            "scenario_tags": ["patient-caller", "post-overdose", "fentanyl", "crisis-protocol-activated", "same-day-admit", "naloxone-reversal"],
            "coaching_notes": "Benchmark post-overdose call. Agent correctly identified this as a medical emergency, asked about ER evaluation, named the specific substance (fentanyl), and escalated to same-day medical intake rather than a standard callback. Instructions to stay with roommate and not drive are correct safety protocol. One of the strongest urgency triage demonstrations in the dataset.",
        },
    }


def _syn_026(ctx: dict) -> dict:
    """Urgency: passive SI signal. Agent partially responds but doesn't fully activate crisis protocol. BORDERLINE #6."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I'm calling because I've been drinking every day for a long time and I think I need to stop. I've been having some dark thoughts lately and I just... I need something to change."),
        ("agent", 18, f"I hear you, {c}. Can you tell me more about the dark thoughts you mentioned? I want to make sure I understand what you mean."),
        ("caller", 30, "I've been thinking that everyone would be better off without me. But I don't have a plan or anything. It's more like a background feeling."),
        ("agent", 44, f"Thank you for being honest about that. I want to acknowledge that what you just described is something we take seriously. Those kinds of thoughts — even as a background feeling — are a sign that you need support beyond just the drinking. Have you told anyone else about these thoughts?"),
        ("caller", 58, "No. You're the first."),
        ("agent", 64, f"I'm glad you told me. {c}, I'm going to note this for our clinical team — it's important context and they will want to address it as part of your care. Now let me ask about the drinking so we have the full picture. How long and how much?"),
        ("caller", 78, "About four years. A six-pack or more every night."),
        ("agent", 86, "Any withdrawal symptoms when you go without?"),
        ("caller", 92, "Yes. Shaking, trouble sleeping."),
        ("agent", 98, "Okay. And insurance?"),
        ("caller", 102, f"Yes. {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 114, "Thank you. I'm going to set this up as a priority intake given everything you've shared. Someone will call you within a few hours."),
        ("caller", 124, "Okay."),
        ("agent", 128, "In the meantime — if those dark thoughts get stronger or more specific, please call 988, which is the mental health crisis line. They're available 24/7."),
        ("caller", 138, "Okay. I will."),
        ("agent", 142, "Good. We'll be in touch soon."),
    ])

    scores = {
        "empathy_rapport": 3,
        "insurance_verification": 3,
        "clinical_screening": 3,
        "urgency_triage": 2,
        "family_caller_handling": None,
        "objection_handling": None,
        "next_step_clarity": 3,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_026",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 152,
            "caller_type": "patient",
            "campaign_source": "google_paid",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_026",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": True,
            "scenario_tags": ["patient-caller", "passive-si", "partial-crisis-response", "borderline", "dual-concern"],
            "coaching_notes": "BORDERLINE: urgency_triage is borderline 1-2 — agent asked a follow-up question about the SI ('can you tell me more') which is good, and gave 988 as a resource at the end, but did not activate the full crisis protocol (no warm transfer attempt, no direct offer to stay on the line, moved back to routine intake after noting it). The 'few hours' callback timeline is inappropriate given the active SI disclosure — this should have been escalated to immediate contact. Reasonable graders may score 1, 2, or 3 on urgency_triage.",
        },
    }


def _syn_027(ctx: dict) -> dict:
    """Urgency: non-urgent caller; agent manufactures urgency inappropriately. Dim 4 = 1."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I'm calling to find out about your programs. I've been thinking about cutting back on drinking for a while and maybe getting some support. I'm not in crisis or anything, just looking at my options."),
        ("agent", 16, "That's good that you're thinking about it. You know, alcohol use tends to get worse over time if you don't address it. Are you drinking every day?"),
        ("caller", 26, "Most days. A glass or two of wine at dinner."),
        ("agent", 32, "That's more than it sounds like. Nightly drinking is a pattern that typically escalates. A lot of people who think they have it under control end up in serious trouble."),
        ("caller", 44, "I mean, I know I should cut back. That's why I'm calling. But I don't feel like I have a major problem."),
        ("agent", 52, "The thing is, people rarely recognise how serious it is until it's gotten really bad. The fact that you're calling is a sign it's already more serious than you think."),
        ("caller", 62, "I'm not sure I agree with that. I just want some information."),
        ("agent", 68, "I understand. But I'd hate for you to wait until something happens — a DUI, a health scare — before you take action. A lot of our patients say they wish they'd come in sooner."),
        ("caller", 80, "Okay, I hear you. What do you have for people who are still working and don't want to do inpatient?"),
        ("agent", 88, "We have IOP — evenings, three times a week. Very manageable."),
        ("caller", 96, "That could work. What does it cost?"),
        ("agent", 100, "Depends on your insurance. Do you have coverage?"),
        ("caller", 106, f"Yes. {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 118, "Okay. I'd really encourage you to move on this — the sooner the better with alcohol."),
        ("caller", 126, "Can someone call me with more details?"),
        ("agent", 130, "Absolutely. You'll hear from us soon."),
        ("caller", 136, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 2,
        "insurance_verification": 3,
        "clinical_screening": 2,
        "urgency_triage": 1,
        "family_caller_handling": None,
        "objection_handling": 2,
        "next_step_clarity": 2,
        "compliance_language": 4,
    }

    return {
        "call_id": "syn_027",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "urgency",
        "metadata": {
            "duration_seconds": 146,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_027",
            "scenario_type": "urgency",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "manufactured-urgency", "low-risk-caller", "pressure-tactics"],
            "coaching_notes": "Urgency triage = 1 (poor): caller explicitly stated they are not in crisis and are calling for information. Agent repeatedly implied the situation was more serious than it is ('rarely recognise how serious it is', 'wish they'd come in sooner', 'a DUI, a health scare') — this is manufactured urgency. No signals of acute crisis were present. Agent should have accepted the caller's self-assessment and provided information without pressure. Empathy was absent — agent treated this as a closing opportunity, not a support call.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# SCENARIO: OBJECTION_HEAVY — BATCH 2 (syn_028–030)
# ══════════════════════════════════════════════════════════════════════════════

def _syn_028(ctx: dict) -> dict:
    """Objection heavy: prior treatment failure objection. Agent handles ambivalence with MI technique."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I've been sober for six months and I've started drinking again. I went to rehab two years ago and it obviously didn't work."),
        ("agent", 16, f"Thank you for telling me that, {c}. Six months of sobriety is real — that's not nothing. Relapse doesn't erase that. Can I ask: when you say rehab 'didn't work,' what does that mean to you? What were you hoping would happen that didn't?"),
        ("caller", 30, "I thought I'd be fixed. I went in, did the 30 days, came out, and eventually ended up back where I started."),
        ("agent", 44, f"That's a really honest answer. The thing I want to offer you — not as reassurance, but as a different frame — is that 30-day residential works for some people and doesn't for others, and that's about fit, not failure. There's research showing that people who relapse after treatment and re-enter treatment have better long-term outcomes than those who never return. You coming back is actually part of the process, not outside of it."),
        ("caller", 68, "I didn't know that."),
        ("agent", 74, f"Most people don't. So the question isn't whether treatment can work for you — it's whether this time we design it differently. What did the last program not give you that you think you needed?"),
        ("caller", 88, "Aftercare. I left and there was nothing. No follow-up, no support group, nothing."),
        ("agent", 96, f"That's one of the most common reasons people relapse — and it's something we specifically address. Our aftercare planning starts on day one, not day thirty. I want to make a note of that for our clinical team right now. {c}, do you have insurance?"),
        ("caller", 110, f"Yes. {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 122, "Thank you. I'm going to verify your benefits and flag the aftercare concern for your intake coordinator. They'll walk you through how our continuing care program works. Can they reach you this afternoon?"),
        ("caller", 136, "Yes. After two."),
        ("agent", 140, f"You'll hear from us before three. {c} — coming back after a relapse is one of the hardest things to do. The fact that you made this call tells me something important about you."),
        ("caller", 152, "Thank you. I hope it's different this time."),
        ("agent", 156, "We'll make sure the plan is."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 4,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_028",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 166,
            "caller_type": "patient",
            "campaign_source": "referral",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_028",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "relapse", "prior-treatment-failure-objection", "aftercare-concern", "mi-technique"],
            "coaching_notes": "Strong objection handling — agent reframed relapse as part of process with genuine evidence, then asked a powerful open question about what was missing (not 'what went wrong'). Correctly identified aftercare as the gap and promised to flag it for intake. The research framing was accurate and non-patronising. Clinical screen was lighter than ideal — only the relapse/drinking history was covered.",
        },
    }


def _syn_029(ctx: dict) -> dict:
    """Objection heavy: stigma and 'what will people think' — handled with warmth and accuracy."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}. How can I help you today?"),
        ("caller", 6, f"Hi, I'm {c}. I've been struggling with benzodiazepines — Xanax, mostly — for about two years. I want to get help but I'm scared about what people will think. I'm a teacher."),
        ("agent", 20, f"Thank you for calling, {c}. That took courage. The fear about what people will think — especially in a profession like teaching where your reputation matters — is something a lot of people face. I want to walk you through the privacy picture, because it's actually more protective than most people realise."),
        ("caller", 38, "Please. That would help."),
        ("agent", 42, f"Your treatment is completely confidential under HIPAA — your employer, your school district, anyone you haven't specifically authorised cannot access your records. Your insurance company processes the claim but does not share diagnosis information with your employer. If you need time off for treatment, FMLA protects your job and HR is only told that you're on approved medical leave — not why. Does that help?"),
        ("caller", 66, "Yes. A lot. I didn't know about FMLA."),
        ("agent", 72, f"Most people don't. And for teachers specifically — there are programs designed around schedules, including summer intensive options and evening outpatient. Benzo dependence is also something our medical team has a lot of experience with because it does require a supervised taper. Have you been taking them as prescribed, or are you taking more than prescribed?"),
        ("caller", 94, "Both at this point. Started prescribed, now I'm taking more than I should."),
        ("agent", 104, f"I understand. That's a really common progression. The supervised taper is important because stopping benzodiazepines abruptly can be medically dangerous — I want to flag that for our clinical team. {c}, do you have health insurance?"),
        ("caller", 118, f"Yes, through the school district. It's {carrier}. Member ID {mid}, group {grp}."),
        ("agent", 132, f"Thank you. District plans often have good mental health and substance use coverage. I'll have our benefits team verify. They'll be discreet — any calls will show up as {TREATMENT_CENTER} on caller ID, not as a specific clinic type, if that matters to you."),
        ("caller", 148, "It does. Thank you for thinking of that."),
        ("agent", 154, f"Of course. Here's what happens next: benefits verification within ninety minutes, followed by a call from our intake team who will talk through level of care and scheduling with your work calendar in mind. They'll call from our main line — just {TREATMENT_CENTER}. Does two o'clock work for you?"),
        ("caller", 172, "Yes. That works."),
        ("agent", 176, f"Perfect. {c} — teachers reach out for help less often than they should because of exactly the fear you named. I'm glad you called."),
    ])

    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 5,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_029",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 186,
            "caller_type": "patient",
            "campaign_source": "organic_search",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_029",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "stigma-objection", "teacher", "benzo-dependence", "hipaa-fmla-knowledge", "caller-id-consideration"],
            "coaching_notes": "Excellent stigma objection handling — agent proactively offered the FMLA/HIPAA detail without being asked, and thought to mention the caller ID display (shows treatment center name, not clinic type). Clinical screen correctly flagged benzo taper risk, which is medically important. The summer program / teacher schedule detail showed genuine attentiveness to the caller's situation. Near-flawless call.",
        },
    }


def _syn_030(ctx: dict) -> dict:
    """Objection heavy: cost is genuine barrier. Agent creative with options; close is vague."""
    a, c = ctx["agent_first"], ctx["caller_first"]
    carrier, mid, grp = ctx["carrier"], ctx["member_id"], ctx["group_number"]

    transcript = _turns([
        ("agent", 0, f"Thank you for calling {TREATMENT_CENTER}, this is {a}."),
        ("caller", 4, f"Hi, I'm {c}. I want to get help for meth use but I'm really worried about cost. I looked at your website and I couldn't find pricing and it's making me anxious."),
        ("agent", 16, f"That's a completely valid concern and I'm glad you called to ask rather than just not calling. Cost transparency is something we should be better at. Let me walk you through the real picture. Do you have insurance?"),
        ("caller", 28, f"Yes, {carrier}. But I have a high deductible. Member ID {mid}, group {grp}."),
        ("agent", 42, "High deductible plans are common, and it can mean you owe more out of pocket before coverage kicks in. Let me be honest about that rather than oversell it. How high is your deductible?"),
        ("caller", 52, "Four thousand dollars. I've met about half of it this year."),
        ("agent", 60, f"Okay, so you have about two thousand left. Depending on our contracted rate with {carrier}, you might owe that two thousand before insurance takes over. But there are options. We have a sliding scale based on income for people in your situation, and we work with CareCredit — 0% for twelve months if approved. We've also had patients successfully apply for state substance use treatment funds that can cover the gap entirely. It depends on your income and state of residence."),
        ("caller", 88, "I didn't know any of those options existed."),
        ("agent", 94, f"Most people don't. Our financial counsellor can run through all three with you in about fifteen minutes and give you actual numbers. That call is free and there's no obligation. Would that be helpful?"),
        ("caller", 106, "Yes, very much."),
        ("agent", 110, "Good. Let me tell you a little about what you'd be getting in terms of the clinical side, so the financial conversation is grounded. What substance are you looking to address?"),
        ("caller", 120, "Meth. About eighteen months. Daily now."),
        ("agent", 128, "And are you experiencing any withdrawal or health issues when you try to stop?"),
        ("caller", 134, "Mostly exhaustion and depression. Nothing physical like alcohol."),
        ("agent", 142, "That's consistent with stimulant withdrawal — it's real even if it's not physically dangerous the way opioid or alcohol withdrawal can be. Our clinical team will assess level of care, but for daily meth use at eighteen months, IOP is often the starting point. Now — someone from our financial team will follow up with you."),
        ("caller", 162, "When?"),
        ("agent", 166, "We'll be in touch."),
        ("caller", 170, "Today?"),
        ("agent", 174, "Yes, today. Keep your phone handy."),
        ("caller", 180, "Okay. Thank you."),
    ])

    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 4,
        "clinical_screening": 3,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 2,
        "compliance_language": 5,
    }

    return {
        "call_id": "syn_030",
        "generated_at": GENERATED_AT,
        "seed": ctx["seed"],
        "scenario_type": "objection_heavy",
        "metadata": {
            "duration_seconds": 190,
            "caller_type": "patient",
            "campaign_source": "website",
            "tracking_number": ctx["tracking_number"],
            "agent_id": ctx["agent_id"],
            "agent_name": f"{ctx['agent_first']} {ctx['agent_last']}",
        },
        "transcript": transcript,
        "gold_labels": {
            "call_id": "syn_030",
            "scenario_type": "objection_heavy",
            "expected_scores": scores,
            "expected_overall": _calc_overall(scores),
            "compliance_override_triggered": False,
            "expected_flags": [],
            "escalation_required": False,
            "scenario_tags": ["patient-caller", "cost-barrier", "high-deductible", "financial-options-offered", "vague-close"],
            "coaching_notes": "Cost objection handled well — agent was honest about the deductible reality rather than minimising it, offered three concrete alternatives (sliding scale, CareCredit, state funds), and offered a free 15-minute financial counsellor call. Clinical screen adequate. The failure is the close: caller had to ask 'today?' twice before getting a concrete answer, and 'keep your phone handy' is not a specific next step. Dim 7 = 2. Strong middle, weak ending.",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# CALL REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

_CALL_BUILDERS = [
    ("syn_001", "excellent", 1, _syn_001),
    ("syn_002", "excellent", 2, _syn_002),
    ("syn_003", "excellent", 3, _syn_003),
    ("syn_004", "weak", 1, _syn_004),
    ("syn_005", "weak", 2, _syn_005),
    ("syn_006", "weak", 3, _syn_006),
    ("syn_007", "family_caller", 1, _syn_007),
    ("syn_008", "family_caller", 2, _syn_008),
    ("syn_009", "family_caller", 3, _syn_009),
    ("syn_010", "urgency", 1, _syn_010),
    ("syn_011", "urgency", 2, _syn_011),
    ("syn_012", "urgency", 3, _syn_012),
    ("syn_013", "objection_heavy", 1, _syn_013),
    ("syn_014", "objection_heavy", 2, _syn_014),
    ("syn_015", "objection_heavy", 3, _syn_015),
    ("syn_016", "excellent", 4, _syn_016),
    ("syn_017", "excellent", 5, _syn_017),
    ("syn_018", "excellent", 6, _syn_018),
    ("syn_019", "weak", 4, _syn_019),
    ("syn_020", "weak", 5, _syn_020),
    ("syn_021", "weak", 6, _syn_021),
    ("syn_022", "family_caller", 4, _syn_022),
    ("syn_023", "family_caller", 5, _syn_023),
    ("syn_024", "family_caller", 6, _syn_024),
    ("syn_025", "urgency", 4, _syn_025),
    ("syn_026", "urgency", 5, _syn_026),
    ("syn_027", "urgency", 6, _syn_027),
    ("syn_028", "objection_heavy", 4, _syn_028),
    ("syn_029", "objection_heavy", 5, _syn_029),
    ("syn_030", "objection_heavy", 6, _syn_030),
]


def generate_all(output_dir: Path) -> None:
    """Generate all 30 synthetic calls and write them to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    gold_labels: dict = {}
    manifest: list = []

    for call_id, scenario, idx, builder in _CALL_BUILDERS:
        ctx = _make_ctx(scenario, idx)
        call = builder(ctx)

        filename = f"{call_id}_{scenario}.json"
        out_path = output_dir / filename
        with open(out_path, "w") as f:
            json.dump(call, f, indent=2)
        overall = call["gold_labels"]["expected_overall"]
        print(f"  wrote {filename}  (overall={overall})")

        gold_labels[call_id] = call["gold_labels"]
        manifest.append({
            "call_id": call_id,
            "filename": filename,
            "scenario_type": scenario,
            "seed": call["seed"],
            "expected_overall": overall,
            "compliance_violation": call["gold_labels"]["compliance_override_triggered"],
            "escalation_required": call["gold_labels"]["escalation_required"],
        })

    gold_path = output_dir / "gold-labels.json"
    with open(gold_path, "w") as f:
        json.dump(gold_labels, f, indent=2)
    print(f"  wrote gold-labels.json  ({len(gold_labels)} calls)")

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump({"total_calls": len(manifest), "calls": manifest}, f, indent=2)
    print(f"  wrote manifest.json  ({len(manifest)} entries)")
