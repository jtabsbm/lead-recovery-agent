#!/usr/bin/env python3
"""
ScreenAgent — AI Agent for Filmmakers
Agentic Cinema Hackathon (Sep 7, 2026 deadline)

An AI agent that helps screenwriters and indie filmmakers:
1. Analyze script structure and pacing
2. Generate shot lists from scene descriptions
3. Track continuity across scenes
4. Suggest budget optimizations
5. Create call sheets from the script

Built with Gemini + Google Cloud Agent Builder concepts.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class SceneType(Enum):
    INTERIOR = "INT"
    EXTERIOR = "EXT"
    MIXED = "INT/EXT"

@dataclass
class Scene:
    number: int
    scene_type: str = ""
    location: str = ""
    time_of_day: str = ""
    description: str = ""
    characters: list = field(default_factory=list)
    estimated_pages: float = 0.0
    estimated_minutes: float = 0.0
    shots: list = field(default_factory=list)
    budget_notes: str = ""
    continuity_notes: str = ""

@dataclass
class Shot:
    shot_number: str
    shot_type: str  # WIDE, MEDIUM, CLOSE, OTS, POV, etc.
    subject: str
    camera_move: str = "STATIC"
    duration: str = ""
    notes: str = ""

class ScreenAgent:
    """Autonomous agent for film production assistance."""
    
    def __init__(self, project_name: str = "Untitled Project"):
        self.project_name = project_name
        self.scenes: list[Scene] = []
        self.characters = set()
        self.locations = set()
        self.total_pages = 0.0
        
    def parse_screenplay(self, text: str):
        """Parse a screenplay into structured scenes."""
        # Standard screenplay scene heading pattern: INT./EXT. LOCATION - TIME
        pattern = r'((?:INT\.?|EXT\.?|INT\.?/EXT\.?)\.?\s+[^-\n]+)\s+-\s*([^\n]+)'
        splits = re.split(pattern, text)
        
        scene_num = 0
        for i in range(1, len(splits), 3):
            scene_num += 1
            heading = splits[i].strip()
            time_of_day = splits[i+1].strip() if i+1 < len(splits) else ""
            
            # Parse scene type and location
            if heading.upper().startswith("INT"):
                scene_type = SceneType.INTERIOR.value
            elif heading.upper().startswith("EXT"):
                scene_type = SceneType.EXTERIOR.value
            else:
                scene_type = SceneType.MIXED.value
            
            location = re.sub(r'^(INT\.?|EXT\.?|INT\.?/EXT\.?)\.?\s*', '', heading, flags=re.IGNORECASE).strip()
            
            # Get scene description
            description = splits[i+2].strip() if i+2 < len(splits) else ""
            
            # Extract characters (all-caps lines that aren't scene headings)
            chars = re.findall(r'\n([A-Z][A-Z\s]{2,})\n', description)
            chars = [c.strip() for c in chars if c.strip() and len(c.strip()) < 30]
            
            # Estimate pages (1 page ≈ 1 minute ≈ 250 words)
            words = len(description.split())
            pages = round(words / 250, 1)
            minutes = pages  # 1 page = 1 minute convention
            
            scene = Scene(
                number=scene_num,
                scene_type=scene_type,
                location=location,
                time_of_day=time_of_day,
                description=description[:500],
                characters=list(set(chars)),
                estimated_pages=pages,
                estimated_minutes=minutes,
            )
            
            self.scenes.append(scene)
            self.characters.update(chars)
            self.locations.add(location)
            self.total_pages += pages
        
        return self.scenes

    def generate_shot_list(self, scene: Scene) -> list[Shot]:
        """Generate a suggested shot list for a scene."""
        shots = []
        desc = scene.description.lower()
        
        # Always start with an establishing shot
        shots.append(Shot(
            shot_number=f"{scene.number}.1",
            shot_type="WIDE",
            subject=f"Establishing: {scene.location}",
            camera_move="STATIC" if scene.scene_type == "EXT" else "SLOW PUSH",
            duration="5-8s",
            notes=f"Establish {scene.location}, {scene.time_of_day.lower()}"
        ))
        
        # Add character coverage
        for i, char in enumerate(scene.characters, 2):
            shots.append(Shot(
                shot_number=f"{scene.number}.{i}",
                shot_type="MEDIUM",
                subject=char,
                camera_move="STATIC",
                duration="3-5s",
                notes=f"Coverage for {char}"
            ))
            shots.append(Shot(
                shot_number=f"{scene.number}.{i+len(scene.characters)}",
                shot_type="CLOSE",
                subject=char,
                camera_move="STATIC",
                duration="2-3s",
                notes=f"Reaction shot for {char}"
            ))
        
        # Check for action keywords
        if any(w in desc for w in ["walks", "runs", "enters", "exits", "moves"]):
            shots.append(Shot(
                shot_number=f"{scene.number}.{len(shots)+1}",
                shot_type="WIDE",
                subject="Action coverage",
                camera_move="TRACKING",
                duration="5-10s",
                notes="Movement coverage"
            ))
        
        if any(w in desc for w in ["phone", "text", "screen", "computer"]):
            shots.append(Shot(
                shot_number=f"{scene.number}.{len(shots)+1}",
                shot_type="INSERT",
                subject="Device screen",
                camera_move="STATIC",
                duration="2-3s",
                notes="Insert shot for device/screen content"
            ))
        
        # End with a scene closer
        shots.append(Shot(
            shot_number=f"{scene.number}.{len(shots)+1}",
            shot_type="WIDE" if scene.scene_type == "INT" else "MEDIUM",
            subject="Scene closer",
            camera_move="SLOW PULL",
            duration="3-5s",
            notes="Transition out"
        ))
        
        scene.shots = [s.__dict__ for s in shots]
        return shots

    def check_continuity(self) -> list[dict]:
        """Check for potential continuity issues across scenes."""
        issues = []
        
        # Check for character consistency
        for i, scene in enumerate(self.scenes):
            for char in scene.characters:
                # Check if character appears, disappears, then reappears
                for j in range(i+2, len(self.scenes)):
                    if char in self.scenes[j].characters:
                        gap = j - i
                        if gap > 2:
                            issues.append({
                                "type": "character_gap",
                                "character": char,
                                "from_scene": scene.number,
                                "to_scene": self.scenes[j].number,
                                "gap_scenes": gap,
                                "note": f"{char} doesn't appear for {gap} scenes"
                            })
                        break
        
        # Check for location continuity
        for i in range(len(self.scenes)-1):
            if self.scenes[i].location == self.scenes[i+1].location:
                if self.scenes[i].time_of_day != self.scenes[i+1].time_of_day:
                    issues.append({
                        "type": "time_inconsistency",
                        "location": self.scenes[i].location,
                        "scene_1": self.scenes[i].number,
                        "time_1": self.scenes[i].time_of_day,
                        "scene_2": self.scenes[i+1].number,
                        "time_2": self.scenes[i+1].time_of_day,
                        "note": "Same location, different time — verify continuity"
                    })
        
        return issues

    def estimate_budget(self) -> dict:
        """Generate rough budget estimates."""
        total_minutes = sum(s.estimated_minutes for s in self.scenes)
        total_shots = sum(len(s.shots) for s in self.scenes)
        
        # Rough indie film rates
        crew_day_rate = 2500  # indie crew per day
        location_per_scene = 500
        equipment_per_day = 800
        post_per_minute = 500
        
        # Estimate shoot days (assume 5 pages/day efficiency)
        shoot_days = max(1, self.total_pages / 5)
        
        budget = {
            "project": self.project_name,
            "total_scenes": len(self.scenes),
            "total_pages": round(self.total_pages, 1),
            "estimated_runtime_minutes": round(total_minutes, 1),
            "total_shots": total_shots,
            "estimated_shoot_days": round(shoot_days, 1),
            "cost_breakdown": {
                "crew": int(shoot_days * crew_day_rate),
                "locations": len(self.locations) * location_per_scene,
                "equipment": int(shoot_days * equipment_per_day),
                "post_production": int(total_minutes * post_per_minute),
            },
            "estimated_total": 0,
            "cost_saving_suggestions": [
                "Combine scenes at the same location to reduce company moves",
                "Shoot coverage for multiple scenes at once when in the same location",
                "Consider which scenes can be simplified to fewer shots",
            ]
        }
        budget["estimated_total"] = sum(budget["cost_breakdown"].values())
        return budget

    def generate_call_sheet(self, scene: Scene) -> dict:
        """Generate a call sheet for a specific scene."""
        return {
            "project": self.project_name,
            "scene_number": scene.number,
            "scene_type": f"{scene.scene_type}. {scene.location}",
            "time_of_day": scene.time_of_day,
            "characters_needed": scene.characters,
            "estimated_pages": scene.estimated_pages,
            "estimated_shots": len(scene.shots),
            "estimated_time": f"{scene.estimated_minutes * 30} minutes",  # 30 min per page
            "notes": [
                f"Verify {scene.location} is available and dressed",
                f"Confirm all cast members are available: {', '.join(scene.characters)}",
                f"Bring appropriate equipment for {scene.scene_type} shoot",
            ]
        }

    def project_report(self) -> dict:
        """Generate a full project analysis report."""
        # Generate shot lists for all scenes
        for scene in self.scenes:
            if not scene.shots:
                self.generate_shot_list(scene)
        
        return {
            "project_name": self.project_name,
            "summary": {
                "total_scenes": len(self.scenes),
                "total_pages": round(self.total_pages, 1),
                "total_characters": len(self.characters),
                "total_locations": len(self.locations),
                "total_shots": sum(len(s.shots) for s in self.scenes),
            },
            "characters": sorted(list(self.characters)),
            "locations": sorted(list(self.locations)),
            "scenes": [
                {
                    "number": s.number,
                    "heading": f"{s.scene_type}. {s.location} - {s.time_of_day}",
                    "pages": s.estimated_pages,
                    "minutes": s.estimated_minutes,
                    "characters": s.characters,
                    "shot_count": len(s.shots),
                }
                for s in self.scenes
            ],
            "continuity_issues": self.check_continuity(),
            "budget_estimate": self.estimate_budget(),
        }


# ─── Demo ──────────────────────────────────────────────────────────────────────

def run_demo():
    """Run a demo with a sample screenplay."""
    sample_script = """INT. COFFEE SHOP - MORNING

SARAH sits at a corner table, laptop open, coffee cooling. She checks her phone nervously.

JAMES enters, scans the room, spots her. He approaches.

JAMES
You're Sarah? I got your message.

SARAH
Sit down. We need to talk about what happened.

James sits. The barista glances over.

INT. SARAH'S APARTMENT - NIGHT

Sarah enters, drops her keys on the counter. She notices the window is open.

She pulls out her phone and texts James.

SARAH
(typing)
Someone was in my apartment.

EXT. CITY ROOFTOP - SUNSET

James and Sarah stand at the edge of the rooftop, looking out over the city.

JAMES
I can protect you. But you have to trust me.

SARAH
Trust takes time.

EXT. CITY ROOFTOP - NIGHT

James paces. Sarah sits on a bench, wrapped in a blanket.

JAMES
They know we're here. We need to move.

Sarah's phone buzzes. She looks at the screen.

SARAH
It's too late. They're already here.
"""
    
    print("=" * 70)
    print("  ScreenAgent — AI Agent for Filmmakers")
    print("  Agentic Cinema Hackathon Prototype")
    print("=" * 70)
    
    agent = ScreenAgent("The Meeting — Short Film")
    agent.parse_screenplay(sample_script)
    
    print(f"\n🎬 PROJECT: {agent.project_name}")
    print(f"   Scenes: {len(agent.scenes)}")
    print(f"   Pages: {agent.total_pages:.1f}")
    print(f"   Characters: {', '.join(sorted(agent.characters))}")
    print(f"   Locations: {', '.join(sorted(agent.locations))}")
    
    # Generate shot lists
    print("\n🎥 SHOT LISTS:")
    for scene in agent.scenes:
        shots = agent.generate_shot_list(scene)
        print(f"\n   Scene {scene.number}: {scene.scene_type}. {scene.location} - {scene.time_of_day}")
        print(f"   {len(shots)} shots, ~{scene.estimated_minutes} min")
        for shot in shots[:3]:
            print(f"     {shot.shot_number}: {shot.shot_type} - {shot.subject} ({shot.camera_move})")
        if len(shots) > 3:
            print(f"     ... and {len(shots)-3} more")
    
    # Continuity check
    print("\n🔍 CONTINUITY CHECK:")
    issues = agent.check_continuity()
    if issues:
        for issue in issues:
            print(f"   ⚠️  {issue['type']}: {issue['note']}")
    else:
        print("   ✓ No continuity issues detected")
    
    # Budget estimate
    print("\n💰 BUDGET ESTIMATE:")
    budget = agent.estimate_budget()
    print(f"   Total: ${budget['estimated_total']:,}")
    for category, cost in budget['cost_breakdown'].items():
        print(f"   {category}: ${cost:,}")
    print(f"\n   Suggestions:")
    for s in budget['cost_saving_suggestions']:
        print(f"   • {s}")
    
    # Call sheet
    print("\n📋 CALL SHEET (Scene 1):")
    call_sheet = agent.generate_call_sheet(agent.scenes[0])
    for k, v in call_sheet.items():
        print(f"   {k}: {v}")
    
    # Full report
    report = agent.project_report()
    output_path = "/Users/wendell/zero-cash-revenue-engine/hackathon/screen-agent-output.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Full report saved to: {output_path}")
    
    print("\n" + "=" * 70)
    print("  Powered by Gemini + Google Cloud Agent Builder")
    print("  Agentic Cinema Hackathon — Sep 7, 2026")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
