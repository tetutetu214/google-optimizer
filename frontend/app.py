"""
Streamlitフロントエンド

Vertex AI Prompt Optimizerを使用したプロンプト最適化ツールのUI。
ユーザーはファイルアップロードまたは直接入力でプロンプトを入力し、
最適化結果をストリーミング形式でリアルタイムに確認できる。
"""
import streamlit as st
import sys
from pathlib import Path
import time
from dotenv import load_dotenv
import os

#  .envファイルから環境変数を読み込み
load_dotenv()

# 親ディレクトリのbackendモジュールをインポートパスに追加
sys.path.append(str(Path(__file__).parent.parent))
from backend.optimizer import PromptOptimizer


# ページ設定
# Streamlitアプリケーションの基本設定を定義
st.set_page_config(
    page_title="プロンプト最適化ツール",
    layout="wide"
)

# 初期化
if 'is_optimizing' not in st.session_state:
    st.session_state.is_optimizing = False
if 'optimization_result' not in st.session_state:
    st.session_state.optimization_result = None
if 'guidelines_data' not in st.session_state:
    st.session_state.guidelines_data = []

# タイトル
st.title("Prompt Optimizer API プロンプト最適化提案ツール")
st.markdown("---")

# サイドバー設定
with st.sidebar:
    st.header("設定")
    project_id = st.text_input(
        "Google Cloud Project ID",
        value=os.getenv("PROJECT_ID", ""),
        help="Vertex AIを使用するプロジェクトID"
    )
    location = st.text_input(
        "Location",
        value=os.getenv("LOCATION", ""),
        help="Vertex AIのリージョン"
    )

# メインコンテンツ
# 画面を左右2カラムに分割（入力部と出力部）
col1, col2 = st.columns([1, 1])

with col1:
    st.header("プロンプト入力")
    
    # ファイルアップロード or テキスト入力
    input_method = st.radio(
        "入力方法",
        ["ファイルアップロード", "直接入力"],
        horizontal=True
    )
    
    prompt_text = ""
    
    if input_method == "ファイルアップロード":
        uploaded_file = st.file_uploader(
            "プロンプトファイルを選択",
            type=["txt", "md"],
            help="テキストファイルまたはMarkdownファイルをアップロード"
        )
        
        if uploaded_file:
            prompt_text = uploaded_file.read().decode("utf-8")
            st.text_area(
                "ファイル内容",
                value=prompt_text,
                height=300,
                disabled=True
            )
    else:
        prompt_text = st.text_area(
            "プロンプトを入力",
            height=300,
            placeholder="最適化したいプロンプトを入力してください..."
        )

    optimize_button = st.button(
        "Prompt Optimizer API による最適化実行",
        type="primary",
        use_container_width=True,
        disabled=not prompt_text or st.session_state.is_optimizing
    )

with col2:
    st.header("プロンプト出力")
    
    # ストリーミング表示時にこれらのプレースホルダーに順次コンテンツを表示
    status_placeholder = st.empty()
    suggested_placeholder = st.empty()
    guidelines_placeholder = st.empty()

# 最適化実行
if optimize_button and prompt_text:
    try:
        # 実行開始でボタンを無効化
        st.session_state.is_optimizing = True
        st.session_state.optimization_result = None
        st.session_state.guidelines_data = []

        # オプティマイザー初期化
        optimizer = PromptOptimizer(project_id, location)
        
        # ストリーミング表示
        guidelines_data = []
        suggested_prompt_content = None        

        # ストリーミング処理のメインループ
        # optimize_prompt_streamから順次データを受け取り、リアルタイムで表示        
        for data in optimizer.optimize_prompt_stream(prompt_text):

            # ステータスメッセージの表示
            # 「最適化を開始します」「完了しました」などの進行状況を表示            
            if data["type"] == "status":
                with status_placeholder:
                    st.info(data["message"])
                time.sleep(0.5)

            # 最適化されたプロンプトの表示
            # Vertex AIが生成した改善版プロンプトを表示
            # elif data["type"] == "suggested_prompt":
            #     with suggested_placeholder.container():
            #         st.subheader("最適化されたプロンプト")
            #         st.code(data["content"], language="text")
                    # # ダウンロードボタン
                    # st.download_button(
                    #     label="最適化プロンプトをダウンロード",
                    #     data=data["content"],
                    #     file_name="optimized_prompt.txt",
                    #     mime="text/plain"
                    # )

            elif data["type"] == "suggested_prompt":
                st.session_state.optimization_result = data["content"]
                

            # 改善提案の表示
            # 個別の改善ポイントを段階的に表示            
            # elif data["type"] == "guideline":
            #     # データを追加
            #     guidelines_data.append(data)
                
            #     # 改善提案セクションを表示
            #     with guidelines_placeholder.container():
            #         st.subheader("改善提案")

            #         # 蓄積された全ての改善提案を順次表示
            #         # 新しい提案が来るたびに全体を再描画                    
            #         for guideline in guidelines_data:
            #             with st.expander(
            #                 f"改善点 {guideline['index']}: {guideline['name']}",
            #                 expanded=True
            #             ):
            #                 # 改善理由を表示
            #                 st.markdown(f"**理由:** {guideline['improvement']}")
                            
            #                 # 変更前後を2カラムで並べて表示
            #                 col_before, col_after = st.columns(2)
                            
            #                 # 左カラム: 変更前
            #                 with col_before:
            #                     st.markdown("**変更前:**")
            #                     st.code(guideline['before'], language="text")
                            
            #                 # 右カラム: 変更後
            #                 with col_after:
            #                     st.markdown("**変更後:**")
            #                     st.code(guideline['after'], language="text")

                # # ストリーミング効果を演出
                # time.sleep(0.3)

            elif data["type"] == "guideline":
                st.session_state.guidelines_data.append(data)
                
            
            # エラー発生時の表示
            elif data["type"] == "error":
                with status_placeholder:
                    st.error(data["message"])
        
        # 完了後、ステータスをクリア
        time.sleep(1)
        status_placeholder.empty()

    # 予期しないエラーが発生した場合     
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")

    finally:
        # 実行終了: ボタンを再有効化
        st.session_state.is_optimizing = False

# Vertex AIが生成した改善版プロンプトを表示
if st.session_state.optimization_result:
    with suggested_placeholder.container():
        st.subheader("最適化されたプロンプト")
        st.code(st.session_state.optimization_result, language="text")

        # ダウンロードボタン
        st.download_button(
            label="📥 最適化プロンプトをダウンロード",
            data=st.session_state.optimization_result,
            file_name="optimized_prompt.txt",
            mime="text/plain"
        )

# 改善提案セクションを表示
if st.session_state.guidelines_data:

    # 改善提案セクションを表示
    with guidelines_placeholder.container():
        st.subheader("改善提案")

        # 蓄積された全ての改善提案を順次表示
        # 新しい提案が来るたびに全体を再描画
        for guideline in st.session_state.guidelines_data:
            with st.expander(
                f"改善点 {guideline['index']}: {guideline['name']}",
                expanded=True
            ):
                # 改善理由を表示
                st.markdown(f"**理由:** {guideline['improvement']}")
                
                # 変更前後を2カラムで並べて表示
                col_before, col_after = st.columns(2)
                with col_before:
                    st.markdown("**変更前:**")
                    st.code(guideline['before'], language="text")
                with col_after:
                    st.markdown("**変更後:**")
                    st.code(guideline['after'], language="text")