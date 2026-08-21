# ============================================================
# CHAPTER 8: PROBABILITY & BRAIN TEASERS
# Practice in: Python (for simulations) / Whiteboard (for logic)
# Asked at: Google, Meta, Amazon, D.E. Shaw, Goldman Sachs
# ============================================================

import random
import numpy as np
from fractions import Fraction

# ============================================================
# SECTION 1: Classic Probability Problems
# ============================================================

# Q1: Monty Hall Problem
# You pick door 1. Host opens door 3 (goat). Should you switch?
# Answer: YES. Switching wins 2/3 of the time.

def monty_hall_simulation(n=100000, switch=True):
    wins = 0
    for _ in range(n):
        car    = random.randint(1, 3)
        choice = random.randint(1, 3)
        # Host opens a door that is not your choice and not the car
        remaining = [d for d in [1, 2, 3] if d != choice and d != car]
        host_opens = random.choice(remaining)
        if switch:
            new_choice = [d for d in [1, 2, 3] if d != choice and d != host_opens][0]
        else:
            new_choice = choice
        if new_choice == car:
            wins += 1
    return wins / n

print(f"Monty Hall - Stay:   {monty_hall_simulation(switch=False):.3f} (expected 0.333)")
print(f"Monty Hall - Switch: {monty_hall_simulation(switch=True):.3f}  (expected 0.667)")

# ============================================================
# Q2: Birthday Problem
# ============================================================
# How many people needed in a room for 50% chance 2 share a birthday?
# Answer: 23 (surprisingly low!)

def birthday_probability(n_people):
    """Probability that at least 2 people share a birthday"""
    no_match = 1.0
    for i in range(n_people):
        no_match *= (365 - i) / 365
    return 1 - no_match

print("\nBirthday Problem:")
for n in [10, 23, 30, 50, 70]:
    print(f"  {n} people: {birthday_probability(n):.3f} chance of shared birthday")

# ============================================================
# Q3: Conditional Probability — Bayes' Theorem
# ============================================================
# P(A|B) = P(B|A) × P(A) / P(B)
#
# Q: Disease test is 99% accurate. 1% of population has disease.
#    You test positive. What's probability you actually have disease?

p_disease    = 0.01   # prior: 1% prevalence
p_pos_given_disease = 0.99  # sensitivity
p_pos_given_no_disease = 0.01  # false positive rate

# P(positive) = P(pos|disease)×P(disease) + P(pos|no_disease)×P(no_disease)
p_pos = (p_pos_given_disease * p_disease +
         p_pos_given_no_disease * (1 - p_disease))

# Bayes: P(disease|positive)
p_disease_given_pos = (p_pos_given_disease * p_disease) / p_pos

print(f"\nBayes Theorem — Disease Test:")
print(f"  Test positive — Prob you have disease: {p_disease_given_pos:.2%}")
print(f"  (Answer: only {p_disease_given_pos:.1%}! — Base rate matters!)")

# ============================================================
# SECTION 2: Expected Value Problems
# ============================================================

# Q: Dice game — roll a fair die, earn that many dollars.
#    You can re-roll once. What's the optimal strategy?
#    Strategy: Re-roll if result < expected value of second roll
#              E[second roll] = (1+2+3+4+5+6)/6 = 3.5
#              So re-roll if first roll <= 3

# Simulate
def dice_game_optimal(n=100000):
    earnings = []
    for _ in range(n):
        roll1 = random.randint(1, 6)
        if roll1 < 3.5:  # re-roll
            roll2 = random.randint(1, 6)
            earnings.append(roll2)
        else:
            earnings.append(roll1)
    return np.mean(earnings)

print(f"\nDice Game Expected Earnings (optimal strategy): ${dice_game_optimal():.3f}")
print(f"  (Analytical: E = 3/6 × 3.5 + 4/6 × (4+5+6)/3 = {3/6*3.5 + 3/6*5:.3f})")

# ============================================================
# SECTION 3: Coin Flip Problems
# ============================================================

# Q: Flip a biased coin (P(H)=0.6) until you get 2 heads in a row. 
#    What's the expected number of flips?
# This is a classic absorbing Markov chain problem.

def simulate_two_heads_in_row(p_head=0.6, n=50000):
    total_flips = []
    for _ in range(n):
        flips = 0
        consecutive = 0
        while consecutive < 2:
            flips += 1
            if random.random() < p_head:
                consecutive += 1
            else:
                consecutive = 0
        total_flips.append(flips)
    return np.mean(total_flips)

print(f"\nExpected flips for 2 consecutive heads (p=0.6): {simulate_two_heads_in_row():.2f}")

# ============================================================
# SECTION 4: Sampling — Reservoir Sampling
# ============================================================
# Q: Pick k random items from a stream of unknown size N (1 pass!)
# This is asked at Google/Amazon for big data context

def reservoir_sample(stream, k):
    """Randomly sample k items from a stream in one pass (O(k) memory)"""
    reservoir = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
    return reservoir

stream = list(range(1, 1001))
sample = reservoir_sample(stream, 10)
print(f"\nReservoir Sample of 10 from 1-1000: {sorted(sample)}")

# ============================================================
# SECTION 5: Common Interview Questions (Know the answers)
# ============================================================
"""
Q1: What is the probability of getting exactly 3 heads in 5 fair coin flips?
    Binomial: C(5,3) × (0.5)^3 × (0.5)^2 = 10/32 = 0.3125

Q2: Two people agree to meet between 12-1pm. Each waits 15 min.
    What's the probability they meet?
    Area method: 1 - (45/60)^2 = 1 - 0.5625 = 0.4375

Q3: There are 3 red and 2 blue balls. Draw 2 without replacement.
    P(both red) = C(3,2)/C(5,2) = 3/10 = 0.30

Q4: You roll two dice. Given the sum is 7, what's P(first die is 3)?
    P(first=3 | sum=7) = P(first=3 AND sum=7) / P(sum=7)
                       = (1/36) / (6/36) = 1/6

Q5: What's P(at least one 6 in 4 rolls of a fair die)?
    P = 1 - P(no 6 in 4 rolls) = 1 - (5/6)^4 ≈ 0.518
"""

# Verify Q5
p_no_six = (5/6)**4
p_at_least_one_six = 1 - p_no_six
print(f"\nP(at least one 6 in 4 rolls): {p_at_least_one_six:.4f}")

# Monte Carlo verify
hits = sum(1 for _ in range(100000) if 6 in [random.randint(1,6) for _ in range(4)])
print(f"Monte Carlo verification:     {hits/100000:.4f}")

print("\n✅ Chapter 8: Probability & Brain Teasers complete!")
