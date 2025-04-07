# LangGraph Slide Generator ドキュメント

## プロジェクト概要

LangGraph Slide Generatorは、画像から構造化されたHTMLスライドを生成するシステムです。このシステムは、LangGraphとLLM（大規模言語モデル）を活用して、教科書ページの画像を解析し、構造化されたHTMLスライドに変換します。

## 目的

本システムの主な目的は以下の通りです：

- 教科書やテキスト画像からHTMLスライドを自動生成する
- 日本語テキストと数式を正確に抽出・変換する
- 元の文書の構造を保持した高品質なスライドを作成する

## ドキュメント構成

1. **[基本設計](./01-basic-design.md)**: システム全体の概要と基本設計
2. **[要件定義](./02-requirements.md)**: 機能要件と非機能要件
3. **[アーキテクチャ](./03-architecture.md)**: システムアーキテクチャと構成要素
4. **[画像処理](./04-image-processing.md)**: 画像解析と前処理
5. **[LLM連携](./05-llm-integration.md)**: LLMを用いたコンテンツ解析
6. **[HTML生成](./06-html-generation.md)**: HTMLスライド生成プロセス
7. **[API設計](./07-api-design.md)**: API仕様
8. **[開発ガイド](./08-development-guide.md)**: 開発者向けガイド

## 関連資料

- LangGraph ドキュメント: [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- MathJax ドキュメント: [MathJax Documentation](https://docs.mathjax.org/)
