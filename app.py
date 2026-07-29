import streamlit as st
import json
import html

st.set_page_config(
    page_title="授業計画シート作成アプリ（三松メソッド）",
    page_icon="📝",
    layout="wide"
)

# 19の思考スキル定義
THINKING_SKILLS = {
    "分析・整理": ["多面的にみる", "順序立てる", "分類する", "変化をとらえる", "比較する", "変換する(図・絵など)"],
    "関係・構造": ["関係づける", "関連づける", "理由づける", "見通す", "構造化する"],
    "統合・評価": ["抽象化する", "焦点化する", "評価する", "応用する", "推論する", "具体化する", "広げてみる", "要約する"]
}

ALL_SKILLS_FLAT = [skill for cat in THINKING_SKILLS.values() for skill in cat]

QUESTIONS = [
    {"key": "subject", "label": "教科名", "type": "text", "prompt": "まずは【教科名】を入力してください。（例: 国語、数学、社会）"},
    {"key": "teacher", "label": "授業者", "type": "text", "prompt": "【授業者名】を入力してください。（例: 山田 太郎）"},
    {"key": "unit_title", "label": "単元（題材）名", "type": "text", "prompt": "【単元（題材）名】を入力してください。（例: ごんぎつね、1次関数）"},
    {"key": "unit_goal", "label": "単元（題材）の目標", "type": "textarea", "prompt": "【単元（題材）の目標】を入力してください。"},
    {"key": "student_status", "label": "生徒の実態", "type": "textarea", "prompt": "【生徒の実態】を入力してください。"},
    {"key": "teaching_ideas", "label": "指導上の工夫", "type": "textarea", "prompt": "【指導上の工夫】を入力してください。"},
    {"key": "viewpoint", "label": "本単元における教科の見方・考え方", "type": "textarea", "prompt": "【本単元における教科の見方・考え方】を入力してください。"},
    {"key": "total_hours", "label": "単元の総時間数", "type": "number", "prompt": "この単元は何時間設定ですか？（例: 5時間なら 5）"},
]

MATSUMATSU_PHASES = [
    {"key": "tsukamu", "title": "① つかむ"},
    {"key": "kangaeru", "title": "② 考える"},
    {"key": "manabi", "title": "③ 学び合う"},
    {"key": "matomeru", "title": "④ まとめる・振り返る"}
]

# セッション状態の初期化
if "step" not in st.session_state:
    st.session_state.step = 0
if "data" not in st.session_state:
    st.session_state.data = {"unit_plan": [], "matsumatsu": {}}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "こんにちは！授業計画シート作成ボットです。質問に順番に答えていくと、三松メソッドに沿った授業計画シートが完成します。\n\nまずは【教科名】を入力してください。"}
    ]
if "hours_done" not in st.session_state:
    st.session_state.hours_done = 0
if "matsumatsu_step" not in st.session_state:
    st.session_state.matsumatsu_step = 0

# 安全にHTML文字列化するヘルパー関数
def safe_html(text):
    if not text:
        return ""
    escaped = html.escape(str(text))
    return escaped.replace("\n", "<br>")

st.title("📝 授業計画シート作成アプリ（三松メソッド対応）")
st.caption("対話形式で質問に答えるだけで、初めての人でも分かりやすい指導計画シートを生成します。")

# サイドバー
with st.sidebar:
    st.header("💾 データの保存・再開")
    save_data = {
        "step": st.session_state.step,
        "data": st.session_state.data,
        "chat_history": st.session_state.chat_history,
        "hours_done": st.session_state.hours_done,
        "matsumatsu_step": st.session_state.matsumatsu_step
    }
    json_str = json.dumps(save_data, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="💾 作業途中のデータを保存(JSON)",
        data=json_str,
        file_name="lesson_plan_progress.json",
        mime="application/json",
        help="チャットの途中でも、このボタンで保存しておけば後から続きを再開できます。"
    )
    
    uploaded_file = st.file_uploader("📂 保存データを読み込んで再開", type=["json"])
    if uploaded_file is not None:
        try:
            loaded_state = json.load(uploaded_file)
            st.session_state.step = loaded_state.get("step", 0)
            st.session_state.data = loaded_state.get("data", {"unit_plan": [], "matsumatsu": {}})
            st.session_state.chat_history = loaded_state.get("chat_history", [])
            st.session_state.hours_done = loaded_state.get("hours_done", 0)
            st.session_state.matsumatsu_step = loaded_state.get("matsumatsu_step", 0)
            st.success("作業データを読み込みました！続きから再開できます。")
            st.rerun()
        except Exception as e:
            st.error("ファイルの読み込みに失敗しました。正しいJSONファイルかご確認ください。")

    st.divider()
    st.header("📋 入力中のデータ概要")
    d_sb = st.session_state.data
    st.write(f"**教科**: {d_sb.get('subject', '未入力')}")
    st.write(f"**授業者**: {d_sb.get('teacher', '未入力')}")
    st.write(f"**単元**: {d_sb.get('unit_title', '未入力')}")
    st.divider()
    if st.button("🔄 最初からやり直す"):
        st.session_state.clear()
        st.rerun()

col_chat, col_preview = st.columns([1, 1.2])

with col_chat:
    st.subheader("💬 チャット対話エリア")
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    step = st.session_state.step
    
    # 基本情報入力
    if step < len(QUESTIONS):
        q = QUESTIONS[step]
        with st.form(key=f"form_step_{step}", clear_on_submit=True):
            if q["type"] == "text":
                val = st.text_input(q["label"])
            elif q["type"] == "textarea":
                val = st.text_area(q["label"])
            elif q["type"] == "number":
                val = st.number_input(q["label"], min_value=1, max_value=20, value=5)
            
            submitted = st.form_submit_button("回答を送信")
            if submitted and val:
                st.session_state.data[q["key"]] = val
                st.session_state.chat_history.append({"role": "user", "content": str(val)})
                st.session_state.step += 1
                
                if st.session_state.step < len(QUESTIONS):
                    next_q = QUESTIONS[st.session_state.step]
                    st.session_state.chat_history.append({"role": "assistant", "content": next_q["prompt"]})
                else:
                    total = int(st.session_state.data["total_hours"])
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"ありがとうございます！次に第1時～第{total}時までの【各時間の目標】と【身に付ける主となる思考スキル】を入力します。\nまず「第1時」の内容を入力してください。"
                    })
                st.rerun()

    # 単元計画入力
    elif step == len(QUESTIONS):
        total_hours = int(st.session_state.data["total_hours"])
        curr_h = st.session_state.hours_done + 1
        
        if curr_h <= total_hours:
            st.write(f"### ⏰ 第 {curr_h} 時 の入力")
            with st.form(key=f"form_hour_{curr_h}", clear_on_submit=True):
                h_goal = st.text_area(f"第 {curr_h} 時 の目標")
                h_skills = st.multiselect(f"第 {curr_h} 時 に身に付ける主となる思考スキル（複数選択可）", ALL_SKILLS_FLAT)
                
                submitted = st.form_submit_button(f"第 {curr_h} 時を登録")
                if submitted and h_goal:
                    st.session_state.data["unit_plan"].append({
                        "hour": curr_h,
                        "goal": h_goal,
                        "skills": h_skills
                    })
                    st.session_state.hours_done += 1
                    skills_str = ", ".join(h_skills) if h_skills else "なし"
                    st.session_state.chat_history.append({"role": "user", "content": f"第{curr_h}時: {h_goal} (思考スキル: {skills_str})"})
                    
                    if st.session_state.hours_done < total_hours:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"次に「第{curr_h + 1}時」の目標と思考スキルを入力してください。"
                        })
                    else:
                        st.session_state.step += 1
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"全{total_hours}時間分の計画が入力されました！\n次に【本時】が第何時にあたるかの選択と、本時のねらいを入力してください。"
                        })
                    st.rerun()

    # 本時選択
    elif step == len(QUESTIONS) + 1:
        total_hours = int(st.session_state.data["total_hours"])
        with st.form(key="form_honshi", clear_on_submit=True):
            honshi_num = st.selectbox("本時は第何時ですか？", range(1, total_hours + 1))
            honshi_aim = st.text_area("本時のねらい")
            submitted = st.form_submit_button("本時設定を完了")
            if submitted and honshi_aim:
                st.session_state.data["honshi_num"] = honshi_num
                st.session_state.data["honshi_aim"] = honshi_aim
                st.session_state.chat_history.append({"role": "user", "content": f"本時: 第{honshi_num}時\nねらい: {honshi_aim}"})
                st.session_state.step += 1
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "それでは最後に、指導課程（三松メソッド）を入力していきます。\nまずは【① つかむ】の学習内容、手立て、身に付ける思考スキル（複数選択可）、教員が意図する生徒の姿を入力してください。"
                })
                st.rerun()

    # 指導課程入力
    elif step == len(QUESTIONS) + 2:
        m_step = st.session_state.matsumatsu_step
        if m_step < len(MATSUMATSU_PHASES):
            phase = MATSUMATSU_PHASES[m_step]
            st.write(f"### 📍 指導課程: {phase['title']}")
            with st.form(key=f"form_matsumatsu_{m_step}", clear_on_submit=True):
                content = st.text_area("学習内容")
                tedate = st.text_area("手立て")
                skills = st.multiselect("身に付ける思考スキル（複数選択可）", ALL_SKILLS_FLAT)
                target_student = st.text_area("教員が意図する生徒の姿")
                
                submitted = st.form_submit_button(f"{phase['title']} を登録")
                if submitted:
                    st.session_state.data["matsumatsu"][phase["key"]] = {
                        "content": content,
                        "tedate": tedate,
                        "skills": skills,
                        "target_student": target_student
                    }
                    st.session_state.matsumatsu_step += 1
                    skills_str = ", ".join(skills) if skills else "なし"
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"【{phase['title']}】\n学習内容: {content}\n手立て: {tedate}\n思考スキル: {skills_str}\n教員が意図する生徒の姿: {target_student}"
                    })
                    
                    if st.session_state.matsumatsu_step < len(MATSUMATSU_PHASES):
                        next_p = MATSUMATSU_PHASES[st.session_state.matsumatsu_step]
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"次に【{next_p['title']}】を入力してください。"
                        })
                    else:
                        st.session_state.step += 1
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": "🎉 すべての入力が完了しました！右側のシート画面をご確認ください。"
                        })
                    st.rerun()

    else:
        st.success("🎉 すべての入力が完了しました！")
        st.info("右側のプレビュー画面で確認し、印刷またはPDF保存してご利用ください。")

# プレビュー表示エリア
with col_preview:
    st.subheader("📄 指導計画シート プレビュー")
    d = st.session_state.data
    mm_data = d.get("matsumatsu", {})

    def get_p(key):
        return mm_data.get(key, {"content": "", "tedate": "", "skills": [], "target_student": ""})

    tsukamu = get_p("tsukamu")
    kangaeru = get_p("kangaeru")
    manabi = get_p("manabi")
    matomeru = get_p("matomeru")

    def fmt_skills(skills):
        if not skills:
            return "( 未設定 )"
        return " / ".join(skills)

    preview_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{
            size: A4 portrait;
            margin: 10mm;
        }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ padding: 0 !important; background-color: #fff !important; }}
            .page {{ 
                border: none !important; 
                box-shadow: none !important; 
                margin: 0 !important; 
                padding: 0 !important;
                page-break-after: always; 
                height: 275mm; /* A4の印刷領域に合わせる */
                overflow: hidden;
            }}
        }}
        * {{
            box-sizing: border-box;
            word-break: break-word; /* 長文の崩れ防止 */
        }}
        body {{
            font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 10px;
            color: #000;
        }}
        .print-btn {{
            background-color: #0288d1;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .print-btn:hover {{ background-color: #01579b; }}
        
        /* A4サイズに最適化したページコンテナ */
        .page {{
            background-color: #ffffff;
            padding: 15px;
            border: 1px solid #ccc;
            font-size: 8.5pt;
            line-height: 1.3;
            margin-bottom: 25px;
            width: 100%;
            min-height: 270mm;
            position: relative;
        }}
        .page-title {{
            text-align: center;
            font-weight: bold;
            font-size: 10.5pt;
            background-color: #e6f0fa;
            padding: 5px;
            border: 1px solid #333;
            margin-bottom: 10px;
        }}
        table.tbl {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 8px;
        }}
        table.tbl th, table.tbl td {{
            border: 1px solid #333;
            padding: 3px 6px;
        }}
        table.tbl th {{
            background-color: #f2f2f2;
            text-align: center;
        }}

        /* 2ページ目（構造図解：相対配置で縦崩れを防ぐ柔軟レイアウト） */
        .diagram-wrapper {{
            display: flex;
            position: relative;
            width: 100%;
            gap: 10px;
            margin-top: 5px;
        }}

        /* 左側：「つなagu」の垂直循環ライン */
        .tsunagu-sidebar {{
            width: 45px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border-left: 18px solid #0288d1;
            border-top: 18px solid #0288d1;
            border-bottom: 18px solid #0288d1;
            border-top-left-radius: 25px;
            border-bottom-left-radius: 25px;
            position: relative;
            margin-left: 5px;
        }}
        .tsunagu-arrow-tip {{
            position: absolute;
            top: -18px;
            right: -25px;
            width: 0;
            height: 0;
            border-top: 15px solid transparent;
            border-bottom: 15px solid transparent;
            border-left: 20px solid #0288d1;
        }}
        .tsunagu-text {{
            font-size: 13pt;
            font-weight: bold;
            color: #0288d1;
            writing-mode: vertical-rl;
            letter-spacing: 4px;
            background: #fff;
            padding: 8px 2px;
        }}

        /* 右側：ステップの流れ */
        .flow-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .phase-card {{
            border: 2px solid #00bcd4;
            background-color: #e0f7fa;
            border-radius: 8px;
            padding: 8px 10px;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.05);
        }}
        .phase-card-title {{
            font-size: 10.5pt;
            font-weight: bold;
            text-decoration: underline;
            text-align: center;
            margin-bottom: 4px;
            color: #006064;
        }}
        
        /* カード内部の左右カラム固定・自動折り返し指定 */
        .phase-card-body {{
            display: flex;
            gap: 10px;
        }}
        .phase-card-left {{
            flex: 1.3;
            min-width: 0; /* カラムのはみ出し・ズレを防止 */
            font-size: 8pt;
        }}
        .phase-card-right {{
            flex: 1;
            min-width: 0; /* カラムのはみ出し・ズレを防止 */
            background-color: #1a5276;
            color: #fff;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 8pt;
        }}
        
        .skill-badge {{
            display: inline-block;
            background-color: #fff;
            border: 1.5px solid #ff9800;
            color: #333;
            font-weight: bold;
            padding: 1px 5px;
            border-radius: 4px;
            font-size: 7.5pt;
            margin-top: 4px;
        }}

        /* 各ステップ間の矢印 */
        .down-arrow-icon {{
            text-align: center;
            color: #0288d1;
            font-size: 14pt;
            line-height: 1;
            margin: -2px 0;
        }}
    </style>
    </head>
    <body>

    <button class="print-btn no-print" onclick="window.print()">🖨️ このシートを印刷 / PDF保存</button>

    <!-- 1ページ目：基本情報・単元計画・指導課程（表形式） -->
    <div class="page">
        <div class="page-title">
            目指す生徒の姿を組み込んだ授業計画シート 【研究主題】 すべての生徒がいきいきと輝く授業を具現化するための集団づくりと授業改善
        </div>
        <table class="tbl">
            <tr>
                <th style="width:15%;">教科</th>
                <td style="width:35%;">{safe_html(d.get("subject", ""))}</td>
                <th style="width:15%;">授業者</th>
                <td style="width:35%;">{safe_html(d.get("teacher", ""))}</td>
            </tr>
            <tr>
                <th>単元（題材）名</th>
                <td colspan="3">{safe_html(d.get("unit_title", ""))}</td>
            </tr>
            <tr>
                <th>単元（題材）の目標</th>
                <td colspan="3">{safe_html(d.get("unit_goal", ""))}</td>
            </tr>
            <tr>
                <th>生徒の実態</th>
                <td colspan="3">{safe_html(d.get("student_status", ""))}</td>
            </tr>
            <tr>
                <th>指導上の工夫</th>
                <td colspan="3">{safe_html(d.get("teaching_ideas", ""))}</td>
            </tr>
            <tr>
                <th>教科の見方・考え方</th>
                <td colspan="3">{safe_html(d.get("viewpoint", ""))}</td>
            </tr>
        </table>

        <div style="font-weight:bold; margin: 6px 0 3px 0; background:#eee; padding:2px 5px;">■ 単元計画</div>
        <table class="tbl">
            <tr>
                <th style="width:12%;">時間</th>
                <th style="width:53%;">各時間の目標</th>
                <th style="width:35%;">身に付ける主となる思考スキル</th>
            </tr>
    '''
    
    unit_plans = d.get("unit_plan", [])
    honshi_num = d.get("honshi_num", 0)
    if not unit_plans:
        preview_html += "<tr><td colspan='3' style='text-align:center; padding:8px; color:#888;'>単元計画は未入力です</td></tr>"
    else:
        for hp in unit_plans:
            is_honshi = "<br><span style='color:red; font-weight:bold;'>★本時</span>" if hp["hour"] == honshi_num else ""
            skills_str = ", ".join(hp["skills"]) if hp["skills"] else "-"
            bg_color = "#fff3cd" if hp["hour"] == honshi_num else "#ffffff"
            preview_html += f'''
            <tr style="background-color: {bg_color};">
                <td style="text-align:center;">第{hp['hour']}時{is_honshi}</td>
                <td>{safe_html(hp['goal'])}</td>
                <td><span style="background:#004085; color:#fff; padding:1px 4px; border-radius:3px; font-size:7.5pt;">{safe_html(skills_str)}</span></td>
            </tr>
            '''
            
    preview_html += f'''
        </table>
        <table class="tbl" style="margin-top:4px;">
            <tr>
                <th style="width:20%;">本時のねらい</th>
                <td>{safe_html(d.get("honshi_aim", ""))}</td>
            </tr>
        </table>

        <div style="font-weight:bold; margin: 6px 0 3px 0; background:#eee; padding:2px 5px;">■ 指導課程（概要）</div>
    '''
    for p in MATSUMATSU_PHASES:
        k = p["key"]
        p_info = mm_data.get(k, {})
        c_val = safe_html(p_info.get("content", ""))
        t_val = safe_html(p_info.get("tedate", ""))
        target = safe_html(p_info.get("target_student", ""))
        skills = p_info.get("skills", [])
        s_str = safe_html(", ".join(skills)) if skills else "なし"
        preview_html += f'''
        <div style="border: 1px solid #333; margin-bottom: 4px; padding: 3px; background-color: #fafafa;">
            <div style="font-weight:bold; background-color: #d9edf7; padding: 1px 4px; border-bottom: 1px solid #333; margin: -3px -3px 3px -3px; font-size:8.5pt;">{p['title']}</div>
            <table style="width:100%; border:none; border-collapse:collapse; font-size:8pt;">
                <tr style="border:none;">
                    <td style="border:none; width:50%; vertical-align:top; padding:1px 3px;">
                        <b>【学習内容】</b>: {c_val}<br>
                        <b>【手立て】</b>: {t_val}
                    </td>
                    <td style="border:none; width:50%; vertical-align:top; background-color:#ffffff; border-left:1px dashed #ccc; padding:1px 4px;">
                        <b>【思考スキル】</b>: <span style="color:#004085; font-weight:bold;">{s_str}</span><br>
                        <b>【教員が意図する生徒の姿】</b>: {target}
                    </td>
                </tr>
            </table>
        </div>
        '''

    preview_html += f'''
    </div>

    <!-- 2ページ目：指導課程（三松メソッド・構造図解） -->
    <div class="page">
        <div class="page-title">■ 指導課程（三松メソッド・構造図解）</div>
        
        <div class="diagram-wrapper">
            <!-- ループ（つなぐ）左サイドライン -->
            <div class="tsunagu-sidebar">
                <div class="tsunagu-arrow-tip"></div>
                <div class="tsunagu-text">つなぐ</div>
            </div>

            <!-- 右側 4フェーズの縦フロー -->
            <div class="flow-container">
                
                <!-- ① つかむ -->
                <div class="phase-card">
                    <div class="phase-card-title">① つかむ</div>
                    <div class="phase-card-body">
                        <div class="phase-card-left">
                            <b>学習内容:</b> {safe_html(tsukamu['content'])}<br>
                            <b>手立て:</b> {safe_html(tsukamu['tedate'])}<br>
                            <div class="skill-badge">💡 思考スキル: {safe_html(fmt_skills(tsukamu['skills']))}</div>
                        </div>
                        <div class="phase-card-right">
                            <b>教員が意図する生徒の姿:</b><br>
                            {safe_html(tsukamu['target_student'])}
                        </div>
                    </div>
                </div>

                <div class="down-arrow-icon">▼</div>

                <!-- ② 考える -->
                <div class="phase-card">
                    <div class="phase-card-title">② 考える</div>
                    <div class="phase-card-body">
                        <div class="phase-card-left">
                            <b>学習内容:</b> {safe_html(kangaeru['content'])}<br>
                            <b>手立て:</b> {safe_html(kangaeru['tedate'])}<br>
                            <div class="skill-badge">💡 思考スキル: {safe_html(fmt_skills(kangaeru['skills']))}</div>
                        </div>
                        <div class="phase-card-right">
                            <b>教員が意図する生徒の姿:</b><br>
                            {safe_html(kangaeru['target_student'])}
                        </div>
                    </div>
                </div>

                <div class="down-arrow-icon">▼</div>

                <!-- ③ 学び合う -->
                <div class="phase-card">
                    <div class="phase-card-title">③ 学び合う</div>
                    <div class="phase-card-body">
                        <div class="phase-card-left">
                            <b>学習内容:</b> {safe_html(manabi['content'])}<br>
                            <b>手立て:</b> {safe_html(manabi['tedate'])}<br>
                            <div class="skill-badge">💡 思考スキル: {safe_html(fmt_skills(manabi['skills']))}</div>
                        </div>
                        <div class="phase-card-right">
                            <b>教員が意図する生徒の姿:</b><br>
                            {safe_html(manabi['target_student'])}
                        </div>
                    </div>
                </div>

                <div class="down-arrow-icon">▼</div>

                <!-- ④ まとめる・振り返る -->
                <div class="phase-card">
                    <div class="phase-card-title">④ まとめる・振り返る</div>
                    <div class="phase-card-body">
                        <div class="phase-card-left">
                            <b>学習内容:</b> {safe_html(matomeru['content'])}<br>
                            <b>手立て:</b> {safe_html(matomeru['tedate'])}<br>
                            <div class="skill-badge">💡 思考スキル: {safe_html(fmt_skills(matomeru['skills']))}</div>
                        </div>
                        <div class="phase-card-right">
                            <b>教員が意図する生徒の姿:</b><br>
                            {safe_html(matomeru['target_student'])}
                        </div>
                    </div>
                </div>

            </div>
        </div>
        
        <div style="font-size: 7.5pt; margin-top: 8px; color: #555;">
            ※ 各教科の見方・考え方は学習指導要領の解説 教科の目標を参考にする
        </div>
    </div>

    </body>
    </html>
    '''
    st.components.v1.html(preview_html, height=2200, scrolling=True)
