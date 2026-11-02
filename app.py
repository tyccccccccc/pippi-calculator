import streamlit as st
import re
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
                if action not in actions:
                    actions.append(action)

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


if calculate:
    schedule, completed_rounds = make_schedule(
        start_date=selected_date,
        round_number=int(round_number),
        stage=stage,
        group=group,
        current_mushrooms=int(current_mushrooms),
        mushrooms_left_today=mushrooms_left_today,
    )
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

        st.caption("一般任務預設可在排定當天完成；實際進度可能因種花或步數順延。")

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


st.markdown(
    '<div class="page-footer">© 踢歪嘻嘻嘻</div>',
    unsafe_allow_html=True,
)
