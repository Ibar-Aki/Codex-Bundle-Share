# Codex Bundle Share

- 作成日: 2026-05-10 23:06 JST
- 作成者: Codex (GPT-5)

## 概要

Codex の `project-bundler` skill が生成した保管用 bundle ファイルを集約するためのリポジトリです。

既定の格納先は次の形式です。

```text
bundles/<project-slug>/bundle_*.txt
```

`project-slug` は GitHub remote の repo 名を優先し、取得できない場合は対象フォルダ名を使います。

## 運用メモ

- 原則として private repo で運用します。
- bundle にはソースコード、手順書、設定断片などが含まれる可能性があります。
- 不要になった古い bundle は、削除前に共有・復元用途が残っていないか確認します。
