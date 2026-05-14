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
]


def generate_all(output_dir: Path) -> None:
    """Generate all 15 synthetic calls and write them to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    gold_labels: dict = {}

    for call_id, scenario, idx, builder in _CALL_BUILDERS:
        ctx = _make_ctx(scenario, idx)
        call = builder(ctx)

        filename = f"{call_id}_{scenario}.json"
        out_path = output_dir / filename
        with open(out_path, "w") as f:
            json.dump(call, f, indent=2)
        print(f"  wrote {filename}  (overall={call['gold_labels']['expected_overall']})")

        gold_labels[call_id] = call["gold_labels"]

    gold_path = output_dir / "gold-labels.json"
    with open(gold_path, "w") as f:
        json.dump(gold_labels, f, indent=2)
    print(f"  wrote gold-labels.json  ({len(gold_labels)} calls)")
