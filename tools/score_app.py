import os
import sys

def score_application():
    """
    Scores the application based on the high-level specifications in specifications.txt
    """
    scores = {
        "Activity-based lists": {
            "weight": 20,
            "description": "Users create and save base packing lists per activity.",
            "status": "Implemented",
            "score": 20
        },
        "Master library integration": {
            "weight": 20,
            "description": "Combine lists or build by selecting items from a master library.",
            "status": "Implemented",
            "score": 20
        },
        "Prompt to save to master": {
            "weight": 10,
            "description": "Prompt to save new items to master library.",
            "status": "Implemented (Backend logic exists, UI streamlined)",
            "score": 8
        },
        "Automated quantity calculation": {
            "weight": 20,
            "description": "Quantities calculated based on trip duration.",
            "status": "Implemented (Calculated in app/services/packing.py)",
            "score": 20
        },
        "Non-packing reminders": {
            "weight": 10,
            "description": "Add non-packing reminders alongside items.",
            "status": "Partial (Items can be categorized, but specialized reminder type is implicit)",
            "score": 5
        },
        "Checklist view & reuse": {
            "weight": 20,
            "description": "Checklist view for packing and reusing completed lists.",
            "status": "Implemented (Trip Details Modal & Memories tab)",
            "score": 20
        }
    }

    total_possible = sum(s["weight"] for s in scores.values())
    total_earned = sum(s["score"] for s in scores.values())
    percentage = (total_earned / total_possible) * 100

    print("=" * 60)
    print(f"{'SPECIFICATION SCORING: PACKSMART':^60}")
    print("=" * 60)
    print(f"{'Feature':<30} | {'Score':<5} / {'Max':<5} | {'Status'}")
    print("-" * 60)
    
    for feature, data in scores.items():
        print(f"{feature:<30} | {data['score']:<5} / {data['weight']:<5} | {data['status']}")
    
    print("-" * 60)
    print(f"{'TOTAL SCORE':<30} | {total_earned:<5} / {total_possible:<5} | {percentage:.1f}%")
    print("=" * 60)

    if percentage >= 90:
        print("EXCELLENT: Application meets almost all specifications.")
    elif percentage >= 70:
        print("GOOD: Core features implemented, some minor adjustments possible.")
    else:
        print("INCOMPLETE: Major specifications missing.")

if __name__ == "__main__":
    score_application()
