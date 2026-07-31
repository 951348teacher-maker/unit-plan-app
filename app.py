import json
import streamlit as st

# 1. ページ基本設定
st.set_page_config(
    page_title="授業計画シート作成アプリ（三松メソッド）",
    page_icon="📝",
    layout="wide",
)

# 19の思考スキル定義
THINKING_SKILLS = {
    "分析・整理": [
        "多面的にみる",
        "順序立てる",
        "分類する",
        "変化をとらえる",
        "比較する",
        "変換する(図・絵など)",
    ],
    "関係・構造": [
        "関係づける",
        "関連づける",
        "理由づける",
        "見通す",
        "構造化する",
    ],
    "統合・評価": [
        "抽象化する",
        "焦点化する",
        "評価する",
        "応用する",
        "推論する",
        "具体化する",
        "広げてみる",
        "要約する",
    ],
}

# セッション状態の初期化
if "data" not in st.session_state:
  st.session_state.data = {
      "subject": "",
      "teacher": "",
      "unit_title": "",
      "unit_goal": "",
      "student_status": "",
      "teaching_ideas": "",
      "viewpoint": "",
      "total_hours": 5,
      "tsukamu": "",
      "kangaeru": "",
      "manabi": "",
      "matomeru": "",
      "hours": [],
  }

if "step" not in st.session_state:
  st.session_state.step = 0

# アプリタイトル
st.title("📝 授業計画シート作成アプリ（三松メソッド対応）")

# サイドバー（保存・復元・リセット）
with st.sidebar:
  st.header("💾 データの保存・復元")
  save_json = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
  st.download_button(
      "💾 作業データを保存(JSON)",
      data=save_json,
      file_name="matsumatsu_lesson_plan.json",
      mime="application/json",
  )

  uploaded_file = st.file_uploader(
      "📂 保存データを読み込んで再開", type=["json"]
  )
  if uploaded_file is not None:
    try:
      loaded_data = json.load(uploaded_file)
      st.session_state.data = loaded_data
      st.success("データを復元しました！")
      st.rerun()
    except Exception:
      st.error("ファイルの読み込みに失敗しました。")

  st.divider()
  if st.button("🔄 最初からやり直す"):
    st.session_state.clear()
    st.rerun()

# 質問リストの定義
QUESTIONS = [
    {
        "key": "subject",
        "label": "教科名",
        "type": "text",
        "prompt": "①【教科名】を入力してください。（例: 国語、数学、社会）",
    },
    {
        "key": "teacher",
        "label": "授業者名",
        "type": "text",
        "prompt": "②【授業者名】を入力してください。（例: 山田 太郎）",
    },
    {
        "key": "unit_title",
        "label": "単元（題材）名",
        "type": "text",
        "prompt": "③【単元（題材）名】を入力してください。",
    },
    {
        "key": "unit_goal",
        "label": "単元（題材）の目標",
        "type": "textarea",
        "prompt": "④【単元（題材）の目標】を入力してください。",
    },
    {
        "key": "student_status",
        "label": "生徒の実態",
        "type": "textarea",
        "prompt": "⑤【生徒の実態】を入力してください。",
    },
    {
        "key": "teaching_ideas",
        "label": "指導上の工夫",
        "type": "textarea",
        "prompt": "⑥【指導上の工夫】を入力してください。",
    },
    {
        "key": "viewpoint",
        "label": "本単元における教科の見方・考え方",
        "type": "textarea",
        "prompt": "⑦【本単元における教科の見方・考え方】を入力してください。",
    },
    {
        "key": "total_hours",
        "label": "単元の総時間数",
        "type": "number",
        "prompt": (
            "⑧ この単元は何時間設定ですか？（例: 5時間なら 5）"
        ),
    },
    {
        "key": "tsukamu",
        "label": "三松メソッド ① つかむ",
        "type": "textarea",
        "prompt": (
            "⑨ 三松メソッド【①"
            " つかむ】（課題設定・導入など）の内容を入力してください。"
        ),
    },
    {
        "key": "kangaeru",
        "label": "三松メソッド ② 考える",
        "type": "textarea",
        "prompt": (
            "⑩ 三松メソッド【②"
            " 考える】（個人思考・探究など）の内容を入力してください。"
        ),
    },
    {
        "key": "manabi",
        "label": "三松メソッド ③ 学び合う",
        "type": "textarea",
        "prompt": (
            "⑪ 三松メソッド【③"
            " 学び合う】（対話・協働など）の内容を入力してください。"
        ),
    },
    {
        "key": "matomeru",
        "label": "三松メソッド ④ まとめる・振り返る",
        "type": "textarea",
        "prompt": (
            "⑫ 三松メソッド【④"
            " まとめる・振り返る】（まとめ・リフレクションなど）の内容を入力してください。"
        ),
    },
]

# 左右2列レイアウト
col_left, col_right = st.columns([1, 1.2])

with col_left:
  st.subheader("💬 入力フォーム")
  step = st.session_state.step

  # 基本情報・三松メソッド質問フェーズ
  if step < len(QUESTIONS):
    q = QUESTIONS[step]
    st.info(f"**ステップ {step+1} / {len(QUESTIONS)}**: {q['prompt']}")

    with st.form(key=f"q_form_{step}"):
      if q["type"] == "text":
        val = st.text_input(
            q["label"], value=st.session_state.data.get(q["key"], "")
        )
      elif q["type"] == "textarea":
        val = st.text_area(
            q["label"], value=st.session_state.data.get(q["key"], "")
        )
      elif q["type"] == "number":
        val = st.number_input(
            q["label"],
            min_value=1,
            max_value=20,
            value=int(st.session_state.data.get(q["key"], 5)),
        )

      sub = st.form_submit_button("次へ進む ➔")
      if sub:
        st.session_state.data[q["key"]] = val
        st.session_state.step += 1
        st.rerun()

  # 時間ごとの詳細計画フェーズ
  else:
    tot = int(st.session_state.data.get("total_hours", 5))
    hours = st.session_state.data.get("hours", [])

    while len(hours) < tot:
      hours.append({"content": "", "skills": [], "eval": ""})
    st.session_state.data["hours"] = hours

    h_idx = step - len(QUESTIONS)

    if h_idx < tot:
      st.info(
          f"**【第 {h_idx+1} / {tot} 時間目】** の計画を入力してください"
      )
      curr_h = hours[h_idx]

      with st.form(key=f"h_form_{h_idx}"):
        c_val = st.text_area(
            "学習内容・主な活動", value=curr_h.get("content", "")
        )

        all_skills = [s for cat in THINKING_SKILLS.values() for s in cat]
        s_val = st.multiselect(
            "使用する思考スキル（複数選択可）",
            options=all_skills,
            default=curr_h.get("skills", []),
        )

        e_val = st.text_area("評価規準・評価方法", value=curr_h.get("eval", ""))

        sub_h = st.form_submit_button("この時間を保存して次へ ➔")
        if sub_h:
          st.session_state.data["hours"][h_idx] = {
              "content": c_val,
              "skills": s_val,
              "eval": e_val,
          }
          st.session_state.step += 1
          st.rerun()
    else:
      st.success(
          "🎉"
          " すべての項目の入力が完了しました！右側の完成シートをご確認ください。"
      )
      if st.button("✏️ 内容を修正する"):
        st.session_state.step = 0
        st.rerun()

  # 前のステップへ戻るボタン
  if step > 0:
    if st.button("⬅️ 前の質問に戻る"):
      st.session_state.step -= 1
      st.rerun()

with col_right:
  st.subheader("📄 授業計画シート（完成イメージ表）")
  d = st.session_state.data

  hours_rows = ""
  for idx, h in enumerate(d.get("hours", [])):
    skills_tags = "".join([
        '<span style="background-color:#e1f5fe; color:#0277bd; padding:2px'
        " 6px; margin:2px; border-radius:4px; display:inline-block;"
        f' font-size:11px;">{s}</span>'
        for s in h.get("skills", [])
    ])
    if not skills_tags:
      skills_tags = '<span style="color:#aaa;">なし</span>'

    hours_rows += f"""
        <tr>
            <td style="text-align:center; font-weight:bold; background-color:#f9f9f9; border:1px solid #ccc;">第 {idx+1} 時</td>
            <td style="border:1px solid #ccc; white-space:pre-wrap;">{h.get('content', '')}</td>
            <td style="border:1px solid #ccc;">{skills_tags}</td>
            <td style="border:1px solid #ccc; white-space:pre-wrap;">{h.get('eval', '')}</td>
        </tr>
        """

  html_preview = f"""
    <div style="border: 2px solid #2b5797; padding: 15px; border-radius: 8px; background-color: #ffffff; font-family: sans-serif; font-size: 13px; color: #333;">
        <h2 style="text-align: center; color: #2b5797; border-bottom: 2px solid #2b5797; padding-bottom: 8px; margin-top:0;">授業計画シート（三松メソッド）</h2>
        
        <table style="width:100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #ccc;" cellpadding="6">
            <tr style="background-color: #f2f4f8;">
                <th style="width:15%; border:1px solid #ccc; text-align:center;">教科名</th>
                <td style="width:35%; border:1px solid #ccc;">{d.get('subject', '')}</td>
                <th style="width:15%; border:1px solid #ccc; text-align:center;">授業者</th>
                <td style="width:35%; border:1px solid #ccc;">{d.get('teacher', '')}</td>
            </tr>
            <tr>
                <th style="background-color: #f2f4f8; border:1px solid #ccc; text-align:center;">単元名</th>
                <td colspan="3" style="border:1px solid #ccc;"><strong>{d.get('unit_title', '')}</strong> （全 {d.get('total_hours', 5)} 時間）</td>
            </tr>
            <tr>
                <th style="background-color: #f2f4f8; border:1px solid #ccc; text-align:center;">単元の目標</th>
                <td colspan="3" style="border:1px solid #ccc; white-space:pre-wrap;">{d.get('unit_goal', '')}</td>
            </tr>
            <tr>
                <th style="background-color: #f2f4f8; border:1px solid #ccc; text-align:center;">生徒の実態</th>
                <td colspan="3" style="border:1px solid #ccc; white-space:pre-wrap;">{d.get('student_status', '')}</td>
            </tr>
            <tr>
                <th style="background-color: #f2f4f8; border:1px solid #ccc; text-align:center;">指導上の工夫</th>
                <td colspan="3" style="border:1px solid #ccc; white-space:pre-wrap;">{d.get('teaching_ideas', '')}</td>
            </tr>
            <tr>
                <th style="background-color: #f2f4f8; border:1px solid #ccc; text-align:center;">見方・考え方</th>
                <td colspan="3" style="border:1px solid #ccc; white-space:pre-wrap;">{d.get('viewpoint', '')}</td>
            </tr>
        </table>

        <h3 style="background-color: #2b5797; color: white; padding: 6px 10px; margin-bottom: 8px; font-size: 14px; border-radius: 4px;">🧩 三松メソッド（学習プロセスの構造化）</h3>
        <table style="width:100%; border-collapse: collapse; margin-bottom: 15px; border: 1px solid #ccc;" cellpadding="6">
            <tr style="background-color: #e8eef7; text-align:center;">
                <th style="width:25%; border:1px solid #ccc;">① つかむ</th>
                <th style="width:25%; border:1px solid #ccc;">② 考える</th>
                <th style="width:25%; border:1px solid #ccc;">③ 学び合う</th>
                <th style="width:25%; border:1px solid #ccc;">④ まとめる・振り返る</th>
            </tr>
            <tr>
                <td style="vertical-align:top; border:1px solid #ccc; height:70px; white-space:pre-wrap;">{d.get('tsukamu', '')}</td>
                <td style="vertical-align:top; border:1px solid #ccc; height:70px; white-space:pre-wrap;">{d.get('kangaeru', '')}</td>
                <td style="vertical-align:top; border:1px solid #ccc; height:70px; white-space:pre-wrap;">{d.get('manabi', '')}</td>
                <td style="vertical-align:top; border:1px solid #ccc; height:70px; white-space:pre-wrap;">{d.get('matomeru', '')}</td>
            </tr>
        </table>

        <h3 style="background-color: #2b5797; color: white; padding: 6px 10px; margin-bottom: 8px; font-size: 14px; border-radius: 4px;">📅 単元展開計画</h3>
        <table style="width:100%; border-collapse: collapse; border: 1px solid #ccc;" cellpadding="6">
            <thead>
                <tr style="background-color: #f2f4f8; text-align:center;">
                    <th style="width:12%; border:1px solid #ccc;">時間</th>
                    <th style="width:40%; border:1px solid #ccc;">学習内容・主な活動</th>
                    <th style="width:23%; border:1px solid #ccc;">思考スキル</th>
                    <th style="width:25%; border:1px solid #ccc;">評価規準・方法</th>
                </tr>
            </thead>
            <tbody>
                {hours_rows if hours_rows else '<tr><td colspan="4" style="text-align:center; color:#888; border:1px solid #ccc;">基本情報の入力完了後、時間ごとの計画を入力できます</td></tr>'}
            </tbody>
        </table>
    </div>
    """

  # 画面にHTMLとして直接レンダリング
  st.html(html_preview)
