"""
プロンプト最適化のバックエンドロジック

このモジュールはVertex AIのPrompt Optimizerを使用して、
ユーザーが入力したプロンプトを最適化する機能を提供する。
最適化結果はストリーミング形式で段階的に返される。
"""
import vertexai
from typing import Generator, Dict, Any
from google import genai
from google.genai import types
import os

class PromptOptimizer:
    """
    Vertex AI Prompt Optimizerのラッパークラス
    
    プロンプトの最適化をストリーミング形式で実行し、
    元のプロンプト、最適化されたプロンプト、改善提案を
    段階的に返す機能を提供する。
    
    Attributes:
        project_id (str): Google CloudのプロジェクトID
        location (str): Vertex AIのリージョン
        client (vertexai.Client): Vertex AIのクライアントインスタンス
    """
    # PromptOptimizerの初期化
    def __init__(self, project_id: str, location: str = "us-central1"):
        # 共通
        self.project_id = project_id
        self.location = location

        # Optimizer用 クライアント
        self.client = vertexai.Client(project=project_id, location=location)
    
        # 翻訳用
        self.genai = genai.Client(
            vertexai=True,
            project=project_id,
            location=location
        )        

    # 英語テキストを日本語に翻訳する
    def translate_to_japanese(self, text: str) -> str:
        # Gemini APIを呼び出して翻訳実行
        try:
            response = self.genai.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=f"以下の英語を自然な日本語に翻訳してください。翻訳結果のみを出力:\n\n{text}"
            )
            # strip()で前後の空白・改行を削除して整形
            return response.text.strip()

        # エラー時は元のテキストを返す    
        except Exception as e:
            return text  

    # プロンプトを最適化し、結果をストリーミング形式で返す
    def optimize_prompt_stream(self, prompt: str) -> Generator[Dict[str, Any], None, None]:
        """
        プロンプトを最適化し、結果をストリーミング形式で返す
        
        Args:
            prompt: 最適化するプロンプト
            
        Yields:
            dict: ストリーミングデータ
        """
        # 処理開始を通知
        yield {
            "type": "status",
            "message": "プロンプト最適化を開始します..."
        }
        
        # プロンプトの分析と最適化を実行
        try:
            response = self.client.prompt_optimizer.optimize_prompt(prompt=prompt)

            # parsed_responseには最適化結果が構造化されて格納
            parsed = response.parsed_response
            
            # 元のプロンプトを送信
            yield {
                "type": "original_prompt",
                "content": parsed.original_prompt
            }
            
            # 最適化されたプロンプトをクライアントに返す
            yield {
                "type": "suggested_prompt",
                "content": parsed.suggested_prompt
            }
            
            # 個別の改善提案を1つずつクライアントに返す
            for i, guideline in enumerate(parsed.applicable_guidelines, 1):
                # 英語の理由を日本語に翻訳
                improvement_ja = self.translate_to_japanese(guideline.suggested_improvement)

                # 改善提案を送信
                yield {
                    "type": "guideline",
                    "index": i,
                    "name": guideline.applicable_guideline,
                    "improvement": improvement_ja,
                    "before": guideline.text_before_change,
                    "after": guideline.text_after_change
                }
            
            # 処理完了をクライアントに通知
            yield {
                "type": "status",
                "message": "最適化が完了しました"
            }

        # エラー発生時はエラー情報をクライアントに返す    
        except Exception as e:
            yield {
                "type": "error",
                "message": f"エラーが発生しました: {str(e)}"
            }