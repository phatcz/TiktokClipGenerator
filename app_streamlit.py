"""
Creator Tool - Video Generation Pipeline
Professional UI for Film/Creator Studio workflow
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional

# Import Phase modules
from story_engine import generate_story
from phase2_generator import generate_phase2_output
from phase3_storyboard import build_storyboard_from_phase2
from phase4_video_plan import generate_video_plan
from phase5_segment_renderer import render_segments_from_video_plan
from phase5_assembler import assemble_video

# Page config
st.set_page_config(
    page_title="Creator Tool",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Creator Studio theme
st.markdown("""
<style>
    /* Main background - dark professional */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #16213e 100%);
    }
    
    /* Headings */
    .main-title {
        color: #64ffda;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .phase-title {
        color: #64ffda;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1rem 0;
        border-left: 4px solid #64ffda;
        padding-left: 1rem;
    }
    
    .section-title {
        color: #bb86fc;
        font-size: 1.3rem;
        font-weight: 500;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Cards */
    .film-card {
        background: rgba(30, 35, 45, 0.95);
        border: 1px solid rgba(100, 255, 218, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .film-card:hover {
        border-color: rgba(100, 255, 218, 0.6);
        box-shadow: 0 6px 30px rgba(100, 255, 218, 0.2);
    }
    
    .selected-card {
        border: 2px solid #64ffda;
        background: rgba(100, 255, 218, 0.05);
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.4);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #64ffda 0%, #bb86fc 100%);
        color: #0f1419;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(100, 255, 218, 0.4);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #64ffda;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #bb86fc;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .status-complete {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        border: 1px solid #00ff88;
    }
    
    .status-pending {
        background: rgba(255, 193, 7, 0.2);
        color: #ffc107;
        border: 1px solid #ffc107;
    }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(100, 255, 218, 0.5), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'phase1_story' not in st.session_state:
    st.session_state.phase1_story = None
if 'phase2_output' not in st.session_state:
    st.session_state.phase2_output = None
if 'phase3_storyboard' not in st.session_state:
    st.session_state.phase3_storyboard = None
if 'phase4_video_plan' not in st.session_state:
    st.session_state.phase4_video_plan = None
if 'phase5_render_result' not in st.session_state:
    st.session_state.phase5_render_result = None
if 'phase5_5_assemble_result' not in st.session_state:
    st.session_state.phase5_5_assemble_result = None
if 'selected_character_id' not in st.session_state:
    st.session_state.selected_character_id = 1
if 'selected_location_id' not in st.session_state:
    st.session_state.selected_location_id = 1
if 'selected_phase' not in st.session_state:
    st.session_state.selected_phase = "Phase 1: Story Input"

# ==================== Sidebar ====================
st.sidebar.markdown('<h1 style="color: #64ffda; font-size: 1.8rem; margin-bottom: 0;">🎬 CREATOR TOOL</h1>', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color: #888; font-size: 0.9rem; margin-top: 0;">Video Generation Studio</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Pipeline Navigation
st.sidebar.markdown('<h3 style="color: #bb86fc; font-size: 1rem;">📋 Production Pipeline</h3>', unsafe_allow_html=True)
phases = [
    "Phase 1: Story Input",
    "Phase 2: Cast & Locations",
    "Phase 3: Storyboard",
    "Phase 4: Video Plan",
    "Phase 5: Render Segments",
    "Phase 5.5: Assemble Video"
]
selected_phase = st.sidebar.radio("", phases, key="selected_phase", label_visibility="collapsed")

# Progress indicator
st.sidebar.markdown("---")
st.sidebar.markdown('<h3 style="color: #bb86fc; font-size: 1rem;">📊 Progress</h3>', unsafe_allow_html=True)
progress_items = [
    ("Story", st.session_state.phase1_story is not None),
    ("Cast & Locations", st.session_state.phase2_output is not None),
    ("Storyboard", st.session_state.phase3_storyboard is not None),
    ("Video Plan", st.session_state.phase4_video_plan is not None),
    ("Rendered", st.session_state.phase5_render_result is not None),
    ("Assembled", st.session_state.phase5_5_assemble_result is not None),
]
for name, completed in progress_items:
    status = "✓" if completed else "○"
    color = "#00ff88" if completed else "#666"
    st.sidebar.markdown(f'<p style="color: {color}; margin: 0.25rem 0;">{status} {name}</p>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown('<h3 style="color: #bb86fc; font-size: 1rem;">⚙️ Project Settings</h3>', unsafe_allow_html=True)

# Input Parameters
goal = st.sidebar.text_input("🎯 Goal", value="ขายคอร์สออนไลน์", help="What is the goal of this video?")
product = st.sidebar.text_input("📦 Product", value="AI Creator Tool", help="Product or service name")
audience = st.sidebar.text_input("👥 Target Audience", value="มือใหม่ ไม่เก่งเทค", help="Who is this video for?")
platform = st.sidebar.selectbox("📱 Platform", ["Facebook Reel", "TikTok", "Instagram Reel", "YouTube Shorts"], index=0, help="Target platform")
num_characters = st.sidebar.number_input("Character Candidates", min_value=1, max_value=10, value=4, help="Number of character options to generate")
num_locations = st.sidebar.number_input("Location Candidates", min_value=1, max_value=10, value=4, help="Number of location options to generate")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Reset Project", use_container_width=True, help="Clear all progress and start fresh"):
    for key in ['phase1_story', 'phase2_output', 'phase3_storyboard', 'phase4_video_plan', 'phase5_render_result', 'phase5_5_assemble_result']:
        st.session_state[key] = None
    st.rerun()

# ==================== Main Area ====================
st.markdown('<h1 class="main-title">CREATOR TOOL</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #888; font-size: 1.1rem; margin-bottom: 2rem;">Professional Video Generation Pipeline</p>', unsafe_allow_html=True)

# ==================== Phase 1: Story Input ====================
if "Phase 1" in selected_phase:
    st.markdown('<h2 class="phase-title">📝 PROJECT CONCEPT</h2>', unsafe_allow_html=True)
    st.markdown("**Define your story concept. This will be the foundation of your video.**")
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate Story Concept", type="primary", use_container_width=True):
            with st.spinner("Creating your story concept..."):
                try:
                    story = generate_story(goal, product, audience, platform)
                    st.session_state.phase1_story = story
                    st.success("✓ Story concept generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display story
    if st.session_state.phase1_story:
        story = st.session_state.phase1_story
        st.markdown("---")
        
        # Film concept card
        st.markdown('<div class="film-card">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">🎬 THE FILM</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            **Goal:** {story.get('goal', '')}  
            **Product:** {story.get('product', '')}  
            **Audience:** {story.get('audience', '')}  
            **Platform:** {story.get('platform', '')}
            """)
        with col2:
            st.metric("Scenes", len(story.get("scenes", [])))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Plot structure
        st.markdown('<h3 class="section-title">📖 PLOT STRUCTURE</h3>', unsafe_allow_html=True)
        st.markdown("Your story is divided into four acts:")
        
        scenes = story.get("scenes", [])
        scene_info = [
            ("Hook", "Grab attention", "#64ffda"),
            ("Conflict", "Present challenge", "#bb86fc"),
            ("Reveal", "Show solution", "#ff6b9d"),
            ("Close", "Call to action", "#ffc107")
        ]
        
        for i, scene in enumerate(scenes):
            if i < len(scene_info):
                label, desc, color = scene_info[i]
                scene_purpose = scene.get('purpose', '').upper()
                
                st.markdown(f'<div class="film-card" style="border-left: 4px solid {color};">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f'<h4 style="color: {color}; margin: 0;">{label}</h4>', unsafe_allow_html=True)
                    st.markdown(f"*{desc}*")
                    st.markdown(f"**Emotion:** {scene.get('emotion', '')}")  
                    st.markdown(f"**Duration:** {scene.get('duration', 0)}s")
                with col2:
                    st.markdown(f"**Scene Description:**")
                    st.markdown(scene.get('description', ''))
                st.markdown('</div>', unsafe_allow_html=True)
        
        # JSON output
        with st.expander("📄 View Raw JSON Data"):
            st.json(story)

# ==================== Phase 2: Cast & Locations ====================
elif "Phase 2" in selected_phase:
    st.markdown('<h2 class="phase-title">👥 CAST & LOCATIONS</h2>', unsafe_allow_html=True)
    st.markdown("**Select your cast members and shooting locations.**")
    
    if not st.session_state.get("phase1_story"):
        st.warning("⚠️ Please complete **Phase 1: Story Input** first to generate cast and location options.")
        st.button("Generate Cast & Locations", disabled=True, use_container_width=True)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Generate Cast & Locations", type="primary", use_container_width=True):
                with st.spinner("Generating cast and location options..."):
                    try:
                        phase2_output = generate_phase2_output(
                            st.session_state.phase1_story,
                            num_characters=num_characters,
                            num_locations=num_locations
                        )
                        st.session_state.phase2_output = phase2_output
                        st.success("✓ Cast and locations generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.phase2_output:
            phase2 = st.session_state.phase2_output
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            # CAST
            with col1:
                st.markdown('<h3 class="section-title">🎭 CAST</h3>', unsafe_allow_html=True)
                st.markdown("Select your main character:")
                
                characters = phase2.get("characters", [])
                if characters:
                    # Selection dropdown
                    char_options = {f"{char.get('id')}: {char.get('name', '')}": char.get('id') for char in characters}
                    selected_char_key = st.selectbox(
                        "Choose Character",
                        options=list(char_options.keys()),
                        index=st.session_state.selected_character_id - 1 if st.session_state.selected_character_id <= len(characters) else 0,
                        key="char_select",
                        label_visibility="collapsed"
                    )
                    st.session_state.selected_character_id = char_options[selected_char_key]
                    
                    # Character cards
                    for char in characters:
                        is_selected = char.get('id') == st.session_state.selected_character_id
                        card_class = "film-card selected-card" if is_selected else "film-card"
                        
                        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                        col_img, col_info = st.columns([1, 2])
                        
                        with col_img:
                            image_url = char.get('image_url', '')
                            if image_url:
                                try:
                                    st.image(image_url, width=180, use_container_width=False)
                                except:
                                    st.image("https://via.placeholder.com/180x240/64ffda/0f1419?text=Character", width=180)
                            else:
                                st.image("https://via.placeholder.com/180x240/64ffda/0f1419?text=Character", width=180)
                        
                        with col_info:
                            st.markdown(f"### {char.get('name', '')}")
                            if is_selected:
                                st.markdown('<span class="status-badge status-complete">SELECTED</span>', unsafe_allow_html=True)
                            st.markdown(f"**Style:** {char.get('style', '')}")  
                            st.markdown(f"**Age:** {char.get('age_range', '')}")  
                            st.markdown(f"**Personality:** {char.get('personality', '')}")  
                            st.markdown(f"*{char.get('description', '')}*")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # LOCATIONS
            with col2:
                st.markdown('<h3 class="section-title">📍 LOCATIONS</h3>', unsafe_allow_html=True)
                st.markdown("Select your shooting location:")
                
                locations = phase2.get("locations", [])
                if locations:
                    # Selection dropdown
                    loc_options = {f"{loc.get('id')}: {loc.get('name', '')}": loc.get('id') for loc in locations}
                    selected_loc_key = st.selectbox(
                        "Choose Location",
                        options=list(loc_options.keys()),
                        index=st.session_state.selected_location_id - 1 if st.session_state.selected_location_id <= len(locations) else 0,
                        key="loc_select",
                        label_visibility="collapsed"
                    )
                    st.session_state.selected_location_id = loc_options[selected_loc_key]
                    
                    # Location cards
                    for loc in locations:
                        is_selected = loc.get('id') == st.session_state.selected_location_id
                        card_class = "film-card selected-card" if is_selected else "film-card"
                        
                        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                        col_img, col_info = st.columns([1, 2])
                        
                        with col_img:
                            image_url = loc.get('image_url', '')
                            if image_url:
                                try:
                                    st.image(image_url, width=180, use_container_width=False)
                                except:
                                    st.image("https://via.placeholder.com/180x240/bb86fc/0f1419?text=Location", width=180)
                            else:
                                st.image("https://via.placeholder.com/180x240/bb86fc/0f1419?text=Location", width=180)
                        
                        with col_info:
                            st.markdown(f"### {loc.get('name', '')}")
                            if is_selected:
                                st.markdown('<span class="status-badge status-complete">SELECTED</span>', unsafe_allow_html=True)
                            st.markdown(f"**Style:** {loc.get('style', '')}")  
                            st.markdown(f"**Mood:** {loc.get('mood', '')}")  
                            st.markdown(f"*{loc.get('description', '')}*")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # JSON output
            with st.expander("📄 View Raw JSON Data"):
                st.json(phase2)

# ==================== Phase 3: Storyboard ====================
elif "Phase 3" in selected_phase:
    st.markdown('<h2 class="phase-title">🎨 STORYBOARD</h2>', unsafe_allow_html=True)
    st.markdown("**Visual storyboard showing key moments from your story.**")
    
    if not st.session_state.get("phase2_output"):
        st.warning("⚠️ Please complete **Phase 2: Cast & Locations** first to build the storyboard.")
        st.button("Build Storyboard", disabled=True, use_container_width=True)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎨 Build Storyboard", type="primary", use_container_width=True):
                with st.spinner("Building visual storyboard..."):
                    try:
                        storyboard = build_storyboard_from_phase2(
                            st.session_state.phase2_output,
                            selected_character_id=st.session_state.selected_character_id,
                            selected_location_id=st.session_state.selected_location_id
                        )
                        st.session_state.phase3_storyboard = storyboard
                        st.success("✓ Storyboard created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.phase3_storyboard:
            storyboard = st.session_state.phase3_storyboard
            st.markdown("---")
            
            # Summary
            scenes = storyboard.get("scenes", [])
            total_keyframes = sum(len(scene.get('keyframes', [])) for scene in scenes)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Scenes", len(scenes))
            with col2:
                st.metric("Total Keyframes", total_keyframes)
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">📸 STORYBOARD FRAMES</h3>', unsafe_allow_html=True)
            
            # Scenes
            for scene_idx, scene in enumerate(scenes):
                scene_id = scene.get("scene_id")
                keyframes = scene.get("keyframes", [])
                
                st.markdown(f'<div class="film-card">', unsafe_allow_html=True)
                st.markdown(f"### 🎬 Scene {scene_id}")
                
                # Keyframe grid
                if keyframes:
                    cols = st.columns(min(len(keyframes), 4))
                    for idx, kf in enumerate(keyframes):
                        with cols[idx % len(cols)]:
                            st.image("https://via.placeholder.com/200x150/64ffda/0f1419?text=Frame", 
                                    caption=f"Frame {kf.get('id', '')} • {kf.get('timing', 0)}s", width=200)
                            st.markdown(f"*{kf.get('description', '')[:60]}...*")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # JSON output
            with st.expander("📄 View Raw JSON Data"):
                st.json(storyboard)

# ==================== Phase 4: Video Plan ====================
elif "Phase 4" in selected_phase:
    st.markdown('<h2 class="phase-title">📋 PRODUCTION PLAN</h2>', unsafe_allow_html=True)
    st.markdown("**Video production timeline with segment breakdown.**")
    
    if not st.session_state.get("phase3_storyboard"):
        st.warning("⚠️ Please complete **Phase 3: Storyboard** first to create the production plan.")
        st.button("Generate Video Plan", disabled=True, use_container_width=True)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📋 Generate Production Plan", type="primary", use_container_width=True):
                with st.spinner("Creating production plan..."):
                    try:
                        video_plan = generate_video_plan(st.session_state.phase3_storyboard)
                        st.session_state.phase4_video_plan = video_plan
                        st.success("✓ Production plan ready!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.phase4_video_plan:
            video_plan = st.session_state.phase4_video_plan
            st.markdown("---")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Segments", video_plan.get("segment_count", 0))
            with col2:
                st.metric("Total Duration", f"{video_plan.get('total_duration', 0):.1f}s")
            with col3:
                segments = video_plan.get("segments", [])
                st.metric("Ready to Render", len(segments))
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">⏱️ PRODUCTION TIMELINE</h3>', unsafe_allow_html=True)
            
            # Segments
            segments = video_plan.get("segments", [])
            for seg_idx, seg in enumerate(segments):
                st.markdown(f'<div class="film-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"### Segment {seg.get('id')}")
                    st.markdown(f"**Duration:** {seg.get('duration', 0)}s")
                
                with col2:
                    col_start, col_end = st.columns(2)
                    with col_start:
                        st.markdown("**START**")
                        start_kf = seg.get("start_keyframe", {})
                        st.markdown(f"Frame: {start_kf.get('id', '')} @ {start_kf.get('timing', 0)}s")
                        st.caption(start_kf.get('description', '')[:80])
                    
                    with col_end:
                        st.markdown("**END**")
                        end_kf = seg.get("end_keyframe", {})
                        st.markdown(f"Frame: {end_kf.get('id', '')} @ {end_kf.get('timing', 0)}s")
                        st.caption(end_kf.get('description', '')[:80])
                    
                    directive = seg.get('directive', '')
                    if directive:
                        st.info(f"**Directive:** {directive}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # JSON output
            with st.expander("📄 View Raw JSON Data"):
                st.json(video_plan)

# ==================== Phase 5: Render Segments ====================
elif "Phase 5" in selected_phase:
    st.markdown('<h2 class="phase-title">🎬 RENDER SEGMENTS</h2>', unsafe_allow_html=True)
    st.markdown("**Render individual video segments. Each segment will be generated separately.**")
    
    if not st.session_state.get("phase4_video_plan"):
        st.warning("⚠️ Please complete **Phase 4: Video Plan** first.")
        st.button("Render Segments", disabled=True, use_container_width=True)
    elif not st.session_state.get("phase1_story"):
        st.warning("⚠️ Story context is required for rendering.")
        st.button("Render Segments", disabled=True, use_container_width=True)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎬 Render All Segments", type="primary", use_container_width=True):
                with st.spinner("Rendering video segments... This may take a while."):
                    try:
                        render_result = render_segments_from_video_plan(
                            st.session_state.phase4_video_plan,
                            story_context=st.session_state.phase1_story
                        )
                        st.session_state.phase5_render_result = render_result
                        st.success("✓ All segments rendered!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.phase5_render_result:
            render_result = st.session_state.phase5_render_result
            st.markdown("---")
            
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Segments", render_result.get("total_segments", 0))
            with col2:
                st.metric("Successful", render_result.get("successful_segments", 0))
            with col3:
                failed = render_result.get("failed_segments", [])
                st.metric("Failed", len(failed) if failed else 0)
            
            st.markdown("---")
            st.markdown('<h3 class="section-title">🎥 RENDERED FOOTAGE</h3>', unsafe_allow_html=True)
            
            # Segment results
            rendered_segs = render_result.get("rendered_segments", [])
            for seg in rendered_segs:
                is_success = seg.get("success", False)
                status_color = "#00ff88" if is_success else "#ff6b6b"
                status_text = "✓ READY" if is_success else "✗ FAILED"
                
                st.markdown(f'<div class="film-card" style="border-left: 4px solid {status_color};">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"### Segment {seg.get('segment_id')}")
                    st.markdown(f'<span class="status-badge" style="background: rgba(0,255,136,0.2); color: {status_color}; border-color: {status_color};">{status_text}</span>', unsafe_allow_html=True)
                
                with col2:
                    if is_success:
                        st.markdown(f"**Video File:** `{seg.get('video_path', '')}`")
                        st.markdown(f"**Duration:** {seg.get('duration', 0)}s")
                        st.video("https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4")
                    else:
                        st.error(f"**Error:** {seg.get('error', 'Unknown error')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # JSON output
            with st.expander("📄 View Raw JSON Data"):
                st.json(render_result)

# ==================== Phase 5.5: Assemble Video ====================
elif "Phase 5.5" in selected_phase:
    st.markdown('<h2 class="phase-title">🎞️ FINAL ASSEMBLY</h2>', unsafe_allow_html=True)
    st.markdown("**Assemble all segments into the final video.**")
    
    if not st.session_state.get("phase5_render_result"):
        st.warning("⚠️ Please complete **Phase 5: Render Segments** first.")
        st.button("Assemble Final Video", disabled=True, use_container_width=True)
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔗 Assemble Final Video", type="primary", use_container_width=True):
                with st.spinner("Assembling final video..."):
                    try:
                        segment_paths = []
                        for rendered_seg in st.session_state.phase5_render_result.get("rendered_segments", []):
                            if rendered_seg.get("success"):
                                segment_paths.append(rendered_seg.get("video_path"))
                        
                        if segment_paths:
                            assemble_result = assemble_video(
                                segment_paths,
                                output_path=None,
                                retry_failed=False
                            )
                            st.session_state.phase5_5_assemble_result = assemble_result
                            st.success("✓ Final video assembled!")
                            st.rerun()
                        else:
                            st.error("No successful segments to assemble")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if st.session_state.phase5_5_assemble_result:
            assemble_result = st.session_state.phase5_5_assemble_result
            st.markdown("---")
            
            if assemble_result.get("success"):
                st.markdown('<div class="film-card" style="border: 3px solid #00ff88; background: rgba(0,255,136,0.1);">', unsafe_allow_html=True)
                st.markdown('<h1 style="color: #00ff88; text-align: center; margin: 1rem 0;">🎉 FILM COMPLETE</h1>', unsafe_allow_html=True)
                st.markdown(f'<p style="text-align: center; font-size: 1.2rem; color: #64ffda;">**Output:** `{assemble_result.get("output_path", "")}`</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Summary
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Segments", assemble_result.get("total_segments", 0))
                with col2:
                    st.metric("Successful", assemble_result.get("successful_segments", 0))
                with col3:
                    st.metric("Failed", len(assemble_result.get("failed_segments", [])))
                with col4:
                    st.metric("Retries", assemble_result.get("retry_count", 0))
                
                st.markdown("---")
                st.markdown('<h3 class="section-title">🎬 FINAL VIDEO PREVIEW</h3>', unsafe_allow_html=True)
                st.video("https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4")
            else:
                st.error("❌ Assembly failed")
                st.write(f"Failed segments: {assemble_result.get('failed_segments', [])}")
            
            # JSON output
            with st.expander("📄 View Raw JSON Data"):
                st.json(assemble_result)

# Footer
st.markdown("---")
st.markdown('<p style="text-align: center; color: #666; font-size: 0.9rem;">Creator Tool MVP v0.1 | Professional Video Generation Pipeline</p>', unsafe_allow_html=True)
