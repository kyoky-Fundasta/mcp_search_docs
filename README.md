
# Introduction

_このプラグラムはユーザー登録の**公式ドキュメント**から必要な内容を調べてユーザーの質問に答えます。
**MCP**プロトコルを遵守し**Claude**に登録可能なかたちでデザインされています。_

# Features

１．MCPツール
    ・**get_document**：公式ドキュメントから情報を調べて質問に答えます。

２．MCPプロンプト
    ・**search docs**：get_documentを活用するためのプロンプトテンプレート。
                直接Claudeチャットからget_documentを呼び出すより効率よくサーチが行えます。

３．MCPリソース
    ・**mcp/support/documentation/list**：検索可能なドキュメントのリストを確認できます。

# 新しいドキュメントを登録する方法

docs.listファイルを開き、docs_url辞書に追加したいドキュメントの名前（任意）とURLを書き入れてください。

# API消費量について
一度の質問に対してGoogle Custom Search JSON APIを１回（失敗やエラーのため再検索時、その都度追加消費）
Geminiを7回使用します。
1分間の間に連続2回まで（質問の回答を読む時間を考慮すると大体問題ないレベル）の規則を守れば一日最大100回まで無料で質問が出来ます。
Claude desktopを無料バージョンで使用している場合、そのトークン数の規制にかかる可能性があります。

## *API消費量について
利用には三つのキーが必要（無料の範囲内で使用可能）になります。
.env.exampleを参照し自分用の.envファイルを作成しAPIキーを書き入れてください。

    
    ・Google Custom Search JSON API：Search Engine IDとAPIの取得要
        Price：100search/dayまで無料
        Link：https://developers.google.com/custom-search/v1/introduction
    
    ・Gemini API キー：グーグルのGemini-2.0-flash
        Price：15RPM, 1500/dayまで無料
        Link：https://aistudio.google.com/apikey



# 設定手順

１. Python(>=3.11)とClaude Desktopを事前にインストールしてください。

２．レポジトリをクローンしてワークデレクとりに移動

３．バーチャル環境設定： uv venv

４．uv sync (uvをインストールしてない場合は先にインストールしてください: pip install uv)

５．APIキーセットアップ

６．ツールを登録：

Option 1 :次のコマンドをプログラムルーツフォルダで実行
mcp install main.py

Option 2 :Claude no configureファイルに直接書き込む(以下はWindowsの例)
```
"docs": {
    "command": "uv",
    "args": [
    "--directory",
    "C:\\Users\\--path-to-the-docs-directory",
    "run",
    "main.py"
    ]
}
```


// "args": [
      //   "run",
      //   "--with",
      //   "mcp[cli]",
      //   "mcp",
      //   "run",
      //   "C:\\Users\\kota-\\OneDrive\\デスクトップ\\FundastA_AI\\MCP\\mcp_search_docs\\main.py"
      // ]