"""
G7X REAL36 Real Catalog Builder v1
- DOCS\REAL36_MISSION_SPEC_V1.md 기준
- GPTORDER\REAL36_REAL_A.txt (36줄) 생성
"""

import sys
from pathlib import Path

def main():
    ssot_root = Path(r"C:\g7core\g7_v1")
    gptorder_dir = ssot_root / "GPTORDER"

    # REAL36_REAL_A.txt 생성 (36개 실전 미션)
    missions = [
        "Write a professional email requesting a meeting with a client.",
        "Summarize the key points from a 5-page technical document.",
        "Create a to-do list for a software project sprint.",
        "Draft a brief project status update for stakeholders.",
        "Write a polite response to a customer complaint.",
        "Generate 3 creative taglines for a new product launch.",
        "Explain the concept of cloud computing in simple terms.",
        "List 5 best practices for remote team collaboration.",
        "Write a short bio for a professional LinkedIn profile.",
        "Create an agenda for a 1-hour team meeting.",
        "Draft a thank-you note after a job interview.",
        "Summarize the main features of a software release.",
        "Write instructions for setting up a new tool.",
        "Generate 3 quiz questions about project management.",
        "Create a checklist for onboarding a new employee.",
        "Write a brief case study about a successful project.",
        "Draft a newsletter introduction for a company update.",
        "List 5 tips for improving productivity.",
        "Write a short description of a team member's role.",
        "Create a simple FAQ section for a product.",
        "Draft a polite decline message for a meeting request.",
        "Summarize quarterly goals in 3 bullet points.",
        "Write a motivational message for team members.",
        "Generate 3 ideas for a team-building activity.",
        "Create a list of resources for learning Python.",
        "Write a short announcement about a policy change.",
        "Draft a follow-up email after a client call.",
        "List 5 common mistakes in code reviews.",
        "Write a brief tutorial on using Git commands.",
        "Create a template for weekly progress reports.",
        "Draft a congratulatory message for a team achievement.",
        "Summarize the benefits of continuous integration.",
        "Write 3 tips for effective time management.",
        "Generate a list of action items from meeting notes.",
        "Create a simple user guide for a new feature.",
        "Write a closing statement for a project retrospective."
    ]

    output_file = gptorder_dir / "REAL36_REAL_A.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for mission in missions:
            f.write(mission + "\n")

    print(f"[CREATED] {output_file} ({len(missions)} missions)")
    print(f"[SUCCESS] REAL36_REAL_A.txt generated")
    return 0

if __name__ == "__main__":
    sys.exit(main())
