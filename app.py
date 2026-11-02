import streamlit as st
import re
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime, timedelta, timezone


st.set_page_config(
    page_title="皮皮精算師",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

taiwan_timezone = timezone(timedelta(hours=8))
today = datetime.now(taiwan_timezone).date()


st.markdown(
    """
    <style>
    :root {
        --cream: #fffaf0;
        --caramel: #c97c36;
        --caramel-dark: #a85f28;
        --sage: #617b58;
        --sage-dark: #344631;
        --sage-light: #edf2e5;
        --ink: #384332;
        --muted: #777767;
        --line: #dedfc9;
        --leaf: #647f56;
    }

    .stApp {
        background:
            radial-gradient(circle at 94% 3%, #edbb78 0, #edbb78 6.3rem, transparent 6.4rem),
            radial-gradient(circle at 3% 11%, #e4ebd7 0, #e4ebd7 8.5rem, transparent 8.6rem),
            linear-gradient(180deg, #fffaf0 0%, #fffdf8 100%);
        color: var(--ink);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 540px;
        padding: 1rem 1rem 3.5rem;
    }

    h1, h2, h3, h4, p, label {
        color: var(--ink);
    }

    h1 {
        font-size: clamp(1.75rem, 7vw, 2.25rem) !important;
        line-height: 1.15 !important;
        margin: 0 !important;
        letter-spacing: -0.04em;
    }

    .subtitle {
        color: #68745c;
        font-size: 1rem;
        font-weight: 500;
        line-height: 1.5;
        margin-top: 0.65rem;
    }

    .today-label {
        color: var(--muted);
        font-size: 1rem;
        margin-top: 0.55rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--line);
        border-radius: 22px;
        box-shadow: 0 8px 24px rgba(91, 107, 68, 0.08);
    }

    div[data-testid="stSegmentedControl"] button {
        min-height: 3rem;
        border-radius: 12px !important;
        font-size: 1.14rem !important;
        font-weight: 700;
    }

    div[data-testid="stSegmentedControl"] button p {
        font-size: 1.14rem !important;
        font-weight: 750 !important;
    }

    div[data-testid="stButton"] button {
        width: 100%;
        min-height: 3.45rem;
        border: 0;
        border-radius: 16px;
        background: linear-gradient(135deg, #edbb78, #c97c36);
        color: #344631;
        font-size: 1.08rem;
        font-weight: 850;
        box-shadow: 0 8px 18px rgba(201, 124, 54, 0.20);
    }

    div[data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #f0c88e, #bb7133);
        color: #384332;
        border: 0;
    }

    div[data-testid="stDateInput"] input {
        border-radius: 12px;
    }

    div[data-testid="stCheckbox"] label p {
        font-size: 1rem;
        font-weight: 650;
    }

    details {
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        background: #ffffff !important;
    }

    .section-label {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: var(--sage);
        font-size: 1.15rem;
        font-weight: 850;
        margin-bottom: 0.15rem;
    }

    .result-banner {
        border-radius: 18px;
        padding: 1rem 1.05rem;
        background: linear-gradient(135deg, #ffe3b5, #ffc66f);
        border: 1px solid #f2ad4b;
        margin-bottom: 0.7rem;
    }

    .result-banner-title {
        color: #59301b;
        font-size: 1.2rem;
        font-weight: 900;
        margin-bottom: 0.2rem;
    }

    .result-banner-note {
        color: #755138;
        font-size: 0.86rem;
    }

    .day-heading {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 1.08rem;
        font-weight: 900;
        color: var(--sage);
        margin-bottom: 0.35rem;
    }

    .day-dot {
        width: 0.7rem;
        height: 0.7rem;
        border-radius: 99px;
        background: var(--caramel);
        display: inline-block;
        flex: 0 0 auto;
    }

    .task-plant {
        color: #367b43;
        font-weight: 800;
    }

    .task-mushroom {
        color: #b55b18;
        font-weight: 750;
    }

    .task-normal {
        color: #525c46;
        font-weight: 650;
    }

    .page-footer {
        margin-top: 2.5rem;
        padding: 1.2rem 0 0.2rem;
        text-align: center;
        color: #83866e;
        font-size: 0.84rem;
        letter-spacing: 0.08rem;
    }

    @media (max-width: 480px) {
        .block-container {
            padding: 0.75rem 0.8rem 3rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.65rem;
        }

        div[data-testid="stSegmentedControl"] button {
            min-height: 3.15rem;
            padding-left: 0.3rem;
            padding-right: 0.3rem;
            font-size: 1.08rem !important;
        }

        div[data-testid="stSegmentedControl"] button p {
            font-size: 1.08rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


missions = {
    1: {
        1: [("走1000步", 0)],
        2: [("培育2隻皮克敏", 0)],
        3: [("完成2個探險", 0)],
        4: [("種1000朵花", 0), ("摧毀2棵蘑菇", 2)],
    },
    2: {
        1: [("走2000步", 0)],
        2: [("種1000朵花", 0), ("摧毀2棵蘑菇", 2)],
        3: [("培育3隻皮克敏", 0), ("摧毀3棵蘑菇", 3)],
        4: [("種500朵天竺葵", 0), ("摧毀4棵蘑菇", 4)],
    },
    3: {
        1: [("走2000步", 0), ("完成2個探險", 0)],
        2: [("種1500朵白色鼠尾草", 0), ("摧毀3棵蘑菇", 3)],
        3: [("種1500朵紅色鼠尾草", 0), ("摧毀4棵蘑菇", 4)],
        4: [
            ("種1500朵黃色鼠尾草", 0),
            ("種2000朵紅色天竺葵", 0),
            ("摧毀5棵蘑菇", 5),
        ],
    },
    4: {
        1: [("完成3個探險", 0), ("摧毀3棵蘑菇", 3)],
        2: [("種2000朵白色天竺葵", 0), ("摧毀4棵蘑菇", 4)],
        3: [
            ("種2000朵黃色天竺葵", 0),
            ("種1000朵藍色鼠尾草", 0),
            ("摧毀4棵蘑菇", 4),
        ],
        4: [
            ("種2000朵藍色天竺葵", 0),
            ("種2500朵鼠尾草", 0),
            ("摧毀5棵蘑菇", 5),
        ],
    },
}


def mushroom_target(stage, group):
    for _, mushroom_count in missions[stage][group]:
        if mushroom_count > 0:
            return mushroom_count
    return 0


def next_position(round_number, stage, group):
    group += 1
    if group > 4:
        group = 1
        stage += 1
    if stage > 4:
        stage = 1
        round_number += 1
    return round_number, stage, group


def make_schedule(
    start_date,
    round_number,
    stage,
    group,
    current_mushrooms,
    mushrooms_left_today,
):
    current_date = start_date
    current_round = round_number
    current_stage = stage
    current_group = group
    progress = current_mushrooms
    schedule = []
    completed_rounds = []
    listed_plant_tasks = set()

    if start_date.month == 12:
        next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
    else:
        next_month = start_date.replace(month=start_date.month + 1, day=1)
    month_end = next_month - timedelta(days=1)

    while current_date <= month_end:
        daily_chances = mushrooms_left_today if current_date == start_date else 3
        actions = []
        safety_counter = 0

        while safety_counter < 30:
            safety_counter += 1
            tasks = missions[current_stage][current_group]
            normal_tasks = [name for name, count in tasks if count == 0]
            target = mushroom_target(current_stage, current_group)

            for task_name in normal_tasks:
                action = f"完成「{task_name}」"
                # 同一輪、同一小關的種花任務只列一次；培育等任務維持原顯示。
                task_key = (current_round, current_stage, current_group, task_name)
                if not task_name.startswith("種") or task_key not in listed_plant_tasks:
                    if action not in actions:
                        actions.append(action)
                    if task_name.startswith("種"):
                        listed_plant_tasks.add(task_key)

            if target == 0:
                old_round = current_round
                current_round, current_stage, current_group = next_position(
                    current_round, current_stage, current_group
                )
                progress = 0
                if current_round > old_round:
                    completed_rounds.append((old_round, current_date))
                continue

            if daily_chances == 0:
                break

            needed = target - progress
            used = min(daily_chances, needed)
            progress += used
            daily_chances -= used
            actions.append(f"摧毀蘑菇{used}棵（{progress}/{target}）")

            if progress < target:
                break

            old_round = current_round
            current_round, current_stage, current_group = next_position(
                current_round, current_stage, current_group
            )
            progress = 0
            if current_round > old_round:
                completed_rounds.append((old_round, current_date))
            if daily_chances == 0:
                break

        schedule.append(
            {
                "date": current_date,
                "actions": actions,
                "round": current_round,
                "stage": current_stage,
                "group": current_group,
                "progress": progress,
            }
        )
        current_date += timedelta(days=1)

    return schedule, completed_rounds



def compact_action(action):
    match = re.search(r"摧毀蘑菇(\d+)棵", action)
    if match:
        return f"{match.group(1)}菇"

    task = action
    if task.startswith("完成「") and task.endswith("」"):
        task = task[3:-1]

    match = re.fullmatch(r"走(\d+)步", task)
    if match:
        return f"{match.group(1)}步"

    match = re.fullmatch(r"培育(\d+)隻皮克敏", task)
    if match:
        return f"{match.group(1)}皮"

    match = re.fullmatch(r"完成(\d+)個探險", task)
    if match:
        return f"{match.group(1)}探"

    match = re.fullmatch(r"種(\d+)朵(.+)", task)
    if match:
        count, flower = match.groups()
        flower_names = {
            "花": "花",
            "天竺葵": "葵",
            "白色天竺葵": "白葵",
            "紅色天竺葵": "紅葵",
            "黃色天竺葵": "黃葵",
            "藍色天竺葵": "藍葵",
            "鼠尾草": "鼠",
            "白色鼠尾草": "白鼠",
            "紅色鼠尾草": "紅鼠",
            "黃色鼠尾草": "黃鼠",
            "藍色鼠尾草": "藍鼠",
        }
        return f"{count}{flower_names.get(flower, flower)}"

    return task


def make_export_text(schedule):
    weekday_short = ["一", "二", "三", "四", "五", "六", "日"]
    lines = []
    for day in schedule:
        if not day["actions"]:
            continue
        date = day["date"]
        date_text = f"{date.month}/{date.day}({weekday_short[date.weekday()]})"
        compact_actions = [compact_action(action) for action in day["actions"]]
        lines.append(f"{date_text} " + "/".join(compact_actions))
    return "\n".join(lines)



ASSET_DIR = Path(__file__).resolve().parent / "assets"
FONT_URL = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/TC/NotoSansTC-Regular.otf"


@st.cache_data(show_spinner=False)
def wallpaper_background():
    return (ASSET_DIR / "november_garden.png").read_bytes()


@st.cache_data(show_spinner=False)
def wallpaper_font_bytes():
    # 可隨部署附上開源 Noto 字型；否則首次使用時下載並在記憶體快取。
    for name in ("NotoSansTC-Regular.otf", "NotoSansTC-Regular.ttf"):
        candidate = ASSET_DIR / name
        if candidate.exists():
            return candidate.read_bytes()
    try:
        with urlopen(FONT_URL, timeout=20) as response:
            data = response.read()
        ImageFont.truetype(BytesIO(data), 24)
        return data
    except Exception as exc:
        # Windows 本機可使用已安裝的中文字型，不把系統字型重新散布。
        local_font = Path("C:/Windows/Fonts/msjh.ttc")
        if local_font.exists():
            return local_font.read_bytes()
        raise RuntimeError(
            "暫時無法取得中文字型，請稍後重試，或將 NotoSansTC-Regular.otf 放入 assets 資料夾。"
        ) from exc


def make_wallpaper(schedule, start_date, end_date, top_percent, background, font_data):
    """只依已有排程排字；不重算進度，也不更動 TXT 內容。"""
    if end_date < start_date:
        raise ValueError("結束日期不可早於開始日期。")
    if (end_date - start_date).days >= 14:
        raise ValueError("每張桌布最多放 14 天，請縮短日期範圍。")
    selected = [day for day in schedule if start_date <= day["date"] <= end_date]
    if not selected:
        raise ValueError("這段日期沒有排程，請重新選擇。")
    if not 40 <= top_percent <= 48:
        raise ValueError("文字位置需介於 40% 到 48%。")

    image = Image.open(BytesIO(background)).convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    scale = width / 853
    left = round(width * 0.065)
    right = round(width * 0.94)
    top = round(height * top_percent / 100)
    bottom = round(height * 0.82)
    orange = "#c56a24"
    green = "#3e5844"

    def font(size):
        return ImageFont.truetype(BytesIO(font_data), max(1, round(size)))

    title_font = font(47 * scale)
    small_font = font(23 * scale)
    draw.text((left, top), "11月任務", font=title_font, fill=orange, anchor="lt")
    subtitle_y = top + round(62 * scale)
    draw.text(
        (left, subtitle_y),
        f"2026・深秋花園  {start_date.month}/{start_date.day}–{end_date.month}/{end_date.day}",
        font=small_font, fill=green, anchor="lt",
    )
    body_top = top + round(108 * scale)
    available = bottom - body_top
    row_height = min(51 * scale, available / len(selected))
    weekdays = "一二三四五六日"
    rows = []
    for day in selected:
        current_date = day["date"]
        label = f"{current_date.month}/{current_date.day}({weekdays[current_date.weekday()]})"
        tokens = [compact_action(action) for action in day["actions"]]
        rows.append((label, tokens or ["等待免費蘑菇次數"]))

    # 所有日期共用同一字級，依最長一行及可用高度縮放，絕不截斷文字。
    size = round(min(31 * scale, row_height * 0.74))
    while size >= round(18 * scale):
        body_font = font(size)
        date_width = max(draw.textlength(label, font=body_font) for label, _ in rows)
        task_x = left + date_width + round(22 * scale)
        if all(task_x + draw.textlength(" / ".join(tokens), font=body_font) <= right
               for _, tokens in rows):
            break
        size -= 1
    else:
        raise ValueError("文字太多，請縮短日期範圍或將文字位置往上移。")
    for index, (label, tokens) in enumerate(rows):
        y = round(body_top + index * row_height)
        draw.text((left, y), label, font=body_font, fill=orange, anchor="lt")
        x = task_x
        for token_index, token in enumerate(tokens):
            if token_index:
                separator = " / "
                draw.text((x, y), separator, font=body_font, fill=green, anchor="lt")
                x += draw.textlength(separator, font=body_font)
            draw.text((x, y), token, font=body_font,
                      fill=orange if re.fullmatch(r"\d+菇", token) else green, anchor="lt")
            x += draw.textlength(token, font=body_font)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


st.title("🌿 皮皮精算師 🌼")
st.caption("2026 年 11 月・深秋花園｜鼠尾草 × 天竺葵")
st.markdown(
    '<div class="subtitle">我們並不是以遊戲的心情玩皮克敏的</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="today-label">今天是 {today.year} 年 {today.month} 月 {today.day} 日</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown('<div class="section-label">🍂 十一月花園記事</div>', unsafe_allow_html=True)
    st.markdown("**11/14、11/15｜社群日**")
    st.markdown("**11/27、11/30｜巨菇加碼**")
    st.caption("活動日期僅供提醒；排程維持每天 3 次免費蘑菇，一般任務預設當天完成。")

st.write("")

with st.container(border=True):
    st.markdown('<div class="section-label">🌿 目前進度</div>', unsafe_allow_html=True)

    selected_date = st.date_input(
        "查詢日期",
        value=min(max(today, date(2026, 11, 1)), date(2026, 11, 30)),
        min_value=date(2026, 11, 1),
        max_value=date(2026, 11, 30),
        format="YYYY/MM/DD",
    )

    round_number = st.segmented_control(
        "第幾輪",
        options=[1, 2, 3, 4],
        default=1,
        format_func=lambda number: f"第{number}輪",
    )
    stage = st.segmented_control(
        "第幾階段",
        options=[1, 2, 3, 4],
        default=1,
        format_func=lambda number: f"第{number}階段",
    )
    group = st.segmented_control(
        "第幾小關",
        options=[1, 2, 3, 4],
        default=1,
        format_func=lambda number: f"第{number}小關",
    )

    st.markdown("#### 這一關的任務")
    tasks = missions[stage][group]
    target = mushroom_target(stage, group)

    for task_name, count in tasks:
        if count == 0:
            st.checkbox(task_name, key=f"{stage}_{group}_{task_name}")

    if target > 0:
        current_mushrooms = st.segmented_control(
            f"已摧毀幾棵蘑菇？（目標{target}棵）",
            options=list(range(target + 1)),
            default=0,
            format_func=lambda number: f"{number}棵",
        )
    else:
        current_mushrooms = 0

    mushrooms_left_today = st.segmented_control(
        "今天還剩幾次免費蘑菇？",
        options=[3, 2, 1, 0],
        default=0,
        format_func=lambda number: "已用完" if number == 0 else f"剩{number}次",
    )

    calculate = st.button("幫我排後續進度", use_container_width=True)


query_signature = (
    selected_date, round_number, stage, group, current_mushrooms, mushrooms_left_today
)
if calculate and any(value is None for value in query_signature):
    st.warning("請先選好輪次、階段、小關與蘑菇次數。")
    calculate = False

if calculate:
    result = make_schedule(
        start_date=selected_date,
        round_number=int(round_number),
        stage=stage,
        group=group,
        current_mushrooms=int(current_mushrooms),
        mushrooms_left_today=mushrooms_left_today,
    )
    st.session_state["calculated_schedule"] = (query_signature, result)

saved_result = st.session_state.get("calculated_schedule")
if saved_result is not None and saved_result[0] == query_signature:
    schedule, completed_rounds = saved_result[1]
    final_position = schedule[-1]

    st.write("")
    st.markdown(
        """
        <div class="result-banner">
            <div class="result-banner-title">📊 預計進度</div>
            <div class="result-banner-note">依每天 3 次免費蘑菇推算</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        if completed_rounds:
            for completed_round, completion_date in completed_rounds:
                st.markdown(
                    f"**{completion_date.month}月{completion_date.day}日**　"
                    f"預計完成第 {completed_round} 輪"
                )
        else:
            st.write("本月底前預計尚未完成目前這一輪。")

        st.markdown(
            f"**月底位置：** 第{final_position['round']}輪・"
            f"第{final_position['stage']}階段・第{final_position['group']}小關"
        )

        if final_position["progress"] > 0:
            final_target = mushroom_target(
                final_position["stage"], final_position["group"]
            )
            st.markdown(
                f"**月底蘑菇進度：** {final_position['progress']} / {final_target}"
            )

        st.caption("種花任務預設在首次列出的當天完成，跨日等待蘑菇時不重複列出；培育等任務維持原顯示，實際進度可能順延。")

    export_text = make_export_text(schedule)

    st.markdown("#### 📄 匯出每日排程")
    st.code(export_text, language=None)

    st.download_button(
        "下載每日排程 TXT",
        data=export_text.encode("utf-8-sig"),
        file_name=f"pikmin_schedule_{selected_date.strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    with st.expander("查看每日詳細安排", expanded=False):
        weekday_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]

        for day in schedule:
            if day["date"].day in (14, 15):
                st.caption("🌼 社群日")
            if day["date"].day in (27, 30):
                st.caption("🍄 巨菇加碼")
            weekday = weekday_names[day["date"].weekday()]
            date_text = f"{day['date'].month}/{day['date'].day}（{weekday}）"

            with st.container(border=True):
                st.markdown(
                    f'<div class="day-heading"><span class="day-dot"></span>{date_text}</div>',
                    unsafe_allow_html=True,
                )

                if day["actions"]:
                    for action in day["actions"]:
                        if "種" in action:
                            css_class = "task-plant"
                            icon = "🌼"
                        elif "蘑菇" in action:
                            css_class = "task-mushroom"
                            icon = "🍄"
                        else:
                            css_class = "task-normal"
                            icon = "✓"

                        st.markdown(
                            f'<div class="{css_class}">{icon}　{action}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.write("等待明天的免費蘑菇次數")

                st.caption(
                    f"當日結束：第{day['round']}輪・"
                    f"第{day['stage']}階段・第{day['group']}小關"
                )


st.markdown("---")
st.markdown("### 🖼️ 十一月桌布下載")
with st.expander("🖼️ 下載十一月純底圖", expanded=False):
    try:
        background_png = wallpaper_background()
        st.image(background_png, caption="深秋花園・純底圖", width=260)
        st.download_button(
            "下載純底圖 PNG", data=background_png,
            file_name="pikmin_202611_garden.png", mime="image/png",
            key="download_background", use_container_width=True,
        )
    except OSError:
        st.error("找不到桌布底圖，請確認 assets 資料夾已與 app.py 一起上傳。")


if saved_result is not None and saved_result[0] == query_signature:
    st.markdown("#### 🖼️ 下載含進度文字的桌布")
    st.caption("每張可放 1～14 天，預設兩週。內容與上方 TXT 相同，文字上方保留時鐘與小工具空間。")
    # 換一次查詢結果才重設日期；調整位置或下載不會清掉計算結果。
    if st.session_state.get("wallpaper_query") != query_signature:
        st.session_state["wallpaper_start"] = schedule[0]["date"]
        st.session_state["wallpaper_end"] = min(
            schedule[0]["date"] + timedelta(days=13), schedule[-1]["date"]
        )
        st.session_state["wallpaper_query"] = query_signature
    start_column, end_column = st.columns(2)
    with start_column:
        wallpaper_start = st.date_input(
            "桌布開始日期", value=None, min_value=schedule[0]["date"],
            max_value=schedule[-1]["date"], key="wallpaper_start", format="YYYY/MM/DD",
        )
    with end_column:
        wallpaper_end = st.date_input(
            "桌布結束日期", value=None, min_value=schedule[0]["date"],
            max_value=schedule[-1]["date"], key="wallpaper_end", format="YYYY/MM/DD",
        )
    wallpaper_top = st.slider(
        "文字往下移（數字越大，越靠下）", min_value=40, max_value=48, value=42,
        format="%d%%", key="wallpaper_top",
    )
    if wallpaper_start is None or wallpaper_end is None:
        st.info("請選擇桌布的開始與結束日期。")
    elif wallpaper_end < wallpaper_start:
        st.warning("結束日期不可早於開始日期。")
    elif (wallpaper_end - wallpaper_start).days >= 14:
        st.warning("每張桌布最多 14 天，請縮短日期範圍；其餘日期可以另外下載一張。")
    else:
        try:
            with st.spinner("正在製作桌布…"):
                wallpaper_png = make_wallpaper(
                    schedule, wallpaper_start, wallpaper_end, wallpaper_top,
                    wallpaper_background(), wallpaper_font_bytes(),
                )
            st.image(wallpaper_png, caption="桌布預覽", width=300)
            st.download_button(
                "下載含進度桌布 PNG", data=wallpaper_png,
                file_name=(f"pikmin_wallpaper_{wallpaper_start:%Y%m%d}_"
                           f"{wallpaper_end:%Y%m%d}.png"),
                mime="image/png", key="download_schedule_wallpaper",
                use_container_width=True,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            st.error(f"桌布暫時無法產生：{exc}")

else:
    st.caption("想下載含進度的桌布，請先在上方計算排程。")


st.markdown(
    '<div class="page-footer">© 踢歪嘻嘻嘻</div>',
    unsafe_allow_html=True,
)
