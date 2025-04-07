# API設計

## 概要

LangGraph Slide GeneratorのAPIは、システムの画像分析とHTMLスライド生成機能へのプログラマティックなアクセスを提供します。このドキュメントでは、利用可能なエンドポイント、リクエスト/レスポンス形式、および使用例について概説します。

## 基本情報

### ベースURL

```
https://api.langgraph-slide-generator.example.com/v1
```

### 認証

すべてのAPIリクエストには、リクエストヘッダーで提供されるAPIキーを使用した認証が必要です：

```
Authorization: Bearer YOUR_API_KEY
```

### レスポンス形式

すべてのAPIレスポンスはJSON形式で返されます。正常なレスポンスとエラーレスポンスは標準形式に従います：

**成功レスポンス**:
```json
{
  "status": "success",
  "data": {
    // レスポンスデータ
  }
}
```

**エラーレスポンス**:
```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "エラーの詳細説明",
    "details": {
      // 追加のエラー情報（該当する場合）
    }
  }
}
```

## エンドポイント

### 1. 画像処理

**エンドポイント**: `/process`

**メソッド**: POST

**説明**: 処理とHTMLスライド生成のための画像を送信します

**リクエストパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|------|-------------|
| images | array | 画像ファイルまたはURLの配列 |
| options | object | 処理オプション（オプション） |

**オプションオブジェクト**:

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| language | string | "ja" | コンテンツの主要言語（"ja"は日本語） |
| template | string | "default" | 使用するHTMLテンプレートスタイル |
| includeEquations | boolean | true | 数式を処理するかどうか |
| slideBreakStrategy | string | "auto" | スライド区切りを決定する戦略（"auto", "heading", "page"） |

**リクエスト例**:

```json
{
  "images": [
    "https://example.com/textbook/page1.jpg",
    "https://example.com/textbook/page2.jpg"
  ],
  "options": {
    "language": "ja",
    "template": "academic",
    "includeEquations": true,
    "slideBreakStrategy": "heading"
  }
}
```

**レスポンス**:

```json
{
  "status": "success",
  "data": {
    "job_id": "j-12345abcde",
    "status": "processing",
    "estimated_completion_time": "2025-04-07T06:25:30Z"
  }
}
```

### 2. ジョブステータス確認

**エンドポイント**: `/jobs/{job_id}`

**メソッド**: GET

**説明**: 処理ジョブのステータスを確認します

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|------|-------------|
| job_id | string | 処理エンドポイントから返されたジョブID |

**レスポンス例**:

```json
{
  "status": "success",
  "data": {
    "job_id": "j-12345abcde",
    "status": "completed",
    "progress": 100,
    "created_at": "2025-04-07T06:20:30Z",
    "completed_at": "2025-04-07T06:23:45Z",
    "result_url": "https://api.langgraph-slide-generator.example.com/v1/results/j-12345abcde"
  }
}
```

可能なステータス値:
- `queued`: ジョブは処理キューにあります
- `processing`: ジョブは現在処理中です
- `completed`: ジョブは正常に完了しました
- `failed`: ジョブは失敗しました

### 3. 結果取得

**エンドポイント**: `/results/{job_id}`

**メソッド**: GET

**説明**: 完了したジョブの結果を取得します

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|------|-------------|
| job_id | string | 処理エンドポイントから返されたジョブID |

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|---------|-------------|
| format | string | "html" | 結果フォーマット（"html", "json"） |

**レスポンス例（format=html）**:

```json
{
  "status": "success",
  "data": {
    "job_id": "j-12345abcde",
    "html": "<!DOCTYPE html>\n<html lang=\"ja\">\n<head>...\n",
    "slide_count": 5,
    "download_url": "https://api.langgraph-slide-generator.example.com/v1/download/j-12345abcde"
  }
}
```

**レスポンス例（format=json）**:

```json
{
  "status": "success",
  "data": {
    "job_id": "j-12345abcde",
    "slides": [
      {
        "title": "転移学習（Transfer Learning）",
        "subtitle": "機械学習プロフェッショナルシリーズ",
        "type": "cover",
        "content": "<div class=\"slide-title\">...\n"
      },
      {
        "title": "本日の内容",
        "type": "toc",
        "content": "<h2>本日の内容</h2>...\n"
      },
      // 追加のスライド...
    ],
    "metadata": {
      "source_images": 2,
      "processing_time": 3.25,
      "language": "ja",
      "template": "academic"
    }
  }
}
```

### 4. HTMLパッケージのダウンロード

**エンドポイント**: `/download/{job_id}`

**メソッド**: GET

**説明**: 完全なHTMLパッケージ（CSSとJavaScriptを含む）をZIPファイルとしてダウンロードします

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|------|-------------|
| job_id | string | 処理エンドポイントから返されたジョブID |

**レスポンス**:

ZIPファイルとして完全なHTMLパッケージが返されます。

### 5. ジョブ一覧取得

**エンドポイント**: `/jobs`

**メソッド**: GET

**説明**: 認証されたユーザーのすべての処理ジョブを一覧表示します

**クエリパラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|---------|-------------|
| status | string | null | ステータスでフィルタリング（"queued", "processing", "completed", "failed"） |
| limit | integer | 20 | 返すジョブの最大数 |
| offset | integer | 0 | ページネーションのためのオフセット |

**レスポンス例**:

```json
{
  "status": "success",
  "data": {
    "jobs": [
      {
        "job_id": "j-12345abcde",
        "status": "completed",
        "created_at": "2025-04-07T06:20:30Z",
        "completed_at": "2025-04-07T06:23:45Z"
      },
      {
        "job_id": "j-67890fghij",
        "status": "processing",
        "created_at": "2025-04-07T06:30:15Z",
        "completed_at": null
      }
    ],
    "total": 2,
    "limit": 20,
    "offset": 0
  }
}
```

## エラー処理

すべてのAPIエンドポイントは標準的なHTTPステータスコードを返します。エラーレスポンスには追加の詳細を含むJSONオブジェクトが含まれます：

```json
{
  "status": "error",
  "error": {
    "code": "invalid_request",
    "message": "リクエストが無効です。リクエストパラメータを確認してください。",
    "details": {
      "images": "少なくとも1つの画像を提供する必要があります。"
    }
  }
}
```

一般的なエラーコード：

| コード | HTTPステータス | 説明 |
|------|-------------|-------------|
| `invalid_request` | 400 | リクエストが無効です |
| `unauthorized` | 401 | 認証に失敗しました |
| `forbidden` | 403 | アクセスが拒否されました |
| `not_found` | 404 | リソースが見つかりません |
| `rate_limit_exceeded` | 429 | レート制限を超えました |
| `internal_error` | 500 | 内部サーバーエラー |

## レート制限

APIリクエストはレート制限の対象となります。現在の制限は以下の通りです：

- `/process`エンドポイントに対して1分あたり10リクエスト
- 他のエンドポイントに対して1分あたり60リクエスト

レート制限情報はレスポンスヘッダーに含まれています：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1617783600
```

## ウェブフック（イベント通知）

長時間実行されるジョブのステータス更新を受信するために、ウェブフックを設定できます。

**エンドポイント**: `/webhooks`

**メソッド**: POST

**説明**: ジョブステータス変更の通知を受け取るウェブフックを登録します

**リクエストパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|------|-------------|
| callback_url | string | ステータス更新を送信するURLエンドポイント |
| events | array | 通知を受け取るイベントタイプの配列（"job.completed", "job.failed"など） |
| secret | string | ウェブフック通知の署名に使用される共有シークレット |

**リクエスト例**:

```json
{
  "callback_url": "https://your-app.example.com/api/webhooks/slide-generator",
  "events": ["job.queued", "job.processing", "job.completed", "job.failed"],
  "secret": "your_webhook_secret"
}
```

**レスポンス**:

```json
{
  "status": "success",
  "data": {
    "webhook_id": "wh-abcdef123456",
    "callback_url": "https://your-app.example.com/api/webhooks/slide-generator",
    "events": ["job.queued", "job.processing", "job.completed", "job.failed"],
    "created_at": "2025-04-07T06:30:00Z"
  }
}
```

**ウェブフック通知の例**:

ジョブステータスが変更されると、登録されたコールバックURLに以下のようなペイロードが送信されます：

```json
{
  "event": "job.completed",
  "job_id": "j-12345abcde",
  "status": "completed",
  "timestamp": "2025-04-07T06:23:45Z",
  "data": {
    "slide_count": 5,
    "processing_time": 183.2,
    "result_url": "https://api.langgraph-slide-generator.example.com/v1/results/j-12345abcde"
  }
}
```

## API実装

### APIルーティング

FastAPIを使用したAPIルーティングの構成例：

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="LangGraph Slide Generator API")

# 認証
API_KEY_HEADER = APIKeyHeader(name="Authorization")

# ルート
@app.post("/v1/process")
async def process_images(
    request: ProcessRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(API_KEY_HEADER)
):
    # APIキー検証
    validate_api_key(api_key)
    
    # ジョブの作成と処理
    job_id = create_job(request.images, request.options)
    background_tasks.add_task(process_job, job_id)
    
    return {
        "status": "success",
        "data": {
            "job_id": job_id,
            "status": "processing",
            "estimated_completion_time": estimate_completion_time(request.images)
        }
    }

@app.get("/v1/jobs/{job_id}")
async def get_job_status(job_id: str, api_key: str = Depends(API_KEY_HEADER)):
    # APIキー検証
    validate_api_key(api_key)
    
    # ジョブステータスの取得
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "status": "success",
        "data": job
    }

# 他のエンドポイント...
```

### 非同期ジョブ処理

APIリクエストを処理し、バックグラウンドでジョブを実行するための実装：

```python
import asyncio
from datetime import datetime
import uuid

# ジョブストレージ（実際の実装ではデータベースを使用）
jobs = {}

def create_job(images, options):
    """新しいジョブを作成してIDを返す"""
    job_id = f"j-{uuid.uuid4().hex[:10]}"
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "images": images,
        "options": options
    }
    
    return job_id

async def process_job(job_id):
    """バックグラウンドでジョブを処理"""
    try:
        job = jobs[job_id]
        job["status"] = "processing"
        
        # 画像処理とスライド生成のメイン処理フロー
        await process_images(job)
        generate_slides(job)
        create_html_package(job)
        
        # ジョブ完了の更新
        job["status"] = "completed"
        job["progress"] = 100
        job["completed_at"] = datetime.utcnow().isoformat()
        job["result_url"] = f"/v1/results/{job_id}"
        
        # ウェブフック通知を送信
        notify_webhooks(job_id, "job.completed")
    
    except Exception as e:
        # エラー処理
        job["status"] = "failed"
        job["error"] = str(e)
        
        # ウェブフック通知を送信
        notify_webhooks(job_id, "job.failed")
```

## API利用例

### Pythonクライアント例

```python
import requests
import json
import time

API_KEY = "your_api_key"
API_BASE = "https://api.langgraph-slide-generator.example.com/v1"

# 画像を処理
def process_images(image_urls, options=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "images": image_urls,
        "options": options or {}
    }
    
    response = requests.post(
        f"{API_BASE}/process",
        headers=headers,
        data=json.dumps(payload)
    )
    
    return response.json()["data"]

# ジョブステータスの確認
def check_job_status(job_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(
        f"{API_BASE}/jobs/{job_id}",
        headers=headers
    )
    
    return response.json()["data"]

# 結果の取得
def get_results(job_id, format="html"):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(
        f"{API_BASE}/results/{job_id}?format={format}",
        headers=headers
    )
    
    return response.json()["data"]

# ダウンロード
def download_html_package(job_id, output_path):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.get(
        f"{API_BASE}/download/{job_id}",
        headers=headers,
        stream=True
    )
    
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return output_path

# 使用例
if __name__ == "__main__":
    # 画像処理リクエスト
    result = process_images(
        ["https://example.com/textbook/page1.jpg"],
        {
            "template": "academic",
            "slideBreakStrategy": "heading"
        }
    )
    
    job_id = result["job_id"]
    print(f"Job ID: {job_id}")
    
    # ステータス確認とポーリング
    while True:
        status_data = check_job_status(job_id)
        print(f"Status: {status_data['status']}, Progress: {status_data.get('progress', 0)}%")
        
        if status_data["status"] in ["completed", "failed"]:
            break
            
        time.sleep(5)  # 5秒ごとにポーリング
    
    # 完了したら結果を取得
    if status_data["status"] == "completed":
        results = get_results(job_id)
        print(f"Generated {results['slide_count']} slides")
        
        # HTMLパッケージをダウンロード
        download_path = download_html_package(job_id, "slides.zip")
        print(f"Downloaded to {download_path}")
```

### JavaScriptクライアント例

```javascript
async function processImages(imageUrls, options = {}) {
  const response = await fetch('https://api.langgraph-slide-generator.example.com/v1/process', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      images: imageUrls,
      options: options
    })
  });
  
  const result = await response.json();
  return result.data;
}

async function checkJobStatus(jobId) {
  const response = await fetch(`https://api.langgraph-slide-generator.example.com/v1/jobs/${jobId}`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  });
  
  const result = await response.json();
  return result.data;
}

async function getResults(jobId, format = 'html') {
  const response = await fetch(`https://api.langgraph-slide-generator.example.com/v1/results/${jobId}?format=${format}`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  });
  
  const result = await response.json();
  return result.data;
}

// 使用例
async function generateSlides() {
  try {
    // 画像処理リクエスト
    const result = await processImages(
      ['https://example.com/textbook/page1.jpg'],
      {
        template: 'academic',
        slideBreakStrategy: 'heading'
      }
    );
    
    const jobId = result.job_id;
    console.log(`Job ID: ${jobId}`);
    
    // ステータス確認とポーリング
    let statusData;
    do {
      await new Promise(resolve => setTimeout(resolve, 5000));  // 5秒待機
      statusData = await checkJobStatus(jobId);
      console.log(`Status: ${statusData.status}, Progress: ${statusData.progress || 0}%`);
    } while (!['completed', 'failed'].includes(statusData.status));
    
    // 完了したら結果を取得
    if (statusData.status === 'completed') {
      const results = await getResults(jobId);
      console.log(`Generated ${results.slide_count} slides`);
      
      // iframeで表示
      document.getElementById('slides-preview').innerHTML = `
        <iframe srcdoc="${results.html.replace(/"/g, '&quot;')}" width="100%" height="600px"></iframe>
      `;
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```
