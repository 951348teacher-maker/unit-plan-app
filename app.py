import streamlit as st
import streamlit.components.v1 as components
import json

# 1. ページ基本設定
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

# 質問定義
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

st.title("📝 授業計画シート作成アプリ（三松メソッド対応）")

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
    st.download_button("💾 作業データを保存(JSON)", data=json_str, file_name="lesson_plan.json", mime="application/json")
    
    uploaded_file = st.file_uploader("📂 保存データを読み込んで再開", type=["json"])
    if uploaded_file is not None:
        try:
            loaded_state = json.load(uploaded_file)
            st.session_state.step = loaded_state.get("step", 0)
            st.session_state.data = loaded_state.get("data", {"unit_plan": [], "matsumatsu": {}})
            st.session_state.chat_history = loaded_state.get("chat_history", [])
            st.session_state.hours_done = loaded_state.get("hours_done", 0)
            st.session_state.matsumatsu_step = loaded_state.get("matsumatsu_step", 0)
            st.success("読み込み完了！")
            st.rerun()
        except Exception:
            st.error("ファイルの読み込みに失敗しました。")

    st.divider()
    if st.button("🔄 最初からやり直す"):
        st.session_state.clear()
        st.rerun()

# メインレイアウト（対話画面と確認画面）
col_chat, col_preview = st.columns([1, 1])

with col_chat:
    st.subheader("💬 チャット対話エリア")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    step = st.session_state.step
    if step < len(QUESTIONS):
        q = QUESTIONS[step]
        with st.form(key=f"form_step_{step}", clear_on_submit=True):
            if q["type"] == "text":
                val = st.text_input(q["label"])
            elif q["type"] == "textarea":
                val = st.text_area(q["label"])
            elif q["type"] == "number":
                val = st.number_input(q["label"], min_value=1, max_value=20, value=5)
            
            if st.form_submit_button("回答を送信") and val:
                st.session_state.data[q["key"]] = val
                st.session_state.chat_history.append({"role": "user", "content": str(val)})
                st.session_state.step += 1
                if st.session_state.step < len(QUESTIONS):
                    st.session_state.chat_history.append({"role": "assistant", "content": QUESTIONS[st.session_state.step]["prompt"]})
                st.rerun()

with col_preview:
    st.subheader("📋 入力内容の確認")
    d = st.session_state.data
    st.markdown(f"**教科名**: {d.get('subject', '未入力')}")
    st.markdown(f"**授業者**: {d.get('teacher', '未入力')}")
    st.markdown(f"**単元名**: {d.get('unit_title', '未入力')}")
    st.markdown(f"**単元の目標**: {d.get('unit_goal', '未入力')}")
    st.markdown(f"**生徒の実態**: {d.get('student_status', '未入力')}")
    st.markdown(f"**指導上の工夫**: {d.get('teaching_ideas', '未入力')}")
    st.markdown(f"**教科の見方・考え方**: {d.get('viewpoint', '未入力')}")
    st.markdown(f"**総時間数**: {d.get('total_hours', '未入力')}")
