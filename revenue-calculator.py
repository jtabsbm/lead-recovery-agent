#!/usr/bin/env python3
"""
CallbackOps Revenue Calculator
Calculates path to $1,000/day profit from different client mixes.
"""

def calculate_revenue_path():
    """Show different paths to $30,000/month ($1,000/day average)."""
    
    tiers = {
        "Pilot ($500 one-time)": {"price": 500, "type": "one-time"},
        "Founding ($1,500/mo)": {"price": 1500, "type": "monthly"},
        "Standard ($2,500/mo)": {"price": 2500, "type": "monthly"},
        "Growth ($4,000/mo)": {"price": 4000, "type": "monthly"},
        "Package 1 - Prospect Sprint ($500)": {"price": 500, "type": "one-time"},
        "Package 2 - Inbox Triage ($650)": {"price": 650, "type": "one-time"},
        "Package 2 - Inbox Triage Standard ($1,100)": {"price": 1100, "type": "one-time"},
    }
    
    print("=" * 60)
    print("  REVENUE CALCULATOR — Path to $1,000/day ($30K/month)")
    print("=" * 60)
    
    # Path 1: All standard clients
    print("\n📊 PATH 1: All Standard Clients ($2,500/mo)")
    clients_needed = 30000 // 2500
    print(f"   Clients needed: {clients_needed}")
    print(f"   Monthly revenue: ${clients_needed * 2500:,}")
    print(f"   Daily average: ${clients_needed * 2500 / 30:.0f}/day")
    
    # Path 2: Mix of tiers
    print("\n📊 PATH 2: Mixed Tiers")
    mix = [
        ("Founding", 1500, 3),
        ("Standard", 2500, 8),
        ("Growth", 4000, 3),
    ]
    total = 0
    for name, price, count in mix:
        rev = price * count
        total += rev
        print(f"   {name} ({price}/mo) × {count} = ${rev:,}/mo")
    print(f"   Total: ${total:,}/mo = ${total/30:.0f}/day")
    
    # Path 3: Recurring + one-time packages
    print("\n📊 PATH 3: Recurring + Package Sales")
    recurring = 6 * 2500  # 6 standard clients
    packages = 4 * 800  # 4 packages per month at avg $800
    total3 = recurring + packages
    print(f"   Recurring: 6 × $2,500 = ${recurring:,}/mo")
    print(f"   Packages: 4 × $800 avg = ${packages:,}/mo")
    print(f"   Total: ${total3:,}/mo = ${total3/30:.0f}/day")
    print(f"   Gap to target: ${max(0, 30000 - total3):,}/mo")
    print(f"   Additional clients needed at $2,500: {(30000 - total3) // 2500}")
    
    # Path 4: Aggressive growth
    print("\n📊 PATH 4: Aggressive (12 Standard + Packages)")
    recurring4 = 12 * 2500
    packages4 = 8 * 800
    total4 = recurring4 + packages4
    print(f"   Recurring: 12 × $2,500 = ${recurring4:,}/mo")
    print(f"   Packages: 8 × $800 avg = ${packages4:,}/mo")
    print(f"   Total: ${total4:,}/mo = ${total4/30:.0f}/day")
    print(f"   TARGET EXCEEDED by ${total4 - 30000:,}/mo")
    
    # Conversion funnel
    print("\n" + "=" * 60)
    print("  SALES FUNNEL — To get 12 standard clients")
    print("=" * 60)
    
    for close_rate in [0.10, 0.15, 0.20, 0.25]:
        for reply_rate in [0.05, 0.10, 0.15]:
            conversations = 12 / close_rate
            prospects = conversations / reply_rate
            print(f"   Reply {reply_rate:.0%} → Close {close_rate:.0%}: "
                  f"Need {prospects:.0f} prospects → {conversations:.0f} convos → 12 clients")
    
    # Timeline
    print("\n" + "=" * 60)
    print("  REALISTIC TIMELINE")
    print("=" * 60)
    timeline = [
        ("Week 1", "30 prospects contacted", 0, "Sending now"),
        ("Week 2", "Follow-ups + 20 more prospects", 0, "Awaiting replies"),
        ("Week 3", "First pilot calls", 500, "1 pilot possible"),
        ("Week 4", "First paying client", 1500, "Founding rate"),
        ("Month 2", "3 clients", 4500, "$150/day"),
        ("Month 3", "6 clients + 2 packages", 16600, "$553/day"),
        ("Month 4", "9 clients + 4 packages", 25700, "$856/day"),
        ("Month 5", "12 clients + 6 packages", 34800, "$1,160/day ✓"),
    ]
    print(f"   {'Phase':<10} {'Milestone':<35} {'Revenue':<12} {'Daily Avg'}")
    for phase, milestone, rev, note in timeline:
        daily = f"${rev/30:.0f}/day" if rev > 0 else "$0/day"
        print(f"   {phase:<10} {milestone:<35} ${rev:<10,} {daily} ({note})")
    
    print("\n" + "=" * 60)
    print("  SUPPLEMENTAL INCOME (while building to target)")
    print("=" * 60)
    supplemental = [
        ("DataAnnotation", "$75-150/hr", "20 hrs/wk", "$6,000-12,000/mo"),
        ("Outlier", "$20-40/hr", "20 hrs/wk", "$1,600-3,200/mo"),
        ("Prolific", "$8-15/hr", "10 hrs/wk", "$320-600/mo"),
        ("Hackathon prizes", "Variable", "1-2 events", "$0-50,000"),
        ("Upwork/Contra", "$500-1100/project", "2/mo", "$1,000-2,200/mo"),
    ]
    print(f"   {'Source':<20} {'Rate':<15} {'Effort':<12} {'Potential'}")
    for src, rate, effort, potential in supplemental:
        print(f"   {src:<20} {rate:<15} {effort:<12} {potential}")


if __name__ == "__main__":
    calculate_revenue_path()
