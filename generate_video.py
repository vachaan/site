import os
import math
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import imageio_ffmpeg

# ==============================================================================
# 1. SETUP & CONFIGURATION
# ==============================================================================
WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION_SEC = 24
TOTAL_FRAMES = FPS * DURATION_SEC

COLOR_OBSIDIAN = (17, 17, 17)
COLOR_CHARCOAL = (41, 41, 41)
COLOR_WHITE    = (255, 255, 255)
COLOR_IVORY    = (243, 243, 241)
COLOR_GREY     = (119, 119, 119)
COLOR_LIGHT_GREY = (180, 180, 180)
COLOR_BORDER_DARK = (46, 46, 46)

# Fonts
font_georgia_xl = ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', 72)
font_georgia_lg = ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', 52)
font_georgia_md = ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', 38)
font_georgia_sm = ImageFont.truetype('C:/Windows/Fonts/georgia.ttf', 28)

font_nirmala_xl = ImageFont.truetype('C:/Windows/Fonts/Nirmala.ttf', 56)
font_nirmala_lg = ImageFont.truetype('C:/Windows/Fonts/Nirmala.ttf', 44)

font_manrope_lg = ImageFont.truetype('assets/fonts/Manrope-Bold.ttf', 36)
font_manrope_md = ImageFont.truetype('assets/fonts/Manrope-Bold.ttf', 26)
font_manrope_sm = ImageFont.truetype('assets/fonts/Manrope-Bold.ttf', 18)
font_manrope_xs = ImageFont.truetype('assets/fonts/Manrope-Bold.ttf', 15)

# Load brand assets
emblem_img = Image.open('assets/images/vachaan-emblem-white.png').convert('RGBA')
founder_img = Image.open('assets/images/founder-krishna.jpg').convert('RGBA')
verse_hindi_img = Image.open('assets/video/verse_hindi_perfect.png').convert('RGBA')

# Prepare founder cropped portrait
crop_w, crop_h = 420, 520
# center-crop founder
fw, fh = founder_img.size
target_aspect = crop_w / crop_h
if fw / fh > target_aspect:
    new_w = int(fh * target_aspect)
    x0 = (fw - new_w) // 2
    founder_cropped = founder_img.crop((x0, 0, x0 + new_w, fh))
else:
    new_h = int(fw / target_aspect)
    y0 = (fh - new_h) // 3
    founder_cropped = founder_img.crop((0, y0, fw, y0 + new_h))
founder_cropped = founder_cropped.resize((crop_w, crop_h), Image.Resampling.LANCZOS)

# Create rounded mask for founder portrait
mask = Image.new('L', (crop_w, crop_h), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([0, 0, crop_w, crop_h], radius=16, fill=255)
founder_rounded = Image.new('RGBA', (crop_w, crop_h), (0, 0, 0, 0))
founder_rounded.paste(founder_cropped, (0, 0), mask=mask)

# ==============================================================================
# 2. HELPER DRAWING FUNCTIONS
# ==============================================================================
def draw_text_centered(draw, text, y, font, fill):
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    x = (WIDTH - text_w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return text_w

def draw_text_tracking(draw, text, y, font, fill, tracking=8):
    # draw text with custom character tracking
    total_w = sum(font.getbbox(c)[2] - font.getbbox(c)[0] + tracking for c in text) - tracking
    x = (WIDTH - total_w) // 2
    for c in text:
        draw.text((x, y), c, font=font, fill=fill)
        x += (font.getbbox(c)[2] - font.getbbox(c)[0]) + tracking

def ease_in_out(t):
    return t * t * (3 - 2 * t)

# ==============================================================================
# 3. SCENE RENDERING
# ==============================================================================
def render_frame(frame_idx):
    time_sec = frame_idx / FPS
    img = Image.new('RGB', (WIDTH, HEIGHT), COLOR_OBSIDIAN)
    draw = ImageDraw.Draw(img)

    # --------------------------------------------------------------------------
    # SCENE 1: Brand Unveiling (0.0s - 4.8s)
    # --------------------------------------------------------------------------
    if time_sec < 5.0:
        t = time_sec / 4.8
        alpha = min(1.0, time_sec / 0.8)
        if time_sec > 4.2:
            alpha = max(0.0, (4.8 - time_sec) / 0.6)

        # Scale emblem slightly from 90% to 100%
        scale = 0.26 + 0.02 * ease_in_out(min(1.0, time_sec / 4.0))
        ew = int(emblem_img.width * scale)
        eh = int(emblem_img.height * scale)
        resized_emblem = emblem_img.resize((ew, eh), Image.Resampling.LANCZOS)

        # Apply alpha to emblem
        if alpha < 1.0:
            r, g, b, a = resized_emblem.split()
            a = a.point(lambda p: int(p * alpha))
            resized_emblem = Image.merge('RGBA', (r, g, b, a))

        emblem_y = 230 - int(15 * (1 - ease_in_out(min(1.0, time_sec / 1.5))))
        img.paste(resized_emblem, ((WIDTH - ew) // 2, emblem_y), resized_emblem)

        # Eyebrow
        if time_sec > 0.4:
            c = int(180 * alpha)
            draw_text_tracking(draw, "OFFICIAL BRAND PRESENTATION", emblem_y + eh + 40, font_manrope_xs, (c, c, c), tracking=6)

        # Brand Title
        if time_sec > 0.8:
            title_alpha = min(1.0, (time_sec - 0.8) / 0.8) * alpha
            c = int(255 * title_alpha)
            draw_text_tracking(draw, "VACHAAN.", emblem_y + eh + 75, font_georgia_xl, (c, c, c), tracking=12)

        # Hairline divider
        if time_sec > 1.2:
            line_progress = min(1.0, (time_sec - 1.2) / 0.8)
            line_w = int(280 * ease_in_out(line_progress))
            c = int(200 * alpha)
            draw.line([(WIDTH // 2 - line_w // 2, emblem_y + eh + 185), (WIDTH // 2 + line_w // 2, emblem_y + eh + 185)], fill=(c, c, c), width=2)

        # Tagline
        if time_sec > 1.5:
            tag_alpha = min(1.0, (time_sec - 1.5) / 0.8) * alpha
            c = int(220 * tag_alpha)
            draw_text_tracking(draw, "YOUR VISION. OUR COMMITMENT.", emblem_y + eh + 215, font_manrope_md, (c, c, c), tracking=6)

        if time_sec > 2.0:
            sub_alpha = min(1.0, (time_sec - 2.0) / 0.8) * alpha
            c = int(140 * sub_alpha)
            draw_text_tracking(draw, "WE PROMISE. WE DELIVER.", emblem_y + eh + 270, font_manrope_sm, (c, c, c), tracking=4)

    # --------------------------------------------------------------------------
    # SCENE 2: Foundational Ethos (Sanskrit Verse) (4.8s - 9.8s)
    # --------------------------------------------------------------------------
    elif time_sec < 10.0:
        local_t = time_sec - 4.8
        alpha = min(1.0, local_t / 0.8)
        if time_sec > 9.2:
            alpha = max(0.0, (9.8 - time_sec) / 0.6)

        # Background card
        card_w, card_h = 1600, 720
        cx, cy = (WIDTH - card_w) // 2, (HEIGHT - card_h) // 2
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill=COLOR_CHARCOAL, outline=(55, 55, 55), width=1)

        # Eyebrow tag
        c = int(160 * alpha)
        draw_text_tracking(draw, "[ FOUNDATIONAL ETHOS ]", cy + 85, font_manrope_sm, (c, c, c), tracking=6)

        # Sanskrit Verse (DirectWrite rendered Devanagari)
        if local_t > 0.4:
            v_alpha = min(1.0, (local_t - 0.4) / 0.8) * alpha
            vw, vh = verse_hindi_img.size
            vx = (WIDTH - vw) // 2
            vy = cy + 155
            v_frame = verse_hindi_img.copy()
            if v_alpha < 1.0:
                vr, vg, vb, va = v_frame.split()
                va = va.point(lambda p: int(p * v_alpha))
                v_frame = Image.merge('RGBA', (vr, vg, vb, va))
            img.paste(v_frame, (vx, vy), v_frame)

        # Divider
        if local_t > 0.9:
            line_w = int(120 * ease_in_out(min(1.0, (local_t - 0.9) / 0.6)))
            c = int(220 * alpha)
            draw.line([(WIDTH // 2 - line_w // 2, cy + 270), (WIDTH // 2 + line_w // 2, cy + 270)], fill=(c, c, c), width=2)

        # English Translation
        if local_t > 1.3:
            t_alpha = min(1.0, (local_t - 1.3) / 0.8) * alpha
            c = int(230 * t_alpha)
            draw_text_centered(draw, "“The tradition of the Raghus has forever prevailed:", cy + 320, font_georgia_md, (c, c, c))
            draw_text_centered(draw, "life may depart, but a pledged word (VACHAAN) shall never be broken.”", cy + 380, font_georgia_md, (c, c, c))

        # Brand Meaning Subtitle
        if local_t > 1.8:
            m_alpha = min(1.0, (local_t - 1.8) / 0.8) * alpha
            c = int(170 * m_alpha)
            draw_text_tracking(draw, "A PROMISE IS ONLY VALUABLE WHEN IT IS FULFILLED.", cy + 490, font_manrope_sm, (c, c, c), tracking=4)

            # 3 Pillars
            c_sub = int(130 * m_alpha)
            draw_text_centered(draw, "Trust  •  Responsibility  •  Dedication", cy + 540, font_manrope_xs, (c_sub, c_sub, c_sub))

    # --------------------------------------------------------------------------
    # SCENE 3: Purpose & The 3 Offerings (9.8s - 15.0s)
    # --------------------------------------------------------------------------
    elif time_sec < 15.2:
        local_t = time_sec - 9.8
        alpha = min(1.0, local_t / 0.8)
        if time_sec > 14.6:
            alpha = max(0.0, (15.2 - time_sec) / 0.6)

        # Soft Ivory / Pure White Editorial Shift
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=COLOR_IVORY)

        # Eyebrow
        c_grey = int(119 * alpha)
        draw_text_tracking(draw, "SERVICES & ACCESSIBILITY", 110, font_manrope_xs, (c_grey, c_grey, c_grey), tracking=6)

        # Headline
        c_obs = int(17 * alpha)
        draw_text_centered(draw, "Digital Excellence Made Accessible.", 155, font_georgia_lg, (c_obs, c_obs, c_obs))

        c_char = int(60 * alpha)
        draw_text_centered(draw, "Professional digital solutions tailored for small businesses, students, and professionals.", 235, font_manrope_sm, (c_char, c_char, c_char))

        # 3 Structured Service Cards
        cards_data = [
            ("01", "Small Business Websites", "Clean, high-performance static web\narchitecture built for credibility\nand customer enquiries.", "Starts from ₹500"),
            ("02", "Student Career Portfolios", "Editorial portfolio websites, ATS-ready\nresumes, and LinkedIn branding for\naspiring graduates.", "Starts from ₹200"),
            ("03", "Career Profile Guidance", "1-on-1 strategic portfolio review,\nLinkedIn profile audit, and career\nconsultation with Krishna.", "₹100 for 3 Hours")
        ]

        card_w = 480
        card_h = 490
        gap = 50
        start_x = (WIDTH - (3 * card_w + 2 * gap)) // 2
        card_y = 310

        for i, (num, title, desc, price) in enumerate(cards_data):
            if local_t > 0.4 + i * 0.3:
                card_alpha = min(1.0, (local_t - (0.4 + i * 0.3)) / 0.6) * alpha
                cx = start_x + i * (card_w + gap)
                
                # Card Background & Border
                draw.rounded_rectangle([cx, card_y, cx + card_w, card_y + card_h], radius=12, fill=COLOR_WHITE, outline=(220, 220, 216), width=1)

                # Number
                c_num = int(150 * card_alpha)
                draw.text((cx + 40, card_y + 35), num, font=font_georgia_md, fill=(c_num, c_num, c_num))

                # Title
                c_title = int(17 * card_alpha)
                draw.text((cx + 40, card_y + 90), title, font=font_georgia_sm, fill=(c_title, c_title, c_title))

                # Divider
                draw.line([(cx + 40, card_y + 145), (cx + card_w - 40, card_y + 145)], fill=(230, 230, 225), width=1)

                # Description lines
                c_desc = int(70 * card_alpha)
                dy = card_y + 175
                for line in desc.split('\n'):
                    draw.text((cx + 40, dy), line, font=font_manrope_xs, fill=(c_desc, c_desc, c_desc))
                    dy += 32

                # Price Tag
                draw.line([(cx + 40, card_y + 390), (cx + card_w - 40, card_y + 390)], fill=(230, 230, 225), width=1)
                c_price = int(17 * card_alpha)
                draw.text((cx + 40, card_y + 420), price, font=font_manrope_md, fill=(c_price, c_price, c_price))

        # Bottom value statement
        if local_t > 1.8:
            c_tag = int(120 * alpha)
            draw_text_tracking(draw, "TRANSPARENCY  •  AFFORDABILITY  •  RELIABLE DELIVERY", 870, font_manrope_xs, (c_tag, c_tag, c_tag), tracking=5)

    # --------------------------------------------------------------------------
    # SCENE 4: Leadership & Founder (15.2s - 19.5s)
    # --------------------------------------------------------------------------
    elif time_sec < 19.6:
        local_t = time_sec - 15.2
        alpha = min(1.0, local_t / 0.8)
        if time_sec > 19.0:
            alpha = max(0.0, (19.6 - time_sec) / 0.6)

        # Split layout: Left Founder Photo, Right Founder Quote & Ethos
        # Left Photo
        px = 240
        py = (HEIGHT - crop_h) // 2
        
        # Frame photo with subtle white border
        draw.rounded_rectangle([px - 4, py - 4, px + crop_w + 4, py + crop_h + 4], radius=20, outline=(70, 70, 70), width=2)
        
        # Paste rounded founder photo
        if alpha < 1.0:
            f_frame = founder_rounded.copy()
            r, g, b, a = f_frame.split()
            a = a.point(lambda p: int(p * alpha))
            f_frame = Image.merge('RGBA', (r, g, b, a))
            img.paste(f_frame, (px, py), f_frame)
        else:
            img.paste(founder_rounded, (px, py), founder_rounded)

        # Right Column
        rx = px + crop_w + 90
        ry = py + 30

        # Eyebrow
        c_grey = int(150 * alpha)
        draw.text((rx, ry), "[ LEADERSHIP & PLEDGE ]", font=font_manrope_xs, fill=(c_grey, c_grey, c_grey))

        # Headline
        c_white = int(255 * alpha)
        draw.text((rx, ry + 40), "Built with Purpose.\nLed by Sincerity.", font=font_georgia_lg, fill=(c_white, c_white, c_white))

        # Quote
        if local_t > 0.5:
            q_alpha = min(1.0, (local_t - 0.5) / 0.8) * alpha
            c_quote = int(220 * q_alpha)
            quotes_lines = [
                "“Founded with the belief that meaningful digital solutions",
                "should be accessible to everyone, VACHAAN represents",
                "a commitment to turning ideas into practical outcomes",
                "through responsible work and honest communication.”"
            ]
            qy = ry + 195
            for ql in quotes_lines:
                draw.text((rx, qy), ql, font=font_georgia_sm, fill=(c_quote, c_quote, c_quote))
                qy += 44

        # Founder Signature & Credits
        if local_t > 1.2:
            s_alpha = min(1.0, (local_t - 1.2) / 0.8) * alpha
            c_name = int(255 * s_alpha)
            draw.text((rx, ry + 405), "Krishna Singh Raghuvanshi", font=font_manrope_md, fill=(c_name, c_name, c_name))
            
            c_role = int(160 * s_alpha)
            draw.text((rx, ry + 450), "Founder, VACHAAN  •  krishnasinghh.in", font=font_manrope_sm, fill=(c_role, c_role, c_role))

    # --------------------------------------------------------------------------
    # SCENE 5: The Grand Launch Announcement (19.6s - 24.0s)
    # --------------------------------------------------------------------------
    else:
        local_t = time_sec - 19.6
        alpha = min(1.0, local_t / 0.8)
        if time_sec > 23.2:
            alpha = max(0.0, (24.0 - time_sec) / 0.8)

        # Pulse animation for live dot
        pulse = 0.5 + 0.5 * math.sin(local_t * math.pi * 3)

        # Top Emblem
        scale = 0.18
        ew = int(emblem_img.width * scale)
        eh = int(emblem_img.height * scale)
        resized_emblem = emblem_img.resize((ew, eh), Image.Resampling.LANCZOS)
        if alpha < 1.0:
            r, g, b, a = resized_emblem.split()
            a = a.point(lambda p: int(p * alpha))
            resized_emblem = Image.merge('RGBA', (r, g, b, a))
        img.paste(resized_emblem, ((WIDTH - ew) // 2, 130), resized_emblem)

        # Eyebrow Pill
        c_grey = int(180 * alpha)
        draw_text_tracking(draw, "OFFICIAL LAUNCH ANNOUNCEMENT", 290, font_manrope_xs, (c_grey, c_grey, c_grey), tracking=6)

        # Main Title
        c_white = int(255 * alpha)
        draw_text_centered(draw, "OUR OFFICIAL WEBSITE GOES LIVE", 335, font_georgia_lg, (c_white, c_white, c_white))

        # Architectural Date Card
        bw, bh = 940, 220
        bx = (WIDTH - bw) // 2
        by = 445
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=COLOR_CHARCOAL, outline=(60, 60, 60), width=1)

        # Date Inside Card
        c_date = int(255 * alpha)
        draw_text_centered(draw, "25 NOVEMBER 2026", by + 40, font_georgia_xl, (c_date, c_date, c_date))

        # Time Inside Card
        c_time = int(220 * alpha)
        draw_text_tracking(draw, "12:00 PM (NOON) IST", by + 135, font_manrope_lg, (c_time, c_time, c_time), tracking=4)

        # Pulsing Live Dot inside Box
        dot_r = 7
        dot_x = bx + bw - 45
        dot_y = by + 40
        dot_alpha = int(255 * pulse * alpha)
        draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=(dot_alpha, dot_alpha, dot_alpha))

        # Tagline & Website
        if local_t > 0.8:
            c_url = int(240 * alpha)
            draw_text_tracking(draw, "vachaan.co", 730, font_manrope_md, (c_url, c_url, c_url), tracking=6)

            c_tag = int(150 * alpha)
            draw_text_tracking(draw, "YOUR VISION. OUR COMMITMENT.", 790, font_manrope_xs, (c_tag, c_tag, c_tag), tracking=6)

            c_mot = int(120 * alpha)
            draw_text_centered(draw, "We Promise. We Deliver.", 840, font_georgia_sm, (c_mot, c_mot, c_mot))

    return np.array(img)

# ==============================================================================
# 4. SOUNDTRACK SYNTHESIS
# ==============================================================================
def generate_soundtrack(output_wav):
    sample_rate = 44100
    total_samples = sample_rate * DURATION_SEC
    t = np.linspace(0, DURATION_SEC, total_samples, False)

    # Base ambient drone (Chords in D minor: D2, A2, D3, F3, A3)
    drone_freqs = [73.42, 110.0, 146.83, 174.61, 220.0]
    ambient = np.zeros(total_samples)

    for i, f in enumerate(drone_freqs):
        detune = 1.0 + (i * 0.0015)
        phase = i * 0.4
        weight = 0.25 / (1 + i * 0.3)
        ambient += np.sin(2 * np.pi * f * detune * t + phase) * weight

    # Gentle low-pass warm modulation
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * t)
    ambient *= lfo

    # Scene Transition Chimes (Resonant harmonic bells at 0.0s, 4.8s, 9.8s, 15.2s, 19.6s)
    chime_times = [0.1, 4.8, 9.8, 15.2, 19.6]
    chimes = np.zeros(total_samples)

    for ct in chime_times:
        chime_start = int(ct * sample_rate)
        chime_dur = int(4.5 * sample_rate)
        chime_end = min(total_samples, chime_start + chime_dur)
        if chime_end > chime_start:
            ct_arr = np.linspace(0, (chime_end - chime_start) / sample_rate, chime_end - chime_start, False)
            decay = np.exp(-1.2 * ct_arr)
            # Harmonic overtone chime
            bell = (
                np.sin(2 * np.pi * 587.33 * ct_arr) * 0.4 +
                np.sin(2 * np.pi * 880.00 * ct_arr) * 0.25 +
                np.sin(2 * np.pi * 1174.66 * ct_arr) * 0.15 +
                np.sin(2 * np.pi * 1760.00 * ct_arr) * 0.10
            ) * decay
            chimes[chime_start:chime_end] += bell

    # Subtle clock ticks in final scene (19.6s to 23.5s)
    ticks = np.zeros(total_samples)
    for tick_t in np.arange(19.6, 23.5, 1.0):
        t_start = int(tick_t * sample_rate)
        t_dur = int(0.05 * sample_rate)
        t_end = min(total_samples, t_start + t_dur)
        if t_end > t_start:
            sub_t = np.linspace(0, (t_end - t_start) / sample_rate, t_end - t_start, False)
            tick_pulse = np.sin(2 * np.pi * 1200 * sub_t) * np.exp(-60 * sub_t) * 0.15
            ticks[t_start:t_end] += tick_pulse

    # Master mix
    audio = (ambient * 0.6) + (chimes * 0.35) + (ticks * 0.2)

    # Master volume envelope (fade in 1.5s, fade out 2.5s)
    fade_in_len = int(1.5 * sample_rate)
    fade_out_len = int(2.5 * sample_rate)
    envelope = np.ones(total_samples)
    envelope[:fade_in_len] = np.linspace(0, 1, fade_in_len)
    envelope[-fade_out_len:] = np.linspace(1, 0, fade_out_len)

    audio *= envelope

    # Normalize to -1.0 dB
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.88

    # Stereo expander (subtle delay on right channel)
    stereo_left = audio
    delay_samples = int(0.012 * sample_rate)
    stereo_right = np.zeros_like(audio)
    stereo_right[delay_samples:] = audio[:-delay_samples]

    stereo_audio = np.vstack([stereo_left, stereo_right]).T
    int16_audio = (stereo_audio * 32767).astype(np.int16)

    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int16_audio.tobytes())

# ==============================================================================
# 5. MAIN EXECUTION
# ==============================================================================
def main():
    print("=" * 60)
    print("VACHAAN Official Launch Video Generator")
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS}fps, Duration: {DURATION_SEC}s ({TOTAL_FRAMES} frames)")
    print("=" * 60)

    raw_video_path = 'assets/video/vachaan-launch-raw.mp4'
    soundtrack_path = 'assets/video/vachaan-soundtrack.wav'
    final_video_path = 'assets/video/vachaan-launch.mp4'

    # Step 1: Generate Soundtrack
    print("\n[1/3] Synthesizing cinematic orchestral soundtrack...")
    generate_soundtrack(soundtrack_path)
    print(f"Soundtrack generated: {os.path.getsize(soundtrack_path):,} bytes")

    # Step 2: Render & Encode Video Frames
    print("\n[2/3] Rendering 720 frames...")
    writer = imageio.get_writer(
        raw_video_path,
        fps=FPS,
        codec='libx264',
        pixelformat='yuv420p',
        quality=9,
        ffmpeg_params=['-preset', 'medium', '-crf', '18']
    )

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        writer.append_data(frame)
        if (i + 1) % 72 == 0 or i == TOTAL_FRAMES - 1:
            progress = ((i + 1) / TOTAL_FRAMES) * 100
            print(f"  Frame {i+1}/{TOTAL_FRAMES} ({progress:.0f}%) rendered")

    writer.close()
    print(f"Raw video stream encoded: {os.path.getsize(raw_video_path):,} bytes")

    # Step 3: Multiplex Video + Audio using FFmpeg
    print("\n[3/3] Multiplexing video and audio into final MP4...")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe,
        '-y',
        '-i', raw_video_path,
        '-i', soundtrack_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-b:a', '256k',
        '-shortest',
        final_video_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up intermediate raw files
    if os.path.exists(raw_video_path):
        os.remove(raw_video_path)

    print("\n" + "=" * 60)
    print("SUCCESS: VACHAAN Launch Video Created!")
    print(f"File Path: {final_video_path}")
    print(f"File Size: {os.path.getsize(final_video_path) / (1024*1024):.2f} MB")
    print("=" * 60)

if __name__ == '__main__':
    main()
