import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.schemas.production_package import ProductionPackage, ChunkItem, FrameCompositionAudit, LeftSubjectAudit, RightSubjectAudit, PostCopy

pkg_data = {
    "project_id": "PROD_011_elainevanhausen_4",
    "reference_video": "elainevanhausen_4.mp4",
    "reference_duration_s": 30.16,
    "topic": "Coca-Cola scalp clarifying rinse for thinning middle part / mineral buildup",
    "brand": "Bennett Studio / Botanique",
    "avatar_name": "Rachel Bennett",
    "avatar_age": 47,
    "avatar_archetype": "Accessible Authority + Aspirational Expert (Salon Owner & Master Stylist)",
    "wardrobe_previous": "Blusa de seda blanca bajo delantal negro con bordado dorado Bennett Studio en el pecho",
    "wardrobe_assigned": "Blusa de seda blanca bajo delantal negro con bordado dorado 'Bennett Studio' en el pecho. Bob ondulado en capas con mechas platinadas. (Sin delantal para el CTA final).",
    "audio_voice_direction_anchor": "[AUDIO & VOICE CADENCE]: Pacing calibrated at 144 WPM (2.4 WPS, avg pause: 0.63s). Vocal Tone: Authentic Everyday UGC Confidence + Salon Authority. Inflection: Crisp American pronunciation with natural dynamic emphasis on operative solution words, zero studio reverb, domestic ambient room acoustics, natural breathing sync.",
    "standard_skeleton_25_30s": "Chunk 1: Visual Hook (0-5s) | Chunk 2: Reframe / Application (5-10s) | Chunk 3: Mechanism Reframe (10-15s) | Chunk 4: Mechanism Deep-Dive (15-20s) | Chunk 5: Payoff & Contrast (20-25s) | Chunk 6: Hard CTA (25-30s)",
    "chunks": [
        {
            "chunk_id": 1,
            "beat_name": "Visual Hook",
            "recommended_duration_s": 5,
            "word_count": 21,
            "voiceover_clean_tts": "I know this sounds completely insane, but pouring a glass bottle of classic Coke right over a thinning middle part changes everything.",
            "visual_direction": "Rachel stands in her luxury salon holding a vintage glass Coca-Cola bottle near her middle part line, looking at the camera with confident intrigue.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium close-up, eye level, 35mm lens, natural depth of field",
                "foreground_props": "Fluted walnut vanity counter with warm beige marble top, backlit capsule mirror",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "Facing camera, torso slightly turned 10 degrees left",
                    "pose": "Right hand holding classic glass soda bottle near crown area, left hand subtly gesturing to hair part line",
                    "hands_interaction": "Holding glass bottle upright near middle part",
                    "gaze_direction": "Looking directly into camera lens with confident and playful expression",
                    "outfit": "Crisp white silk blouse under black canvas stylist apron with 'Bennett Studio' embroidered in elegant gold cursive"
                },
                "right_subject": None,
                "environment_background": "Luxury salon Bennett Studio interior, warm beige plaster walls, backlit capsule mirrors, golden arched doorway, soft warm ambient lighting",
                "lighting_style": "Soft diffused salon vanity lighting, natural rim light on hair, hyper-realistic skin texture, 8k resolution, zero CGI artifacts"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 portrait photograph of a beautiful 47-year-old female salon owner with layered collarbone-length wavy bob hair and platinum highlights, wearing a crisp white silk blouse under a premium black canvas apron with elegant gold embroidery 'Bennett Studio' on the chest, holding a vintage glass soda bottle near her hair parting, luxury salon interior background with fluted walnut vanities and glowing warm arched mirrors, soft studio vanity lighting, cinematic photorealism, shot on 35mm f/1.8 --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Medium close-up of Rachel speaking directly to the camera with expressive facial animation, holding a glass bottle up and gesturing smoothly toward her hair part, natural head tilts, conversational hand movement, 4k ultra realistic motion, seamless loop",
            "asset_tags": ["rachel_bennett", "hook", "coke_bottle", "luxury_salon", "bennett_studio"],
            "continuity_notes": "Maintain consistent salon station lighting, platinum highlights on bob, and embroidered apron."
        },
        {
            "chunk_id": 2,
            "beat_name": "Reframe / Action",
            "recommended_duration_s": 5,
            "word_count": 19,
            "voiceover_clean_tts": "Massage it directly into your roots down to the ends, let the bubbles work for ten minutes, then rinse thoroughly.",
            "visual_direction": "Rachel demonstrating gentle scalp massage technique with her fingertips at the salon vanity, explaining the process clearly.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium shot, eye level, 35mm lens",
                "foreground_props": "Walnut vanity countertop, glass bottle resting on marble surface",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "Facing camera, direct eye contact",
                    "pose": "Both hands raised gently massaging scalp roots, demonstrating circular motion",
                    "hands_interaction": "Fingertips resting lightly in hair at temples and crown",
                    "gaze_direction": "Looking directly at camera with engaging instructional smile",
                    "outfit": "Crisp white silk blouse under black canvas stylist apron with 'Bennett Studio' in gold cursive"
                },
                "right_subject": None,
                "environment_background": "Luxury salon Bennett Studio interior, warm beige plaster walls, soft background blur",
                "lighting_style": "Warm ambient salon lighting, soft highlights catching wavy hair texture"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 medium shot of a 47-year-old female master stylist with layered wavy bob and platinum highlights, wearing a white silk blouse under a black salon apron with gold cursive embroidery 'Bennett Studio', both hands gently placed at her scalp demonstrating a hair care technique, smiling warmly at camera, luxury modern salon background, soft flattering lighting, 35mm lens --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Rachel speaking conversationally while lightly massaging her fingertips at her roots, smiling warmly at camera, natural fluid arm motion, realistic lip sync, lifelike human dynamics",
            "asset_tags": ["rachel_bennett", "action", "scalp_massage", "salon_interior"],
            "continuity_notes": "Consistent hair volume and wardrobe across cuts."
        },
        {
            "chunk_id": 3,
            "beat_name": "Mechanism Reframe",
            "recommended_duration_s": 5,
            "word_count": 18,
            "voiceover_clean_tts": "Most clients waste hundreds on clarifying treatments when the real secret is the mild phosphoric acid in Coca-Cola.",
            "visual_direction": "Rachel leans slightly against the walnut counter, gesturing with one hand while holding the glass bottle in the other, authoritative expert stance.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium close-up, eye level",
                "foreground_props": "Luxury product bottles neatly displayed on dark walnut floating shelves",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "3/4 turn towards camera",
                    "pose": "Left hand holding glass bottle, right hand open in explanatory gesture",
                    "hands_interaction": "Presenting bottle and gesturing emphatically",
                    "gaze_direction": "Confident direct eye contact with camera",
                    "outfit": "Crisp white silk blouse under black canvas stylist apron with 'Bennett Studio' in gold cursive"
                },
                "right_subject": None,
                "environment_background": "Luxury salon background with backlit cosmetic display and golden archway",
                "lighting_style": "Clean salon key light, rich golden rim light, crisp 4k detail"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 portrait of a 47yo chic female salon owner with platinum wavy bob, white silk blouse and black apron with gold 'Bennett Studio' lettering, gesturing knowingly with one hand while holding a vintage glass bottle, luxury salon display background with warm golden backlighting, sharp photorealistic detail --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Rachel explaining with authoritative hand gesture, slight head nod, clear articulate speech, smooth natural body movement, high definition realistic video",
            "asset_tags": ["rachel_bennett", "mechanism", "expert_reframe", "bennett_studio"],
            "continuity_notes": "Maintain exact golden embroidery on apron."
        },
        {
            "chunk_id": 4,
            "beat_name": "Mechanism Deep-Dive",
            "recommended_duration_s": 5,
            "word_count": 18,
            "voiceover_clean_tts": "It literally breaks down months of hard water mineral buildup and heavy silicone suffocating your hair follicles.",
            "visual_direction": "Rachel touches her crown and lifts a section of wavy hair to illustrate scalp breathing and root volume, speaking with scientific clarity.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium close-up, eye level, 50mm portrait lens",
                "foreground_props": "Walnut vanity station with soft amber ambient glow",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "Facing camera directly",
                    "pose": "One hand gently lifting hair at the crown to demonstrate root lift and clean scalp",
                    "hands_interaction": "Touching hair near parting line with delicate professional touch",
                    "gaze_direction": "Looking into camera with serious, informative expression",
                    "outfit": "Crisp white silk blouse under black canvas stylist apron with 'Bennett Studio' in gold cursive"
                },
                "right_subject": None,
                "environment_background": "Modern luxury salon Bennett Studio, soft warm depth of field",
                "lighting_style": "Soft directional beauty lighting highlighting hair shine and texture"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 close-up of a 47-year-old beautiful female stylist with healthy platinum-highlighted wavy bob, wearing a white silk blouse and black embroidered apron 'Bennett Studio', one hand gently lifting a section of hair at the crown showing clean roots and volume, luxury salon interior background, soft cinematic bokeh, 50mm lens --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Rachel gently touches and lifts her hair roots, talking passionately with authentic facial expressions and natural head movement, 4k ultra realistic video",
            "asset_tags": ["rachel_bennett", "mechanism_deepdive", "scalp_health", "root_volume"],
            "continuity_notes": "Hair shine and texture must look immaculate and healthy."
        },
        {
            "chunk_id": 5,
            "beat_name": "Payoff & Contrast",
            "recommended_duration_s": 5,
            "word_count": 16,
            "voiceover_clean_tts": "Why spend forty dollars on chemical detox scrubs when a two-dollar bottle delivers salon-grade scalp clarity?",
            "visual_direction": "Rachel standing proudly with open hands in a rhetorical, cheerful gesture, radiant hair bouncing softly in the warm salon glow.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium shot, eye level, 35mm lens",
                "foreground_props": "Luxury salon station with clean marble counter",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "Facing camera, standing tall and confident",
                    "pose": "Both hands open in an inviting, expressive shrug and smile",
                    "hands_interaction": "Open palms emphasizing the value comparison",
                    "gaze_direction": "Direct eye contact with bright, encouraging smile",
                    "outfit": "Crisp white silk blouse under black canvas stylist apron with 'Bennett Studio' in gold cursive"
                },
                "right_subject": None,
                "environment_background": "Luxury salon Bennett Studio with golden arched portal in background",
                "lighting_style": "Bright warm golden hour aesthetic salon lighting, vibrant hair shine"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 medium shot of a cheerful 47yo master stylist with radiant wavy bob and platinum highlights, wearing a white silk blouse under a black apron with gold embroidery 'Bennett Studio', gesturing with open hands in an expressive smile, luxury salon background with warm arched golden lights, cinematic realistic lighting --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Rachel smiling warmly, gesturing with open hands in a rhetorical payoff moment, fluid natural body posture, lifelike eye blinks and lip sync, photorealistic video",
            "asset_tags": ["rachel_bennett", "payoff", "contrast", "salon_glow"],
            "continuity_notes": "High energy transition leading into CTA."
        },
        {
            "chunk_id": 6,
            "beat_name": "Hard CTA",
            "recommended_duration_s": 5,
            "word_count": 18,
            "voiceover_clean_tts": "Comment HAIR below and I'll send you my complete salon-approved scalp detox protocol right away!",
            "visual_direction": "Rachel in her pure white silk blouse (no apron), smiling warmly and pointing downwards toward the comment area with both hands.",
            "composition_audit": {
                "camera_shot_type": "Vertical 9:16 medium close-up, eye level, 35mm lens",
                "foreground_props": "Clean luxury salon background with warm backlit ambiance",
                "left_subject": {
                    "name": "Rachel Bennett",
                    "character_id": "rachel_bennett_47yo",
                    "orientation": "Centered facing camera",
                    "pose": "Both hands pointing gracefully down toward bottom of the frame",
                    "hands_interaction": "Pointing down to prompt viewer engagement",
                    "gaze_direction": "Direct warm, welcoming eye contact",
                    "outfit": "Crisp white silk button-down blouse with sleeves neatly rolled to forearms, collar open, no apron"
                },
                "right_subject": None,
                "environment_background": "Luxury salon Bennett Studio interior, illuminated golden archway glowing softly behind her",
                "lighting_style": "Flattering warm beauty lighting, soft ambient golden halo around hair"
            },
            "midjourney_prompt_9_16": "Vertical 9:16 portrait of an elegant 47yo female expert with wavy bob and platinum highlights, wearing an upscale crisp white silk button-down blouse (no apron), smiling warmly and pointing downwards with both index fingers towards the bottom frame, luxury salon interior background with soft glowing golden archway, high fashion UGC aesthetic, 35mm f/2.0 --ar 9:16 --v 6.1 --style raw",
            "video_motion_prompt_i2v": "Rachel smiling warmly at camera, pointing downwards with both hands in an inviting gesture, natural head nod and cheerful expression, realistic lip sync and smooth movement, 4k master quality",
            "asset_tags": ["rachel_bennett", "cta", "white_silk_blouse", "no_apron", "manychat_keyword"],
            "continuity_notes": "Wardrobe change intentional: pure white silk blouse without apron for final high-converting CTA."
        }
    ],
    "post_copy": {
        "cover_headline": "COKE DETOX FOR THINNING HAIR?",
        "title": "The $2 Scalp Detox That Reverses Mineral Buildup & Follicle Suffocation",
        "caption": "Have you noticed your middle part widening or hair feeling weighed down no matter how much you wash it? 💆‍♀️✨\n\nHard water minerals and heavy product silicones create an invisible layer that literally suffocates your hair follicles. Before you drop $40 on another harsh chemical scrub, try this simple salon-tested scalp clarity reset!\n\n👇 Drop 'HAIR' below and I will send you my complete step-by-step Scalp Reset Protocol directly to your inbox!",
        "manychat_keyword": "HAIR",
        "hashtags": [
            "#HairLossHelp",
            "#ScalpHealth",
            "#HairGrowthJourney",
            "#BennettStudio",
            "#HairDetox",
            "#ThinningHairSolutions",
            "#SalonSecrets",
            "#HealthyHairTips"
        ]
    }
}

# Validate with Pydantic
pkg = ProductionPackage(**pkg_data)
print("ProductionPackage validation SUCCESSFUL!")

# Write JSON
json_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/02_Script_Prompts/production_package_PROD_011.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(pkg.dict(), f, indent=2, ensure_ascii=False)
print(f"Saved: {json_path}")

# Render Markdown
md_content = f"""# Production Package: {pkg.project_id}
**Reference:** `{pkg.reference_video}` ({pkg.reference_duration_s}s)  
**Topic:** {pkg.topic}  
**Brand:** {pkg.brand}  
**Avatar:** {pkg.avatar_name} ({pkg.avatar_age}yo, {pkg.avatar_archetype})  
**Wardrobe Assigned:** {pkg.wardrobe_assigned}  
**ManyChat Keyword:** `{pkg.post_copy.manychat_keyword}`  
**Cover Headline:** `{pkg.post_copy.cover_headline}`  

---

## Audio & Cadence Direction
{pkg.audio_voice_direction_anchor}

---

## Post Copy & Metadata
- **Cover Headline (Thumbnail Badge):** `{pkg.post_copy.cover_headline}`
- **Post Title:** {pkg.post_copy.title}
- **ManyChat Trigger:** `{pkg.post_copy.manychat_keyword}`
- **Caption:**
```text
{pkg.post_copy.caption}
```
- **Hashtags:** `{' '.join(pkg.post_copy.hashtags)}`

---

## 6-Chunk Production Prompts (70/30 Paraphrased)

"""

for chunk in pkg.chunks:
    md_content += f"""### Chunk {chunk.chunk_id}: {chunk.beat_name} ({chunk.recommended_duration_s}s | {chunk.word_count} words | ~{round(chunk.word_count/chunk.recommended_duration_s, 2)} WPS)
- **Voiceover TTS:**
> "{chunk.voiceover_clean_tts}"

- **Visual Direction:** {chunk.visual_direction}
- **Midjourney Image Prompt (9:16):**
```text
{chunk.midjourney_prompt_9_16}
```
- **Video Motion Prompt (I2V):**
```text
{chunk.video_motion_prompt_i2v}
```
- **Continuity Notes:** {chunk.continuity_notes}

---
"""

md_path = Path("Rachel Bennett - Botanique/04_IN_PRODUCTION/PROD_011_elainevanhausen_4/02_Script_Prompts/prompts_PROD_011.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved: {md_path}")
