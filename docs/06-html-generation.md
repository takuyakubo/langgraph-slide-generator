# HTML生成

## 概要

HTML生成コンポーネントは、画像から抽出され、LLMによって分析・構造化されたコンテンツを、整形されたHTMLスライドに変換する役割を担います。このドキュメントでは、元のコンテンツの構造、スタイル、意味を正確に表現するHTMLスライドを生成するためのアプローチ、技術、考慮事項について説明します。

## 生成プロセス

HTMLスライド生成の一般的なプロセスは以下の通りです：

1. **コンテンツ構造化**
   - 分析されたコンテンツを論理的なスライド単位に整理
   - 見出し階層とセクション境界の決定
   - 関連するコンテンツ要素のグループ化

2. **HTMLテンプレート選択**
   - コンテンツタイプに基づく適切なスライドテンプレートの選択
   - 基本スタイリングとレイアウト構造の適用

3. **コンテンツ変換**
   - 構造化されたコンテンツのHTML要素への変換
   - 特殊要素（数式、リスト、表など）の処理
   - 適切なセマンティックHTMLタグの適用

4. **スタイル適用**
   - 元のコンテンツの表示に合わせたCSSスタイルの適用
   - レスポンシブデザイン原則の実装
   - スライド間での一貫した視覚テーマの作成

5. **検証と最適化**
   - 標準準拠のためのHTML検証
   - パフォーマンスとアクセシビリティのための最適化
   - クロスブラウザ互換性の確認

## HTML構造

### 基本スライド構造

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>スライドタイトル</title>
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
    <!-- 追加のヘッダー要素 -->
</head>
<body>
    <!-- スライドコンテナ -->
    <div class="slide-deck">
        <!-- 個別スライド -->
        <div class="slide">
            <div class="slide-header">
                <h1>スライドタイトル</h1>
            </div>
            <div class="slide-content">
                <!-- コンテンツ要素 -->
            </div>
            <div class="slide-footer">
                <!-- フッター情報 -->
            </div>
        </div>
        <!-- 追加のスライド -->
    </div>
    
    <!-- ナビゲーションコントロール -->
    <div class="slide-navigation">
        <button class="prev-slide">前へ</button>
        <span class="slide-counter">1 / 10</span>
        <button class="next-slide">次へ</button>
    </div>
    
    <script src="slide-controls.js"></script>
</body>
</html>
```

### スライドコンテナ

```html
<div class="slide">
    <div class="slide-header">
        <h1>スライドタイトル</h1>
        <p class="subtitle">サブタイトルまたはコンテキスト</p>
    </div>
    <div class="slide-content">
        <!-- コンテンツ要素 -->
    </div>
</div>
```

### コンテンツ要素

#### 見出し

```html
<h2>主見出し</h2>
<h3>副見出し</h3>
```

#### 段落

```html
<p>通常の段落テキスト内容...</p>
<p class="highlight">ハイライトされた段落内容...</p>
```

#### リスト

```html
<ul>
    <li>箇条書き項目</li>
    <li>別の箇条書き項目</li>
</ul>

<ol>
    <li>番号付き項目</li>
    <li>別の番号付き項目</li>
</ol>
```

#### ノートとコールアウト

```html
<div class="note">
    <p>重要なノート内容...</p>
</div>

<div class="key-point">
    <p>重要な概念やアイデア...</p>
</div>
```

#### 数式表現

```html
<div class="equation">
    <span class="math">$$\mathcal{D}_S \neq \mathcal{D}_T$$</span>
</div>

<p>インライン数式の例：<span class="math">$P^T_{X,Y} \neq P^S_{X,Y}$</span></p>
```

### スライドタイプ

#### 表紙スライド

```html
<div class="slide cover-slide">
    <div class="slide-content centered">
        <h1>文書タイトル</h1>
        <p class="subtitle">サブタイトルまたは著者情報</p>
        <div class="date-info">2025年4月7日</div>
    </div>
</div>
```

#### 目次スライド

```html
<div class="slide toc-slide">
    <h1>目次</h1>
    <ol class="toc-list">
        <li><a href="#slide3">第1章: はじめに</a></li>
        <li><a href="#slide5">第2章: 基本概念</a></li>
        <li><a href="#slide12">第3章: 応用例</a></li>
        <li><a href="#slide18">第4章: まとめ</a></li>
    </ol>
</div>
```

#### 区切りスライド

```html
<div class="slide divider-slide">
    <div class="centered">
        <h1>第2章</h1>
        <h2>基本概念</h2>
    </div>
</div>
```

## CSS設計

### 基本レイアウト

```css
body {
    font-family: 'Helvetica Neue', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
    margin: 0;
    padding: 0;
    overflow: hidden;
}

.slide-deck {
    width: 100%;
    height: 100vh;
    position: relative;
}

.slide {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    display: flex;
    flex-direction: column;
    padding: 40px;
    box-sizing: border-box;
    background-color: #fff;
    transition: transform 0.5s ease;
}

.slide-header {
    margin-bottom: 20px;
}

.slide-content {
    flex: 1;
    overflow-y: auto;
}

.slide-footer {
    margin-top: 20px;
    font-size: 0.8rem;
    color: #666;
}
```

### 日本語タイポグラフィ

```css
/* 日本語フォント設定 */
.ja-mincho {
    font-family: 'Hiragino Mincho ProN', 'Yu Mincho', serif;
}

.ja-gothic {
    font-family: 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
}

/* 縦書きテキスト */
.vertical-text {
    writing-mode: vertical-rl;
    text-orientation: mixed;
    height: 100%;
}

/* 行間と文字間隔 */
p, li {
    line-height: 1.7;
    letter-spacing: 0.03em;
}

/* 見出しスタイル */
h1, h2, h3, h4, h5, h6 {
    line-height: 1.4;
    margin-top: 0.8em;
    margin-bottom: 0.5em;
}
```

### レスポンシブデザイン

```css
/* 基本レスポンシブ設定 */
@media (max-width: 768px) {
    .slide {
        padding: 20px;
    }
    
    h1 {
        font-size: 1.8rem;
    }
    
    h2 {
        font-size: 1.5rem;
    }
    
    .two-col {
        flex-direction: column;
    }
    
    .col {
        width: 100%;
        margin-bottom: 20px;
    }
}

/* 印刷用スタイル */
@media print {
    .slide {
        page-break-after: always;
        position: relative;
        height: auto;
        min-height: 100vh;
    }
    
    .slide-navigation {
        display: none;
    }
}
```

## 数式処理

### MathJax初期化

```html
<script>
    MathJax = {
        tex: {
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']]
        },
        svg: {
            fontCache: 'global'
        },
        startup: {
            typeset: true
        }
    };
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
```

### 数式スタイリング

```css
.equation {
    display: block;
    text-align: center;
    margin: 1.5em 0;
    overflow-x: auto;
}

.math {
    font-style: italic;
}

.mjx-chtml {
    display: inline-block;
    line-height: 0;
    text-indent: 0;
    text-align: left;
    text-transform: none;
    font-style: normal;
    font-weight: normal;
    font-size: 100%;
    font-size-adjust: none;
    letter-spacing: normal;
    word-wrap: normal;
    direction: ltr;
}
```

## スライド生成の実装

### テンプレートエンジンアプローチ

HTML生成モジュールはJinja2テンプレートエンジンを使用してスライドを構築します：

```
コンテンツ構造 → テンプレート選択 → 変数マッピング → テンプレートレンダリング → HTML出力
```

### テンプレート例

#### 基本スライドテンプレート

```html
{# base_slide.html #}
<div class="slide {{ slide_type }}">
    {% if title %}
    <div class="slide-header">
        <h1>{{ title }}</h1>
        {% if subtitle %}<p class="subtitle">{{ subtitle }}</p>{% endif %}
    </div>
    {% endif %}
    
    <div class="slide-content">
        {% block content %}{% endblock %}
    </div>
    
    {% if footer %}
    <div class="slide-footer">
        {{ footer }}
    </div>
    {% endif %}
</div>
```

#### コンテンツスライドテンプレート

```html
{# content_slide.html #}
{% extends "base_slide.html" %}

{% block content %}
    {% for element in content_elements %}
        {% if element.type == 'heading' %}
            <h{{ element.level }}>{{ element.content }}</h{{ element.level }}>
        {% elif element.type == 'paragraph' %}
            <p{% if element.highlight %} class="highlight"{% endif %}>{{ element.content }}</p>
        {% elif element.type == 'list' %}
            {% if element.ordered %}
                <ol>
                    {% for item in element.items %}
                        <li>{{ item }}</li>
                    {% endfor %}
                </ol>
            {% else %}
                <ul>
                    {% for item in element.items %}
                        <li>{{ item }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% elif element.type == 'equation' %}
            <div class="equation">
                <span class="math">$${{ element.content }}$$</span>
            </div>
        {% elif element.type == 'note' %}
            <div class="note">
                <p>{{ element.content }}</p>
            </div>
        {% endif %}
    {% endfor %}
{% endblock %}
```

## スライド分割アルゴリズム

### 分割戦略

HTML生成モジュールは、様々な戦略に基づいてコンテンツをスライドに分割します：

1. **見出しベース分割**
   - 主要な見出し（h2レベル）ごとに新しいスライドを作成
   - 長いセクションは複数のスライドに分割

2. **コンテンツ量ベース分割**
   - スライドあたりの最適なコンテンツ量に基づいて分割
   - テキスト量、リスト項目数、図表の存在を考慮

3. **論理構造ベース分割**
   - 論理的に関連するコンテンツのグループ化
   - 概念的な区切りに基づく分割

### 実装アプローチ

```
1. コンテンツブロックの重み付け計算
2. ブレークポイント候補の特定
3. 最適なブレークポイントの選択
4. スライド構造の生成
```

## インタラクティブ機能

### ナビゲーション

スライドには基本的なナビゲーション機能が含まれます：

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    const prevButton = document.querySelector('.prev-slide');
    const nextButton = document.querySelector('.next-slide');
    const counter = document.querySelector('.slide-counter');
    
    let currentSlide = 0;
    
    function updateSlides() {
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.style.display = 'flex';
            } else {
                slide.style.display = 'none';
            }
        });
        
        counter.textContent = `${currentSlide + 1} / ${slides.length}`;
        
        prevButton.disabled = currentSlide === 0;
        nextButton.disabled = currentSlide === slides.length - 1;
    }
    
    prevButton.addEventListener('click', function() {
        if (currentSlide > 0) {
            currentSlide--;
            updateSlides();
        }
    });
    
    nextButton.addEventListener('click', function() {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            updateSlides();
        }
    });
    
    // キーボードナビゲーション
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            prevButton.click();
        } else if (e.key === 'ArrowRight') {
            nextButton.click();
        }
    });
    
    // 初期表示
    updateSlides();
});
```

### アクセシビリティ

スライドのアクセシビリティを確保するための実装：

```html
<!-- アクセシビリティ強化 -->
<div class="slide" role="region" aria-label="スライド 1" tabindex="0">
    <div class="slide-header">
        <h1 id="slide1-title">スライドタイトル</h1>
    </div>
    <div class="slide-content" aria-labelledby="slide1-title">
        <!-- アクセシブルなコンテンツ要素 -->
        <img src="diagram.png" alt="プロセスフロー図：入力から出力までの5段階" />
    </div>
</div>

<!-- スクリーンリーダー向け情報 -->
<div class="sr-only">
    プレゼンテーションには合計10枚のスライドがあります。左右の矢印キーで移動できます。
</div>
```

## 品質保証

### 検証基準

- HTML構造の正確性と標準準拠
- 元のコンテンツとの視覚的な一致度
- 数式表示の正確さ
- 様々な画面サイズでのレスポンシブ性
- スライド間の一貫性

### テストアプローチ

- 自動HTMLバリデーション
- 元のコンテンツとの視覚的比較
- クロスブラウザ互換性テスト
- 様々なデバイスでのレスポンシブデザインテスト
- 数式表示の検証

## HTML生成ベストプラクティス

1. **セマンティックHTML**
   - 意味を伝える適切なHTML5要素の使用
   - アクセシビリティのためのARIA属性の適用
   - 論理的な文書構造の維持

2. **最適化**
   - 効率的なCSSセレクタの使用
   - 画像の適切な最適化
   - 必要最小限のJavaScriptの使用

3. **一貫性**
   - 一貫したクラス命名規則
   - 統一されたスタイリングアプローチ
   - 再利用可能なコンポーネント定義

4. **カスタマイズ可能性**
   - テーマ切り替えの容易さ
   - 必要に応じたスタイル調整の仕組み
   - モジュール化されたCSSの提供
